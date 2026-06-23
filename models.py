"""
Database models and persistence layer for the Intelligent Job Portal backend.

The module exposes small dataclasses for the core domain entities and a
Database class that uses SQLite out of the box. If DATABASE_URL points to a
PostgreSQL connection string and psycopg is installed, the same repository API
can be adapted to PostgreSQL-backed deployments.
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Iterator, List, Optional


def utc_now() -> str:
    """Return the current UTC timestamp as an ISO-8601 string."""

    return datetime.now(timezone.utc).isoformat()


def _json_dumps(value: Any) -> str:
    """Serialize JSON data using stable settings for database storage."""

    return json.dumps(value or [], ensure_ascii=False, sort_keys=True)


def _json_loads(value: Optional[str], default: Any = None) -> Any:
    """Deserialize database JSON safely, returning default on empty values."""

    if not value:
        return [] if default is None else default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return [] if default is None else default


@dataclass
class User:
    """Application user profile persisted by the backend."""

    id: int
    name: str
    email: str
    resume_text: str
    skills: List[str]
    experience_years: int
    industry_domain: str
    auto_apply_enabled: bool
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the user."""

        data = asdict(self)
        data["auto_apply_enabled"] = bool(self.auto_apply_enabled)
        return data


@dataclass
class Recruiter:
    """Recruiter or organization account that can post job vacancies."""

    id: int
    organization_name: str
    email: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the recruiter."""

        return asdict(self)


@dataclass
class Job:
    """Job vacancy with textual requirements and normalized skill metadata."""

    id: int
    recruiter_id: int
    title: str
    description: str
    required_skills: List[str]
    industry_domain: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the job."""

        return asdict(self)


@dataclass
class Application:
    """Tracked job application created manually or by the auto-apply engine."""

    id: int
    user_id: int
    job_id: int
    match_score: float
    status: str
    xai_reason: str
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the application."""

        return asdict(self)


class DatabaseError(RuntimeError):
    """Raised when a persistence operation fails."""


class Database:
    """
    Small repository layer for user, recruiter, job, and application records.

    Parameters:
        database_url: Optional database URL. Defaults to DATABASE_URL or a local
            SQLite file named job_portal.db.

    Return format:
        Repository methods return dataclass instances or None when records are
        not found. Write methods commit transactions atomically.
    """

    def __init__(self, database_url: Optional[str] = None) -> None:
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///job_portal.db")
        self.backend = "postgres" if self.database_url.startswith(("postgres://", "postgresql://")) else "sqlite"
        self._postgres_module = None
        self._memory_conn = None
        if self.backend == "postgres":
            try:
                import psycopg  # type: ignore

                self._postgres_module = psycopg
            except ImportError as exc:
                raise DatabaseError("PostgreSQL requires psycopg. Install psycopg or use SQLite fallback.") from exc
        self.init_db()

    @contextmanager
    def connect(self) -> Iterator[Any]:
        """
        Yield a database connection and close it after use.

        The SQLite fallback stores JSON arrays as TEXT. PostgreSQL deployments
        can replace this layer with SQLAlchemy without touching business logic.
        """

        if self.backend == "postgres":
            conn = self._postgres_module.connect(self.database_url)
        else:
            db_path = self.database_url.replace("sqlite:///", "", 1)
            if db_path == ":memory:":
                if self._memory_conn is None:
                    self._memory_conn = sqlite3.connect(db_path)
                    self._memory_conn.row_factory = sqlite3.Row
                    self._memory_conn.execute("PRAGMA foreign_keys = ON")
                conn = self._memory_conn
            else:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            if self.backend != "sqlite" or self.database_url.replace("sqlite:///", "", 1) != ":memory:":
                conn.close()

    def init_db(self) -> None:
        """
        Create required tables when they do not exist.

        This method is idempotent and is called during Database initialization,
        allowing the API to run immediately in local verification environments.
        """

        statements = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL DEFAULT 'Anonymous User',
                email TEXT NOT NULL UNIQUE,
                resume_text TEXT NOT NULL DEFAULT '',
                skills TEXT NOT NULL DEFAULT '[]',
                experience_years INTEGER NOT NULL DEFAULT 0,
                industry_domain TEXT NOT NULL DEFAULT 'general',
                auto_apply_enabled INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS recruiters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recruiter_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                required_skills TEXT NOT NULL DEFAULT '[]',
                industry_domain TEXT NOT NULL DEFAULT 'general',
                created_at TEXT NOT NULL,
                FOREIGN KEY (recruiter_id) REFERENCES recruiters(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                match_score REAL NOT NULL,
                status TEXT NOT NULL,
                xai_reason TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(user_id, job_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
            """,
        ]
        with self.connect() as conn:
            for statement in statements:
                conn.execute(statement)
            conn.commit()

    def upsert_user_profile(
        self,
        *,
        email: str,
        name: str = "Anonymous User",
        resume_text: str = "",
        skills: Optional[List[str]] = None,
        experience_years: int = 0,
        industry_domain: str = "general",
        auto_apply_enabled: bool = False,
    ) -> User:
        """
        Create or update a user profile from parsed resume data.

        Parameters:
            email: Stable unique identifier for the user.
            name: Display name used by the portal.
            resume_text: Raw extracted resume text.
            skills: Normalized skill list produced by ResumeParser.
            experience_years: Estimated total years of experience.
            industry_domain: Dominant inferred industry/domain.
            auto_apply_enabled: Whether automatic application is allowed.

        Returns:
            The newly persisted or updated User instance.
        """

        now = utc_now()
        payload = (
            name,
            resume_text,
            _json_dumps(skills),
            int(experience_years or 0),
            industry_domain or "general",
            1 if auto_apply_enabled else 0,
            now,
            email,
        )
        with self.connect() as conn:
            try:
                existing = self.get_user_by_email(email, conn=conn)
                if existing:
                    conn.execute(
                        """
                        UPDATE users
                           SET name = ?, resume_text = ?, skills = ?, experience_years = ?,
                               industry_domain = ?, auto_apply_enabled = ?, updated_at = ?
                         WHERE email = ?
                        """,
                        payload,
                    )
                    user_id = existing.id
                else:
                    conn.execute(
                        """
                        INSERT INTO users
                            (name, resume_text, skills, experience_years, industry_domain,
                             auto_apply_enabled, updated_at, email, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        payload[:-1] + (email, now),
                    )
                    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                conn.commit()
            except Exception as exc:  # noqa: BLE001 - wrap DB-specific failures.
                conn.rollback()
                raise DatabaseError(f"Unable to save user profile: {exc}") from exc
        user = self.get_user(user_id)
        if not user:
            raise DatabaseError("User profile was saved but could not be reloaded.")
        return user

    def get_user_by_email(self, email: str, conn: Optional[Any] = None) -> Optional[User]:
        """Return a user by email or None when the profile does not exist."""

        own_conn = conn is None
        if own_conn:
            context = self.connect()
            conn = context.__enter__()
        try:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            return self._row_to_user(row) if row else None
        finally:
            if own_conn:
                context.__exit__(None, None, None)

    def get_user(self, user_id: int) -> Optional[User]:
        """Return a user by numeric ID or None when no matching row exists."""

        with self.connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._row_to_user(row) if row else None

    def create_recruiter(self, organization_name: str, email: str) -> Recruiter:
        """
        Create a recruiter account or return the existing account for email.

        Parameters:
            organization_name: Recruiter organization/company name.
            email: Unique recruiter contact email.

        Returns:
            Recruiter instance persisted in the database.
        """

        now = utc_now()
        with self.connect() as conn:
            try:
                row = conn.execute("SELECT * FROM recruiters WHERE email = ?", (email,)).fetchone()
                if row:
                    return self._row_to_recruiter(row)
                conn.execute(
                    "INSERT INTO recruiters (organization_name, email, created_at) VALUES (?, ?, ?)",
                    (organization_name, email, now),
                )
                recruiter_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                conn.commit()
            except Exception as exc:  # noqa: BLE001
                conn.rollback()
                raise DatabaseError(f"Unable to create recruiter: {exc}") from exc
        recruiter = self.get_recruiter(recruiter_id)
        if not recruiter:
            raise DatabaseError("Recruiter was saved but could not be reloaded.")
        return recruiter

    def get_recruiter(self, recruiter_id: int) -> Optional[Recruiter]:
        """Return a recruiter by ID or None when no matching row exists."""

        with self.connect() as conn:
            row = conn.execute("SELECT * FROM recruiters WHERE id = ?", (recruiter_id,)).fetchone()
        return self._row_to_recruiter(row) if row else None

    def create_job(
        self,
        *,
        recruiter_id: int,
        title: str,
        description: str,
        required_skills: Iterable[str],
        industry_domain: str = "general",
    ) -> Job:
        """
        Persist a job vacancy posted by a recruiter.

        Parameters:
            recruiter_id: ID of an existing recruiter.
            title: Human-readable job title.
            description: Full job description used for semantic matching.
            required_skills: Skill labels normalized by the API or recruiter.
            industry_domain: Optional domain tag for analytics/filtering.

        Returns:
            The created Job instance.
        """

        if not self.get_recruiter(recruiter_id):
            raise DatabaseError(f"Recruiter {recruiter_id} does not exist.")
        now = utc_now()
        with self.connect() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO jobs
                        (recruiter_id, title, description, required_skills, industry_domain, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (recruiter_id, title, description, _json_dumps(list(required_skills)), industry_domain, now),
                )
                job_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                conn.commit()
            except Exception as exc:  # noqa: BLE001
                conn.rollback()
                raise DatabaseError(f"Unable to create job: {exc}") from exc
        job = self.get_job(job_id)
        if not job:
            raise DatabaseError("Job was saved but could not be reloaded.")
        return job

    def get_job(self, job_id: int) -> Optional[Job]:
        """Return a job by ID or None when no matching vacancy exists."""

        with self.connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._row_to_job(row) if row else None

    def upsert_application(self, *, user_id: int, job_id: int, match_score: float, status: str, xai_reason: str) -> Application:
        """
        Create or update an application tracker row.

        Parameters:
            user_id: Candidate user ID.
            job_id: Vacancy ID.
            match_score: Similarity score in the range 0.0 to 100.0.
            status: Workflow state such as Applied, Under Review, or Not Applied.
            xai_reason: Short explainability message shown to the user/recruiter.

        Returns:
            Application instance after persistence.
        """

        now = utc_now()
        with self.connect() as conn:
            try:
                existing = conn.execute(
                    "SELECT id FROM applications WHERE user_id = ? AND job_id = ?",
                    (user_id, job_id),
                ).fetchone()
                if existing:
                    application_id = existing["id"]
                    conn.execute(
                        """
                        UPDATE applications
                           SET match_score = ?, status = ?, xai_reason = ?, updated_at = ?
                         WHERE id = ?
                        """,
                        (float(match_score), status, xai_reason, now, application_id),
                    )
                else:
                    conn.execute(
                        """
                        INSERT INTO applications
                            (user_id, job_id, match_score, status, xai_reason, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (user_id, job_id, float(match_score), status, xai_reason, now, now),
                    )
                    application_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                conn.commit()
            except Exception as exc:  # noqa: BLE001
                conn.rollback()
                raise DatabaseError(f"Unable to save application: {exc}") from exc
        application = self.get_application(application_id)
        if not application:
            raise DatabaseError("Application was saved but could not be reloaded.")
        return application

    def get_application(self, application_id: int) -> Optional[Application]:
        """Return an application by ID or None when no matching row exists."""

        with self.connect() as conn:
            row = conn.execute("SELECT * FROM applications WHERE id = ?", (application_id,)).fetchone()
        return self._row_to_application(row) if row else None

    @staticmethod
    def _row_to_user(row: Any) -> User:
        """Convert a database row into a User dataclass."""

        return User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            resume_text=row["resume_text"],
            skills=_json_loads(row["skills"]),
            experience_years=row["experience_years"],
            industry_domain=row["industry_domain"],
            auto_apply_enabled=bool(row["auto_apply_enabled"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _row_to_recruiter(row: Any) -> Recruiter:
        """Convert a database row into a Recruiter dataclass."""

        return Recruiter(id=row["id"], organization_name=row["organization_name"], email=row["email"], created_at=row["created_at"])

    @staticmethod
    def _row_to_job(row: Any) -> Job:
        """Convert a database row into a Job dataclass."""

        return Job(
            id=row["id"],
            recruiter_id=row["recruiter_id"],
            title=row["title"],
            description=row["description"],
            required_skills=_json_loads(row["required_skills"]),
            industry_domain=row["industry_domain"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _row_to_application(row: Any) -> Application:
        """Convert a database row into an Application dataclass."""

        return Application(
            id=row["id"],
            user_id=row["user_id"],
            job_id=row["job_id"],
            match_score=round(float(row["match_score"]), 2),
            status=row["status"],
            xai_reason=row["xai_reason"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
