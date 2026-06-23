"""
Flask API entry point for the Intelligent Job Portal backend.

Run locally:
    python app.py

The API uses SQLite by default for immediate verification. Set DATABASE_URL for
deployment, SECRET_KEY for production, and MAX_CONTENT_LENGTH_MB if upload size
limits need adjustment.
"""

from __future__ import annotations

import io
import os
from typing import Any, Dict, Tuple

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

from auto_apply import AutoApplyEngine
from matching_engine import MatchingEngine
from models import Database, DatabaseError
from parser import ResumeParser


ALLOWED_UPLOAD_EXTENSIONS = {"txt", "pdf"}


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Flask app with initialized parser, matching engine, database repository,
        and REST endpoints for resume upload, job posting, and match evaluation.
    """

    app = Flask(__name__)
    max_mb = int(os.getenv("MAX_CONTENT_LENGTH_MB", "5"))
    app.config["MAX_CONTENT_LENGTH"] = max_mb * 1024 * 1024
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")

    db = Database()
    parser = ResumeParser()
    matching_engine = MatchingEngine()
    auto_apply_engine = AutoApplyEngine(db=db, matching_engine=matching_engine)

    @app.errorhandler(ValueError)
    def handle_value_error(exc: ValueError):
        """Return consistent JSON for validation errors."""

        return jsonify({"error": str(exc)}), 400

    @app.errorhandler(DatabaseError)
    def handle_database_error(exc: DatabaseError):
        """Return consistent JSON for database transaction errors."""

        return jsonify({"error": str(exc)}), 500

    @app.errorhandler(413)
    def handle_file_too_large(_exc):
        """Return JSON when uploads exceed configured MAX_CONTENT_LENGTH."""

        return jsonify({"error": "Uploaded file is too large."}), 413

    @app.get("/")
    def index():
        """
        Return a compact API index for users opening the base URL in a browser.

        Returns:
            JSON service description with the available REST endpoints and
            expected HTTP methods.
        """

        return jsonify(
            {
                "service": "intelligent-job-portal-api",
                "status": "running",
                "endpoints": {
                    "health": {"method": "GET", "path": "/api/health"},
                    "upload_resume": {"method": "POST", "path": "/api/upload-resume"},
                    "create_job": {"method": "POST", "path": "/api/jobs"},
                    "match_evaluate": {"method": "POST", "path": "/api/match-evaluate"},
                },
            }
        )

    @app.get("/api/health")
    def health_check():
        """Report whether the service is alive for deployment probes."""

        return jsonify({"status": "ok", "service": "intelligent-job-portal-api"})

    @app.post("/api/upload-resume")
    def upload_resume():
        """
        Accept resume text or a .txt/.pdf upload, parse entities, and save user.

        Request:
            Multipart form-data:
                file: Optional resume file.
                email: Required user email.
                name: Optional user name.
                auto_apply_enabled: Optional boolean-like string.
            JSON:
                resume_text: Required if no file is provided.
                email: Required user email.
                name: Optional user name.
                auto_apply_enabled: Optional boolean.

        Returns:
            JSON containing user_id and extracted resume metrics.
        """

        payload = _request_payload()
        email = str(payload.get("email", "")).strip().lower()
        if not email:
            raise ValueError("email is required.")

        resume_text = _extract_resume_text(payload)
        parsed = parser.parse(resume_text)
        user = db.upsert_user_profile(
            email=email,
            name=str(payload.get("name") or "Anonymous User").strip() or "Anonymous User",
            resume_text=parsed.clean_text,
            skills=parsed.skills,
            experience_years=parsed.experience_years,
            industry_domain=parsed.industry_domain,
            auto_apply_enabled=_as_bool(payload.get("auto_apply_enabled", False)),
        )
        return jsonify(
            {
                "user_id": user.id,
                "user": user.to_dict(),
                "extracted_metrics": {
                    "skills": parsed.skills,
                    "experience_years": parsed.experience_years,
                    "industry_domain": parsed.industry_domain,
                    "token_count": len(parsed.tokens),
                },
            }
        ), 201

    @app.post("/api/jobs")
    def create_job():
        """
        Create a recruiter if needed and store a new job vacancy.

        Request JSON:
            recruiter_email: Required unique recruiter email.
            organization_name: Required recruiter organization.
            title: Required job title.
            description: Required job description.
            required_skills: Optional list of required skills.
            industry_domain: Optional domain label.

        Returns:
            JSON containing recruiter and created job objects.
        """

        payload = _request_payload()
        required = ["recruiter_email", "organization_name", "title", "description"]
        missing = [field for field in required if not str(payload.get(field, "")).strip()]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}.")

        required_skills = payload.get("required_skills", [])
        if isinstance(required_skills, str):
            required_skills = [skill.strip() for skill in required_skills.split(",") if skill.strip()]
        if not isinstance(required_skills, list):
            raise ValueError("required_skills must be a list or comma-separated string.")

        recruiter = db.create_recruiter(
            organization_name=str(payload["organization_name"]).strip(),
            email=str(payload["recruiter_email"]).strip().lower(),
        )
        job = db.create_job(
            recruiter_id=recruiter.id,
            title=str(payload["title"]).strip(),
            description=str(payload["description"]).strip(),
            required_skills=[str(skill).strip().lower() for skill in required_skills if str(skill).strip()],
            industry_domain=str(payload.get("industry_domain") or "general").strip() or "general",
        )
        return jsonify({"recruiter": recruiter.to_dict(), "job": job.to_dict()}), 201

    @app.post("/api/match-evaluate")
    def match_evaluate():
        """
        Evaluate a user/job pair and trigger auto-apply when eligible.

        Request JSON:
            user_id: Required integer user ID.
            job_id: Required integer job ID.

        Returns:
            JSON containing match percentage, decision, application status,
            XAI explanation, matched skills, and missing skills.
        """

        payload = _request_payload()
        user_id = _required_int(payload, "user_id")
        job_id = _required_int(payload, "job_id")
        result = auto_apply_engine.evaluate_and_apply(user_id=user_id, job_id=job_id)
        return jsonify(result), 200

    return app


def _request_payload() -> Dict[str, Any]:
    """
    Normalize JSON and form-data request values into a single dict.

    Returns:
        Dictionary containing request fields. File objects remain accessible via
        request.files and are not copied into the payload.
    """

    if request.is_json:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object.")
        return data
    return dict(request.form.items())


def _extract_resume_text(payload: Dict[str, Any]) -> str:
    """
    Extract resume text from JSON/form field or uploaded file.

    Parameters:
        payload: Normalized request payload.

    Returns:
        Resume text string ready for ResumeParser.

    Raises:
        ValueError: If no text/file is supplied or the file type is unsupported.
    """

    if "file" in request.files:
        uploaded = request.files["file"]
        filename = secure_filename(uploaded.filename or "")
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if extension not in ALLOWED_UPLOAD_EXTENSIONS:
            raise ValueError("Only .txt and .pdf resume uploads are supported.")
        file_bytes = uploaded.read()
        if not file_bytes:
            raise ValueError("Uploaded resume file is empty.")
        if extension == "pdf":
            return _extract_pdf_text(file_bytes)
        return file_bytes.decode("utf-8", errors="ignore")

    resume_text = str(payload.get("resume_text", "")).strip()
    if not resume_text:
        raise ValueError("resume_text or file upload is required.")
    return resume_text


def _extract_pdf_text(file_bytes: bytes) -> str:
    """
    Extract text from an uploaded PDF using pdfplumber when available.

    Parameters:
        file_bytes: Raw PDF bytes from Flask upload.

    Returns:
        Concatenated PDF page text.
    """

    try:
        import pdfplumber  # type: ignore
    except ImportError as exc:
        raise ValueError("PDF upload requires pdfplumber. Use resume_text or install pdfplumber.") from exc

    pages = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("No readable text could be extracted from the PDF.")
    return text


def _as_bool(value: Any) -> bool:
    """
    Convert common JSON/form boolean values to bool.

    Parameters:
        value: bool, number, or string-like value.

    Returns:
        True for true/1/yes/on/enabled, otherwise False.
    """

    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return str(value).strip().lower() in {"true", "1", "yes", "on", "enabled"}


def _required_int(payload: Dict[str, Any], field: str) -> int:
    """
    Read and validate a required integer field from request payload.

    Parameters:
        payload: Request payload dict.
        field: Required field name.

    Returns:
        Parsed integer value.
    """

    try:
        value = int(payload[field])
    except KeyError as exc:
        raise ValueError(f"{field} is required.") from exc
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer.") from exc
    if value <= 0:
        raise ValueError(f"{field} must be positive.")
    return value


app = create_app()


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    debug = _as_bool(os.getenv("FLASK_DEBUG", "false"))
    app.run(host=host, port=port, debug=debug)
