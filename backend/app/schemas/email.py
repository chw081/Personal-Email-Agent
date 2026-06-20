from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EmailCreate(BaseModel):
    gmail_message_id: str | None = None
    thread_id: str | None = None
    sender: str
    sender_email: str | None = None
    subject: str
    snippet: str | None = None
    body_text: str | None = None
    received_at: datetime | None = None
    is_unread: bool = True
    has_attachment: bool = False
    gmail_labels: list[str] | None = None


class EmailRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    gmail_message_id: str | None
    thread_id: str | None
    sender: str
    sender_email: str | None
    subject: str
    snippet: str | None
    body_text: str | None
    received_at: datetime | None
    is_unread: bool
    has_attachment: bool
    gmail_labels: list[str] | None
    created_at: datetime
    updated_at: datetime
