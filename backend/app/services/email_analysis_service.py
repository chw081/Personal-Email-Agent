"""Rule-based email analysis service."""

from app.schemas.analysis import AnalyzedEmail, EmailAnalysisRequest, EmailAnalysisResponse

HIGH_PRIORITY_KEYWORDS = ("urgent", "asap", "deadline", "interview", "action required")
MEDIUM_PRIORITY_KEYWORDS = ("meeting", "schedule", "follow up", "invoice")

CAREER_KEYWORDS = ("interview", "recruiter", "application", "job")
FINANCE_KEYWORDS = ("invoice", "payment", "bank", "credit", "statement")
PROMOTION_KEYWORDS = ("sale", "discount", "offer", "promotion")

SUMMARY_MAX_LENGTH = 180
EMPTY_SUMMARY = "No useful preview available."


def _analysis_content(email: EmailAnalysisRequest) -> str:
    """Prefer extracted body text over Gmail snippet for classification."""
    body = (email.body or "").strip()
    if body:
        return body
    return email.snippet.strip()


def _combined_text(email: EmailAnalysisRequest) -> str:
    return " ".join((email.subject, email.sender, _analysis_content(email))).lower()


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


def _build_summary(snippet: str) -> str:
    cleaned = snippet.strip()
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


def analyze_email(email: EmailAnalysisRequest) -> EmailAnalysisResponse:
    """Classify an email using deterministic keyword rules."""
    text = _combined_text(email)
    category = _determine_category(text)

    return EmailAnalysisResponse(
        summary=_build_summary(_analysis_content(email)),
        priority=_determine_priority(text),
        category=category,
        action_items=_build_action_items(category),
    )


def analyze_emails_bulk(emails: list[EmailAnalysisRequest]) -> list[AnalyzedEmail]:
    """Analyze each email independently and preserve input order."""
    return [
        AnalyzedEmail(original_email=email, analysis=analyze_email(email))
        for email in emails
    ]
