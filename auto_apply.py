"""
Auto-apply decision engine for intelligent job recommendations.

The engine coordinates database access and semantic matching, then persists an
application row only when the candidate explicitly enabled automation and meets
the configured threshold.
"""

from __future__ import annotations

from typing import Dict

from matching_engine import MatchingEngine
from models import Database, DatabaseError


class AutoApplyEngine:
    """
    Evaluate whether a user should be automatically applied to a job.

    Parameters:
        db: Repository object used to load users/jobs and save applications.
        matching_engine: Optional preconfigured MatchingEngine.
        threshold: Minimum match percentage required for auto-apply.
    """

    def __init__(self, db: Database, matching_engine: MatchingEngine | None = None, threshold: float = 70.0) -> None:
        self.db = db
        self.matching_engine = matching_engine or MatchingEngine()
        self.threshold = threshold

    def evaluate_and_apply(self, user_id: int, job_id: int) -> Dict[str, object]:
        """
        Compute match score and conditionally create/update application status.

        Parameters:
            user_id: Candidate profile ID.
            job_id: Job vacancy ID.

        Decision logic:
            1. Load user and job from the database.
            2. Verify user.auto_apply_enabled.
            3. Compute semantic match score through MatchingEngine.
            4. If score >= threshold and automation is enabled, persist an
               application with "Under Review" status.

        Returns:
            JSON-compatible dict containing match_score, application_status,
            decision, xai_reason, and matched/missing skill details.

        Raises:
            ValueError: If user_id/job_id does not exist.
            DatabaseError: If application persistence fails.
        """

        user = self.db.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} was not found.")
        job = self.db.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} was not found.")

        match_result = self.matching_engine.compute_match(user.to_dict(), job.to_dict())
        eligible = match_result.match_score >= self.threshold and user.auto_apply_enabled

        if eligible:
            status = "Under Review"
            decision = "auto_applied"
            xai_reason = (
                f"Auto-apply approved because the score {match_result.match_score:.2f}% "
                f"meets the {self.threshold:.0f}% threshold and auto-apply is enabled. "
                f"{match_result.explanation}"
            )
            application = self.db.upsert_application(
                user_id=user_id,
                job_id=job_id,
                match_score=match_result.match_score,
                status=status,
                xai_reason=xai_reason,
            )
            application_id = application.id
        else:
            status = "Not Applied"
            decision = "not_applied"
            if not user.auto_apply_enabled:
                reason = "auto-apply is disabled for this user"
            else:
                reason = f"the score is below the {self.threshold:.0f}% threshold"
            xai_reason = f"Auto-apply was not executed because {reason}. {match_result.explanation}"
            application_id = None

        return {
            "user_id": user_id,
            "job_id": job_id,
            "match_score": match_result.match_score,
            "application_status": status,
            "decision": decision,
            "application_id": application_id,
            "xai_reason": xai_reason,
            "matched_skills": match_result.matched_skills,
            "missing_skills": match_result.missing_skills,
            "algorithm": match_result.algorithm,
            "elapsed_ms": match_result.elapsed_ms,
        }
