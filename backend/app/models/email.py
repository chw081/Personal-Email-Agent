import uuid
from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.analysis import EmailAnalysis


class Email(Base):
    __tablename__ = "emails"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gmail_message_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    thread_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    sender_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_unread: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_attachment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    gmail_labels: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    analysis: Mapped["EmailAnalysis | None"] = relationship(
        "EmailAnalysis", back_populates="email", uselist=False, cascade="all, delete-orphan"
    )
