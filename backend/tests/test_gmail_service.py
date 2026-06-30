"""
Offline tests for gmail_service.py — no browser OAuth required.

Run from backend/:
    python tests/test_gmail_service.py
    python -m unittest tests.test_gmail_service -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services import gmail_service
from app.services.gmail_service import (
    GmailCredentialsNotFoundError,
    GmailServiceError,
    _format_message,
    _header_value,
    fetch_recent_gmail_messages,
)


SAMPLE_GMAIL_RESPONSE = {
    "id": "abc123",
    "threadId": "thread456",
    "internalDate": "1704103200000",
    "snippet": "Your order has shipped.",
    "payload": {
        "headers": [
            {"name": "From", "value": "Shop <orders@shop.example>"},
            {"name": "Subject", "value": "Order shipped"},
            {"name": "Date", "value": "Mon, 1 Jan 2024 10:00:00 +0000"},
        ]
    },
}


def _b64(value: str) -> str:
    import base64

    return base64.urlsafe_b64encode(value.encode()).decode().rstrip("=")


PLAIN_BODY_MESSAGE = {
    **SAMPLE_GMAIL_RESPONSE,
    "payload": {
        "headers": [
            {"name": "From", "value": "Shop <orders@shop.example>"},
            {"name": "To", "value": "customer@example.com"},
            {"name": "Subject", "value": "Order shipped"},
            {"name": "Date", "value": "Mon, 1 Jan 2024 10:00:00 +0000"},
        ],
        "mimeType": "text/plain",
        "body": {"data": _b64("Your order has shipped and will arrive tomorrow.")},
    },
}


class HeaderAndFormatTests(unittest.TestCase):
    def test_header_value_is_case_insensitive(self) -> None:
        headers = [{"name": "Subject", "value": "Hello"}]
        self.assertEqual(_header_value(headers, "subject"), "Hello")

    def test_header_value_missing_returns_empty_string(self) -> None:
        self.assertEqual(_header_value([], "From"), "")

    def test_format_message_maps_expected_fields(self) -> None:
        result = _format_message(SAMPLE_GMAIL_RESPONSE)

        self.assertEqual(result["gmail_id"], "abc123")
        self.assertEqual(result["thread_id"], "thread456")
        self.assertEqual(result["from"], "Shop <orders@shop.example>")
        self.assertEqual(result["subject"], "Order shipped")
        self.assertTrue(result["date"].startswith("2024-01-01"))
        self.assertEqual(result["snippet"], "Your order has shipped.")
        self.assertEqual(result["internal_date_ms"], 1704103200000)
        self.assertEqual(result["recipients"], "")
        self.assertEqual(result["body_text"], "")
        self.assertFalse(result["has_attachment"])

    def test_format_message_extracts_plain_text_body(self) -> None:
        result = _format_message(PLAIN_BODY_MESSAGE)

        self.assertEqual(result["recipients"], "customer@example.com")
        self.assertEqual(result["body_text"], "Your order has shipped and will arrive tomorrow.")
        self.assertFalse(result["has_attachment"])


class FetchRecentMessagesTests(unittest.TestCase):
    def test_rejects_invalid_limit(self) -> None:
        with self.assertRaises(ValueError):
            fetch_recent_gmail_messages(0)

    @patch.object(gmail_service, "get_gmail_service")
    def test_returns_structured_messages(self, mock_get_service: MagicMock) -> None:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "abc123"}, {"id": "def456"}],
        }
        mock_service.users().messages().get().execute.side_effect = [
            PLAIN_BODY_MESSAGE,
            {
                **SAMPLE_GMAIL_RESPONSE,
                "id": "def456",
                "threadId": "thread789",
                "internalDate": "1704189600000",
                "snippet": "Meeting reminder.",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "Calendar <cal@example.com>"},
                        {"name": "To", "value": "team@example.com"},
                        {"name": "Subject", "value": "Team sync"},
                        {"name": "Date", "value": "Tue, 2 Jan 2024 09:00:00 +0000"},
                    ],
                    "mimeType": "text/plain",
                    "body": {"data": _b64("Please schedule a follow up meeting about the invoice.")},
                },
            },
        ]

        results = fetch_recent_gmail_messages(limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["gmail_id"], "def456")
        self.assertEqual(results[1]["gmail_id"], "abc123")
        self.assertEqual(results[0]["subject"], "Team sync")
        self.assertIn("follow up meeting", results[0]["body_text"].lower())
        self.assertEqual(mock_get_service.call_count, 1)

    @patch.object(gmail_service, "get_gmail_service")
    def test_returns_empty_list_when_inbox_is_empty(self, mock_get_service: MagicMock) -> None:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.users().messages().list().execute.return_value = {}

        self.assertEqual(fetch_recent_gmail_messages(limit=5), [])


class OAuthTests(unittest.TestCase):
    @patch.object(gmail_service, "_credentials_path")
    def test_missing_credentials_raises_clear_error(self, mock_path: MagicMock) -> None:
        mock_path.return_value.exists = MagicMock(return_value=False)
        mock_path.return_value.is_file = MagicMock(return_value=False)
        mock_path.return_value.__str__ = lambda self: "/tmp/missing-credentials.json"

        with self.assertRaises(GmailCredentialsNotFoundError):
            gmail_service._run_oauth_flow()


class CredentialsLoadTests(unittest.TestCase):
    @patch.object(gmail_service, "_token_path")
    def test_invalid_token_file_raises_service_error(self, mock_token_path: MagicMock) -> None:
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.__str__ = lambda self: "/tmp/token.json"
        mock_token_path.return_value = mock_file

        with patch.object(
            gmail_service.Credentials,
            "from_authorized_user_file",
            side_effect=ValueError("bad token"),
        ):
            with self.assertRaises(GmailServiceError):
                gmail_service._load_stored_credentials()


if __name__ == "__main__":
    unittest.main(verbosity=2)
