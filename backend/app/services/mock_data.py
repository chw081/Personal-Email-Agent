from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.email import Email


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


MOCK_EMAILS: list[dict] = [
    {
        "gmail_message_id": "mock-gmail-001",
        "thread_id": "mock-thread-001",
        "sender": "Google Security",
        "sender_email": "no-reply@accounts.google.com",
        "subject": "Security alert: suspicious sign-in blocked",
        "snippet": "We blocked a sign-in attempt from an unrecognized device.",
        "body_text": "Review recent activity on your Google Account.",
        "received_at": _utcnow(),
        "is_unread": True,
        "has_attachment": False,
        "gmail_labels": ["INBOX", "UNREAD", "CATEGORY_UPDATES"],
    },
    {
        "gmail_message_id": "mock-gmail-002",
        "thread_id": "mock-thread-002",
        "sender": "LinkedIn Recruiting",
        "sender_email": "jobs-noreply@linkedin.com",
        "subject": "Senior Backend Engineer role — recruiter outreach",
        "snippet": "A recruiter would like to connect about a new opportunity.",
        "body_text": "Hi, I came across your profile and think you'd be a strong fit.",
        "received_at": _utcnow(),
        "is_unread": True,
        "has_attachment": False,
        "gmail_labels": ["INBOX", "UNREAD"],
    },
    {
        "gmail_message_id": "mock-gmail-003",
        "thread_id": "mock-thread-003",
        "sender": "Acme Corp Hiring",
        "sender_email": "talent@acmecorp.example",
        "subject": "Application received — Software Engineer",
        "snippet": "Thank you for applying. We have received your application.",
        "body_text": "Our team will review your materials and follow up soon.",
        "received_at": _utcnow(),
        "is_unread": False,
        "has_attachment": False,
        "gmail_labels": ["INBOX"],
    },
    {
        "gmail_message_id": "mock-gmail-004",
        "thread_id": "mock-thread-004",
        "sender": "Uber",
        "sender_email": "receipts@uber.example",
        "subject": "Your Uber receipt for Friday trip",
        "snippet": "Total: $24.50. Thanks for riding with Uber.",
        "body_text": "Trip receipt attached for your records.",
        "received_at": _utcnow(),
        "is_unread": False,
        "has_attachment": True,
        "gmail_labels": ["INBOX", "CATEGORY_UPDATES"],
    },
    {
        "gmail_message_id": "mock-gmail-005",
        "thread_id": "mock-thread-005",
        "sender": "Weee!",
        "sender_email": "orders@weee.example",
        "subject": "Weee order confirmation #A12847",
        "snippet": "Your grocery order is confirmed for delivery tomorrow.",
        "body_text": "Order summary and delivery window inside.",
        "received_at": _utcnow(),
        "is_unread": True,
        "has_attachment": False,
        "gmail_labels": ["INBOX", "UNREAD"],
    },
    {
        "gmail_message_id": "mock-gmail-006",
        "thread_id": "mock-thread-006",
        "sender": "MegaStore Deals",
        "sender_email": "promo@megastore.example",
        "subject": "Flash sale: 40% off this weekend only",
        "snippet": "Limited time offer on selected items. Shop now.",
        "body_text": "Use code SAVE40 at checkout.",
        "received_at": _utcnow(),
        "is_unread": True,
        "has_attachment": False,
        "gmail_labels": ["INBOX", "UNREAD", "CATEGORY_PROMOTIONS"],
    },
    {
        "gmail_message_id": "mock-gmail-007",
        "thread_id": "mock-thread-007",
        "sender": "OpenRouter",
        "sender_email": "billing@openrouter.example",
        "subject": "OpenRouter API usage summary",
        "snippet": "Your monthly API key usage report is ready.",
        "body_text": "Review token usage and billing details.",
        "received_at": _utcnow(),
        "is_unread": False,
        "has_attachment": False,
        "gmail_labels": ["INBOX"],
    },
    {
        "gmail_message_id": "mock-gmail-008",
        "thread_id": "mock-thread-008",
        "sender": "Alex Morgan",
        "sender_email": "alex.morgan@example.com",
        "subject": "Dinner this weekend?",
        "snippet": "Want to catch up and grab dinner on Saturday?",
        "body_text": "Let me know if you're free — would love to hear what you've been up to.",
        "received_at": _utcnow(),
        "is_unread": True,
        "has_attachment": False,
        "gmail_labels": ["INBOX", "UNREAD"],
    },
]


def seed_mock_emails(db: Session) -> list[Email]:
    created: list[Email] = []

    for payload in MOCK_EMAILS:
        existing = (
            db.query(Email)
            .filter(Email.gmail_message_id == payload["gmail_message_id"])
            .first()
        )
        if existing:
            continue

        email = Email(**payload)
        db.add(email)
        created.append(email)

    db.commit()
    for email in created:
        db.refresh(email)

    return created
