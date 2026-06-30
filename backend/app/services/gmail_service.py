"""Gmail OAuth authentication and read-only message fetching."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError

from app.config import get_settings
from app.services.gmail_content import extract_message_content

logger = logging.getLogger(__name__)

GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
SCOPES = [GMAIL_READONLY_SCOPE]

GmailMessage = TypedDict(
    "GmailMessage",
    {
        "gmail_id": str,
        "thread_id": str,
        "from": str,
        "recipients": str,
        "subject": str,
        "date": str,
        "snippet": str,
        "body_text": str,
        "has_attachment": bool,
        "internal_date_ms": int,
    },
)


class GmailServiceError(Exception):
    """Raised when Gmail authentication or API calls fail."""


class GmailCredentialsNotFoundError(GmailServiceError):
    """Raised when OAuth client credentials are missing."""


def _credentials_path() -> Path:
    return Path(get_settings().gmail_credentials_path)


def _token_path() -> Path:
    return Path(get_settings().gmail_token_path)


def _load_stored_credentials() -> Credentials | None:
    token_file = _token_path()
    if not token_file.is_file():
        return None

    try:
        return Credentials.from_authorized_user_file(str(token_file), SCOPES)
    except (ValueError, json.JSONDecodeError) as exc:
        raise GmailServiceError(f"Invalid token file at {token_file}") from exc


def _save_credentials(credentials: Credentials) -> None:
    token_file = _token_path()
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(credentials.to_json(), encoding="utf-8")
    logger.info("Saved Gmail OAuth token to %s", token_file)


def _refresh_credentials(credentials: Credentials) -> Credentials:
    try:
        credentials.refresh(Request())
    except Exception as exc:
        raise GmailServiceError("Failed to refresh Gmail OAuth token") from exc
    return credentials


def _run_oauth_flow() -> Credentials:
    credentials_file = _credentials_path()
    if not credentials_file.is_file():
        raise GmailCredentialsNotFoundError(
            f"Gmail OAuth credentials not found at {credentials_file}. "
            "Download credentials.json from Google Cloud Console."
        )

    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
        return flow.run_local_server(port=0)
    except Exception as exc:
        raise GmailServiceError("Gmail OAuth flow failed") from exc


def get_gmail_credentials() -> Credentials:
    """Return valid Gmail OAuth credentials, refreshing or prompting as needed."""
    credentials = _load_stored_credentials()

    if credentials and credentials.valid:
        return credentials

    if credentials and credentials.expired and credentials.refresh_token:
        credentials = _refresh_credentials(credentials)
        _save_credentials(credentials)
        return credentials

    credentials = _run_oauth_flow()
    _save_credentials(credentials)
    return credentials


def get_gmail_service() -> Resource:
    """Build an authenticated Gmail API client."""
    credentials = get_gmail_credentials()
    try:
        return build("gmail", "v1", credentials=credentials, cache_discovery=False)
    except Exception as exc:
        raise GmailServiceError("Failed to initialize Gmail API client") from exc


def _header_value(headers: list[dict[str, str]], name: str) -> str:
    target = name.lower()
    for header in headers:
        if header.get("name", "").lower() == target:
            return header.get("value", "")
    return ""


def _internal_date_ms(message: dict) -> int:
    value = message.get("internalDate")
    if value is None:
        return 0
    return int(value)


def _format_date(message: dict, headers: list[dict[str, str]]) -> str:
    internal_ms = _internal_date_ms(message)
    if internal_ms:
        return datetime.fromtimestamp(internal_ms / 1000, tz=timezone.utc).isoformat()
    return _header_value(headers, "Date")


def _format_message(message: dict) -> GmailMessage:
    payload = message.get("payload", {})
    headers = payload.get("headers", [])
    body_text, has_attachment = extract_message_content(payload)

    return {
        "gmail_id": message.get("id", ""),
        "thread_id": message.get("threadId", ""),
        "from": _header_value(headers, "From"),
        "recipients": _header_value(headers, "To"),
        "subject": _header_value(headers, "Subject"),
        "date": _format_date(message, headers),
        "snippet": message.get("snippet", ""),
        "body_text": body_text,
        "has_attachment": has_attachment,
        "internal_date_ms": _internal_date_ms(message),
    }


def _fetch_message(service: Resource, message_id: str) -> GmailMessage:
    try:
        message = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full",
            )
            .execute()
        )
    except HttpError as exc:
        raise GmailServiceError(f"Failed to fetch Gmail message {message_id}") from exc

    return _format_message(message)


def fetch_recent_gmail_messages(limit: int = 5) -> list[GmailMessage]:
    """
    Authenticate with Gmail and fetch recent inbox messages.

    Args:
        limit: Maximum number of messages to return (default 5).

    Returns:
        A list of structured message dictionaries sorted newest-first.
    """
    if limit < 1:
        raise ValueError("limit must be at least 1")

    service = get_gmail_service()

    try:
        response = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], maxResults=limit)
            .execute()
        )
    except HttpError as exc:
        raise GmailServiceError("Failed to list Gmail inbox messages") from exc

    message_refs = response.get("messages", [])
    if not message_refs:
        return []

    messages: list[GmailMessage] = []
    for ref in message_refs:
        message_id = ref.get("id")
        if not message_id:
            continue
        messages.append(_fetch_message(service, message_id))

    messages.sort(key=lambda message: message["internal_date_ms"], reverse=True)
    return messages[:limit]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = fetch_recent_gmail_messages()
    for item in results:
        print(json.dumps(item, indent=2))
