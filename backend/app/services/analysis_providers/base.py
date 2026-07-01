"""Shared types and helpers for email analysis providers."""

from typing import Protocol

from app.schemas.analysis import EmailAnalysisRequest, EmailAnalysisResponse

EMPTY_SUMMARY = "No useful preview available."


def get_analysis_content(email: EmailAnalysisRequest) -> str:
    """Return the best available text content for analysis (body preferred over snippet)."""
    body = (email.body or "").strip()
    if body:
        return body
    return email.snippet.strip()


class EmailAnalysisProvider(Protocol):
    """Interface for email analysis implementations (rule-based, LLM, etc.)."""

    def analyze(self, email: EmailAnalysisRequest) -> EmailAnalysisResponse:
        """Analyze a single email and return structured results."""
