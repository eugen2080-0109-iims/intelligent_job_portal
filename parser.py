"""
Resume parsing and lightweight information extraction pipeline.

ResumeParser combines deterministic text cleaning with optional NLTK-powered
tokenization and lemmatization. Entity extraction is intentionally transparent:
it uses a curated skill lexicon, experience regexes, and domain keyword scoring
so the module can run offline during local development and be replaced later by
a trained NER model.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Sequence


@dataclass
class ParsedResume:
    """Structured resume profile emitted by ResumeParser."""

    clean_text: str
    tokens: List[str]
    skills: List[str]
    experience_years: int
    industry_domain: str

    def to_dict(self) -> Dict[str, object]:
        """Return parsed resume output as JSON-compatible data."""

        return asdict(self)


class ResumeParser:
    """
    Parse raw resume text into normalized entities for matching.

    Parameters:
        skill_lexicon: Optional custom skills to detect in resume text.

    The parser avoids hard dependency on NLTK corpus downloads. If tokenizers or
    WordNet data are unavailable, it falls back to regex tokenization and simple
    lowercasing so the API remains operational.
    """

    DEFAULT_SKILLS = {
        "python",
        "flask",
        "django",
        "fastapi",
        "javascript",
        "typescript",
        "react",
        "node",
        "sql",
        "postgresql",
        "mysql",
        "sqlite",
        "mongodb",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "machine learning",
        "deep learning",
        "nlp",
        "natural language processing",
        "scikit-learn",
        "tensorflow",
        "pytorch",
        "bert",
        "sentence transformers",
        "pandas",
        "numpy",
        "data analysis",
        "rest api",
        "microservices",
        "git",
        "ci/cd",
        "html",
        "css",
    }

    DOMAIN_KEYWORDS = {
        "software_engineering": ["backend", "frontend", "api", "microservices", "software", "developer", "engineer"],
        "data_science": ["machine learning", "analytics", "model", "prediction", "data", "nlp", "classification"],
        "devops": ["docker", "kubernetes", "deployment", "cloud", "aws", "azure", "ci/cd"],
        "business": ["sales", "marketing", "operations", "management", "stakeholder", "crm"],
        "general": [],
    }

    def __init__(self, skill_lexicon: Sequence[str] | None = None) -> None:
        self.skill_lexicon = sorted(set(skill_lexicon or self.DEFAULT_SKILLS), key=len, reverse=True)
        self._lemmatizer = None
        try:
            from nltk.stem import WordNetLemmatizer  # type: ignore

            self._lemmatizer = WordNetLemmatizer()
        except Exception:
            self._lemmatizer = None

    def parse(self, raw_text: str) -> ParsedResume:
        """
        Execute the full information extraction pipeline.

        Parameters:
            raw_text: Resume text extracted from a file upload or JSON body.

        Calculation:
            1. Normalize whitespace and punctuation.
            2. Tokenize and lemmatize text.
            3. Extract skills, experience years, and industry domain.

        Returns:
            ParsedResume containing clean_text, tokens, skills,
            experience_years, and industry_domain.

        Raises:
            ValueError: If raw_text is empty or not a string.
        """

        if not isinstance(raw_text, str) or not raw_text.strip():
            raise ValueError("Resume text cannot be empty.")

        clean_text = self.clean_text(raw_text)
        tokens = self.preprocess(clean_text)
        entities = self.extract_entities(clean_text, tokens)
        return ParsedResume(
            clean_text=clean_text,
            tokens=tokens,
            skills=entities["skills"],
            experience_years=entities["experience_years"],
            industry_domain=entities["industry_domain"],
        )

    def clean_text(self, text: str) -> str:
        """
        Normalize resume text while preserving skill phrases.

        Parameters:
            text: Raw resume text.

        Returns:
            Lowercased text with normalized symbols and collapsed whitespace.
        """

        normalized = text.replace("\x00", " ")
        normalized = re.sub(r"[^\w\s.+#/-]", " ", normalized.lower())
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def preprocess(self, clean_text: str) -> List[str]:
        """
        Tokenize and lemmatize cleaned text.

        Parameters:
            clean_text: Output from clean_text().

        Returns:
            List of normalized tokens useful for downstream feature matching.
        """

        try:
            from nltk.tokenize import word_tokenize  # type: ignore

            tokens = word_tokenize(clean_text)
        except Exception:
            tokens = re.findall(r"[a-z0-9.+#/-]+", clean_text)

        lemmatized: List[str] = []
        for token in tokens:
            if len(token) <= 1:
                continue
            if self._lemmatizer:
                try:
                    token = self._lemmatizer.lemmatize(token)
                except Exception:
                    pass
            lemmatized.append(token)
        return lemmatized

    def extract_entities(self, clean_text: str, tokens: Sequence[str]) -> Dict[str, object]:
        """
        Extract mocked IE/NER entities from cleaned resume text.

        Parameters:
            clean_text: Normalized resume text.
            tokens: Token sequence generated by preprocess().

        Logic:
            Skills are matched from a curated lexicon, experience is inferred
            from phrases such as "3 years", and domain is selected by keyword
            score. This mirrors an IE pipeline while remaining deterministic.

        Returns:
            Dict with skills, experience_years, and industry_domain.
        """

        skills = self.extract_skills(clean_text)
        experience_years = self.extract_experience_years(clean_text)
        industry_domain = self.infer_industry_domain(clean_text, tokens, skills)
        return {
            "skills": skills,
            "experience_years": experience_years,
            "industry_domain": industry_domain,
        }

    def extract_skills(self, clean_text: str) -> List[str]:
        """
        Detect known skills by phrase-boundary matching.

        Parameters:
            clean_text: Normalized resume text.

        Returns:
            Alphabetically sorted list of unique skill labels.
        """

        found = set()
        for skill in self.skill_lexicon:
            pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
            if re.search(pattern, clean_text):
                found.add(skill)
        return sorted(found)

    def extract_experience_years(self, clean_text: str) -> int:
        """
        Estimate total years of professional experience.

        Parameters:
            clean_text: Normalized resume text.

        Returns:
            Maximum year count found near "year(s)" phrases, capped at 50.
        """

        matches = re.findall(r"(\d{1,2})\s*\+?\s*(?:years?|yrs?)", clean_text)
        if not matches:
            return 0
        return min(max(int(value) for value in matches), 50)

    def infer_industry_domain(self, clean_text: str, tokens: Sequence[str], skills: Sequence[str]) -> str:
        """
        Infer the most likely industry domain using keyword scoring.

        Parameters:
            clean_text: Normalized resume text.
            tokens: Tokenized text for single-word domain checks.
            skills: Extracted skills that can boost related domains.

        Returns:
            Domain key such as software_engineering, data_science, or devops.
        """

        token_set = set(tokens)
        skill_text = " ".join(skills)
        scores = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if " " in keyword:
                    score += 2 if keyword in clean_text or keyword in skill_text else 0
                else:
                    score += 1 if keyword in token_set or keyword in skill_text else 0
            scores[domain] = score
        best_domain = max(scores, key=scores.get)
        return best_domain if scores[best_domain] > 0 else "general"
