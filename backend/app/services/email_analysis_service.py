"""Public email analysis service — delegates to a configurable provider."""

from __future__ import annotations

import logging

from app.config import get_settings
from app.schemas.analysis import AnalyzedEmail, EmailAnalysisRequest, EmailAnalysisResponse
from app.services.analysis_providers.base import EmailAnalysisProvider
from app.services.analysis_providers.llm import LLMEmailAnalysisProvider
from app.services.analysis_providers.rule_based import RuleBasedEmailAnalysisProvider

logger = logging.getLogger(__name__)

_FALLBACK_PROVIDER = RuleBasedEmailAnalysisProvider()
_primary_provider: EmailAnalysisProvider | None = None


def _build_primary_provider() -> EmailAnalysisProvider:
    provider_name = get_settings().analysis_provider.strip().lower()
    if provider_name == "llm":
        try:
            return LLMEmailAnalysisProvider()
        except RuntimeError as exc:
            logger.warning("LLM provider unavailable, using rule-based: %s", exc)
            return RuleBasedEmailAnalysisProvider()
    return RuleBasedEmailAnalysisProvider()


def get_analysis_provider() -> EmailAnalysisProvider:
    """Return the active analysis provider configured via ANALYSIS_PROVIDER."""
    global _primary_provider
    if _primary_provider is None:
        _primary_provider = _build_primary_provider()
    return _primary_provider


def reset_analysis_provider_cache() -> None:
    """Clear cached provider selection (for tests)."""
    global _primary_provider
    _primary_provider = None


def _analyze_with_fallback(
    email: EmailAnalysisRequest,
    provider: EmailAnalysisProvider,
) -> EmailAnalysisResponse:
    if isinstance(provider, RuleBasedEmailAnalysisProvider):
        return provider.analyze(email)

    try:
        return provider.analyze(email)
    except Exception as exc:
        logger.warning(
            "LLM analysis failed for subject=%r, falling back to rule-based: %s",
            email.subject,
            exc,
        )
        return _FALLBACK_PROVIDER.analyze(email)


def analyze_email(email: EmailAnalysisRequest) -> EmailAnalysisResponse:
    """Analyze a single email using the configured provider."""
    return _analyze_with_fallback(email, get_analysis_provider())


def analyze_emails_bulk(emails: list[EmailAnalysisRequest]) -> list[AnalyzedEmail]:
    """Analyze each email independently and preserve input order."""
    provider = get_analysis_provider()
    return [
        AnalyzedEmail(
            original_email=email,
            analysis=_analyze_with_fallback(email, provider),
        )
        for email in emails
    ]
