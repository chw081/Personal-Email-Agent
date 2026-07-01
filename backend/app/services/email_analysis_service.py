"""Public email analysis service — delegates to a configurable provider."""

from app.schemas.analysis import AnalyzedEmail, EmailAnalysisRequest, EmailAnalysisResponse
from app.services.analysis_providers.base import EmailAnalysisProvider
from app.services.analysis_providers.rule_based import RuleBasedEmailAnalysisProvider

_default_provider: EmailAnalysisProvider = RuleBasedEmailAnalysisProvider()


def get_analysis_provider() -> EmailAnalysisProvider:
    """Return the active analysis provider. Swap implementation here for LLM providers."""
    return _default_provider


def analyze_email(email: EmailAnalysisRequest) -> EmailAnalysisResponse:
    """Analyze a single email using the configured provider."""
    return get_analysis_provider().analyze(email)


def analyze_emails_bulk(emails: list[EmailAnalysisRequest]) -> list[AnalyzedEmail]:
    """Analyze each email independently and preserve input order."""
    provider = get_analysis_provider()
    return [
        AnalyzedEmail(original_email=email, analysis=provider.analyze(email))
        for email in emails
    ]
