from dataclasses import dataclass

from app.models.email import Email


@dataclass(frozen=True)
class ClassificationResult:
    domain: str
    subcategory: str
    priority: str
    action: str
    confidence: float
    reason: str


_RULES: list[tuple[tuple[str, ...], ClassificationResult]] = [
    (
        ("security alert", "suspicious sign-in", "verify your account", "unusual activity"),
        ClassificationResult(
            domain="security",
            subcategory="account_security",
            priority="critical",
            action="review",
            confidence=0.95,
            reason="Security-related subject or sender indicates account alert.",
        ),
    ),
    (
        ("application received", "application confirmation", "thank you for applying"),
        ClassificationResult(
            domain="career",
            subcategory="job_application",
            priority="important",
            action="review",
            confidence=0.9,
            reason="Job application confirmation keywords detected.",
        ),
    ),
    (
        ("recruiter", "job opportunity", " hiring", "linkedin"),
        ClassificationResult(
            domain="career",
            subcategory="job_recruiting",
            priority="important",
            action="review",
            confidence=0.88,
            reason="Recruiting or job outreach keywords detected.",
        ),
    ),
    (
        ("receipt", "uber", "invoice", "payment confirmation"),
        ClassificationResult(
            domain="finance",
            subcategory="receipt",
            priority="normal",
            action="archive",
            confidence=0.85,
            reason="Receipt or payment-related keywords detected.",
        ),
    ),
    (
        ("weee", "order confirmation", "your order"),
        ClassificationResult(
            domain="shopping",
            subcategory="order_confirmation",
            priority="normal",
            action="keep",
            confidence=0.82,
            reason="Shopping order confirmation keywords detected.",
        ),
    ),
    (
        ("promotion", "discount", "sale", "% off", "limited time offer"),
        ClassificationResult(
            domain="low_value",
            subcategory="promotion",
            priority="low",
            action="delete_candidate",
            confidence=0.8,
            reason="Promotional or marketing keywords detected.",
        ),
    ),
    (
        ("openrouter", "api key", "course enrollment", "online course", "tutorial"),
        ClassificationResult(
            domain="learning",
            subcategory="ai_tools",
            priority="normal",
            action="keep",
            confidence=0.83,
            reason="Learning or developer-tool keywords detected.",
        ),
    ),
    (
        ("family", "dinner", "weekend plans", "catch up"),
        ClassificationResult(
            domain="personal",
            subcategory="personal_message",
            priority="normal",
            action="reply",
            confidence=0.75,
            reason="Personal conversation keywords detected.",
        ),
    ),
]

_DEFAULT = ClassificationResult(
    domain="unknown",
    subcategory="general",
    priority="normal",
    action="keep",
    confidence=0.5,
    reason="No strong keyword match; default classification applied.",
)


def classify_email(email: Email) -> ClassificationResult:
    """Return a deterministic mock classification based on subject and sender."""
    haystack = " ".join(
        part for part in (email.subject, email.sender, email.sender_email, email.snippet) if part
    ).lower()

    for keywords, result in _RULES:
        if any(keyword in haystack for keyword in keywords):
            return result

    return _DEFAULT
