"""Rule-based keyword email analysis provider."""

from app.schemas.analysis import EmailAnalysisRequest, EmailAnalysisResponse
from app.services.analysis_providers.base import EMPTY_SUMMARY, get_analysis_content

HIGH_PRIORITY_KEYWORDS = ("urgent", "asap", "deadline", "interview", "action required")
MEDIUM_PRIORITY_KEYWORDS = ("meeting", "schedule", "follow up", "invoice")

CAREER_KEYWORDS = ("interview", "recruiter", "application", "job")
FINANCE_KEYWORDS = ("invoice", "payment", "bank", "credit", "statement")
PROMOTION_KEYWORDS = ("sale", "discount", "offer", "promotion")

SUMMARY_MAX_LENGTH = 180


def _combined_text(email: EmailAnalysisRequest) -> str:
    return " ".join((email.subject, email.sender, get_analysis_content(email))).lower()


def _determine_priority(text: str) -> str:
    if any(keyword in text for keyword in HIGH_PRIORITY_KEYWORDS):
        return "High"
    if any(keyword in text for keyword in MEDIUM_PRIORITY_KEYWORDS):
        return "Medium"
    return "Low"


def _determine_category(text: str) -> str:
    if any(keyword in text for keyword in CAREER_KEYWORDS):
        return "Career"
    if any(keyword in text for keyword in FINANCE_KEYWORDS):
        return "Finance"
    if any(keyword in text for keyword in PROMOTION_KEYWORDS):
        return "Promotion"
    return "Other"


def _build_summary(content: str) -> str:
    cleaned = content.strip()
    if not cleaned:
        return EMPTY_SUMMARY
    if len(cleaned) <= SUMMARY_MAX_LENGTH:
        return cleaned
    return cleaned[:SUMMARY_MAX_LENGTH]


def _build_action_items(category: str) -> list[str]:
    if category == "Career":
        return ["Review and respond if relevant."]
    if category == "Finance":
        return ["Check financial details."]
    return ["No immediate action needed."]


class RuleBasedEmailAnalysisProvider:
    """Deterministic keyword-based email analysis (default MVP implementation)."""

    def analyze(self, email: EmailAnalysisRequest) -> EmailAnalysisResponse:
        text = _combined_text(email)
        category = _determine_category(text)

        return EmailAnalysisResponse(
            summary=_build_summary(get_analysis_content(email)),
            priority=_determine_priority(text),
            category=category,
            action_items=_build_action_items(category),
        )
