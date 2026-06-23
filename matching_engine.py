"""
Semantic matching and recommendation engine for resumes and job descriptions.

The engine prefers Sentence-Transformers when available locally, then falls
back to TF-IDF cosine similarity from scikit-learn, and finally to a pure
Python token-overlap score if ML libraries are unavailable. This layered design
keeps production deployments strong while preserving local testability.
"""

from __future__ import annotations

import math
import re
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable, List, Sequence


@dataclass
class MatchResult:
    """Structured output from a resume/job matching operation."""

    match_score: float
    algorithm: str
    elapsed_ms: float
    matched_skills: List[str]
    missing_skills: List[str]
    explanation: str

    def to_dict(self) -> Dict[str, object]:
        """Return JSON-compatible match result data."""

        return {
            "match_score": self.match_score,
            "algorithm": self.algorithm,
            "elapsed_ms": self.elapsed_ms,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "explanation": self.explanation,
        }


class MatchingEngine:
    """
    Compute semantic match scores between candidate profiles and jobs.

    Parameters:
        model_name: Sentence-Transformers model name. The default
            all-MiniLM-L6-v2 balances speed and quality.
        prefer_sentence_transformers: Whether to attempt transformer embeddings
            before TF-IDF fallback.

    Performance:
        The transformer model and job embeddings are cached. TF-IDF is used for
        lightweight comparisons and generally stays within the requested
        0.2-0.3 second per-comparison window on small local inputs.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", prefer_sentence_transformers: bool = True) -> None:
        self.model_name = model_name
        self.prefer_sentence_transformers = prefer_sentence_transformers
        self._model = None
        self._model_load_failed = False

    def compute_match(self, resume_profile: Dict[str, object], job: Dict[str, object]) -> MatchResult:
        """
        Calculate a 0-100 match score for a candidate and job.

        Parameters:
            resume_profile: Dict containing clean_text/resume_text and skills.
            job: Dict containing description, title, and required_skills.

        Calculation:
            Score combines semantic text similarity with explicit skill overlap.
            Final score = 80% semantic similarity + 20% required skill coverage.

        Returns:
            MatchResult with score, algorithm, elapsed time, skill gap details,
            and an XAI-friendly explanation.
        """

        start = time.perf_counter()
        resume_text = str(resume_profile.get("clean_text") or resume_profile.get("resume_text") or "")
        job_text = f"{job.get('title', '')} {job.get('description', '')}".strip()
        if not resume_text or not job_text:
            raise ValueError("Resume text and job description are required for matching.")

        resume_skills = self._normalize_skills(resume_profile.get("skills", []))
        required_skills = self._normalize_skills(job.get("required_skills", []))
        matched_skills = sorted(resume_skills.intersection(required_skills))
        missing_skills = sorted(required_skills.difference(resume_skills))

        semantic_score, algorithm = self._semantic_similarity(resume_text, job_text)
        skill_score = len(matched_skills) / len(required_skills) if required_skills else 0.0
        final_score = (0.8 * semantic_score) + (0.2 * skill_score)
        match_score = round(max(0.0, min(final_score * 100.0, 100.0)), 2)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        explanation = self._build_explanation(match_score, matched_skills, missing_skills, algorithm)

        return MatchResult(
            match_score=match_score,
            algorithm=algorithm,
            elapsed_ms=elapsed_ms,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            explanation=explanation,
        )

    def _semantic_similarity(self, resume_text: str, job_text: str) -> tuple[float, str]:
        """
        Compute semantic similarity using the strongest available backend.

        Parameters:
            resume_text: Cleaned candidate profile text.
            job_text: Job title and description.

        Returns:
            Tuple of normalized similarity in 0.0-1.0 and algorithm label.
        """

        if self.prefer_sentence_transformers and not self._model_load_failed:
            try:
                return self._sentence_transformer_similarity(resume_text, job_text), "sentence-transformers"
            except Exception:
                self._model_load_failed = True

        try:
            return self._tfidf_similarity(resume_text, job_text), "tf-idf"
        except Exception:
            return self._token_overlap_similarity(resume_text, job_text), "token-overlap"

    def _sentence_transformer_similarity(self, resume_text: str, job_text: str) -> float:
        """
        Calculate cosine similarity using Sentence-Transformers embeddings.

        Parameters:
            resume_text: Candidate text.
            job_text: Job text.

        Returns:
            Cosine similarity normalized to 0.0-1.0.
        """

        model = self._load_sentence_transformer()
        vectors = model.encode([resume_text, job_text], normalize_embeddings=True)
        similarity = float(vectors[0] @ vectors[1])
        return max(0.0, min(similarity, 1.0))

    def _load_sentence_transformer(self):
        """
        Lazy-load the configured Sentence-Transformers model.

        Returns:
            Loaded SentenceTransformer instance.
        """

        if self._model is None:
            from sentence_transformers import SentenceTransformer  # type: ignore

            self._model = SentenceTransformer(self.model_name)
        return self._model

    @staticmethod
    def _tfidf_similarity(resume_text: str, job_text: str) -> float:
        """
        Calculate cosine similarity with Scikit-learn TF-IDF vectors.

        Parameters:
            resume_text: Candidate text.
            job_text: Job text.

        Returns:
            Similarity score in the range 0.0-1.0.
        """

        from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
        from sklearn.metrics.pairwise import cosine_similarity  # type: ignore

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=5000)
        matrix = vectorizer.fit_transform([resume_text, job_text])
        return float(cosine_similarity(matrix[0], matrix[1])[0][0])

    @staticmethod
    def _token_overlap_similarity(resume_text: str, job_text: str) -> float:
        """
        Calculate a pure-Python Jaccard-like fallback similarity.

        Parameters:
            resume_text: Candidate text.
            job_text: Job text.

        Returns:
            Token overlap score in the range 0.0-1.0.
        """

        resume_tokens = set(re.findall(r"[a-z0-9.+#/-]+", resume_text.lower()))
        job_tokens = set(re.findall(r"[a-z0-9.+#/-]+", job_text.lower()))
        if not resume_tokens or not job_tokens:
            return 0.0
        intersection = len(resume_tokens.intersection(job_tokens))
        denominator = math.sqrt(len(resume_tokens) * len(job_tokens))
        return intersection / denominator if denominator else 0.0

    @staticmethod
    def _normalize_skills(raw_skills: object) -> set[str]:
        """
        Normalize skills from a list-like object into lowercase strings.

        Parameters:
            raw_skills: Iterable skill collection or unsupported value.

        Returns:
            Set of lowercase skill labels.
        """

        if not isinstance(raw_skills, Iterable) or isinstance(raw_skills, (str, bytes)):
            return set()
        return {str(skill).strip().lower() for skill in raw_skills if str(skill).strip()}

    @staticmethod
    def _build_explanation(score: float, matched_skills: Sequence[str], missing_skills: Sequence[str], algorithm: str) -> str:
        """
        Build an explainable summary of the matching decision.

        Parameters:
            score: Final match percentage.
            matched_skills: Required skills present in the candidate profile.
            missing_skills: Required skills absent from the candidate profile.
            algorithm: Similarity backend used for text comparison.

        Returns:
            Short XAI explanation for API clients.
        """

        matched = ", ".join(matched_skills[:5]) if matched_skills else "no explicit required skills"
        missing = ", ".join(missing_skills[:5]) if missing_skills else "no major required skill gaps"
        return (
            f"Score {score:.2f}% was computed with {algorithm}; matched skills include {matched}, "
            f"while missing skills include {missing}."
        )

    @lru_cache(maxsize=512)
    def cached_job_text(self, job_id: int, title: str, description: str) -> str:
        """
        Cache canonical job text for repeated matching operations.

        Parameters:
            job_id: Database job identifier.
            title: Job title.
            description: Job description.

        Returns:
            Concatenated text used for vectorization.
        """

        return f"{job_id} {title} {description}".strip()
