"""Public email analysis service — delegates to a configurable provider."""

from app.schemas.analysis import AnalyzedEmail, EmailAnalysisRequest, EmailAnalysisResponse
from app.services.analysis_providers.base import EmailAnalysisProvider
from app.services.analysis_providers.rule_based import RuleBasedEmailAnalysisProvider

DEFAULT_ANALYSIS_PROVIDER: EmailAnalysisProvider = RuleBasedEmailAnalysisProvider()


def get_analysis_provider() -> EmailAnalysisProvider:
    """Return the active analysis provider. Swap DEFAULT_ANALYSIS_PROVIDER for LLM providers."""
    return DEFAULT_ANALYSIS_PROVIDER


def analyze_email(email: EmailAnalysisRequest) -> EmailAnalysisResponse:
    """Analyze a single email using the configured provider."""
    return DEFAULT_ANALYSIS_PROVIDER.analyze(email)


def analyze_emails_bulk(emails: list[EmailAnalysisRequest]) -> list[AnalyzedEmail]:
    """Analyze each email independently and preserve input order."""
    return [
        AnalyzedEmail(original_email=email, analysis=analyze_email(email))
        for email in emails
    ]
