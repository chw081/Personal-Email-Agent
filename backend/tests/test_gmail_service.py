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
    "snippet": "Your order has shipped.",
    "payload": {
        "headers": [
            {"name": "From", "value": "Shop <orders@shop.example>"},
            {"name": "Subject", "value": "Order shipped"},
            {"name": "Date", "value": "Mon, 1 Jan 2024 10:00:00 +0000"},
        ]
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
        self.assertEqual(result["date"], "Mon, 1 Jan 2024 10:00:00 +0000")
        self.assertEqual(result["snippet"], "Your order has shipped.")


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
            SAMPLE_GMAIL_RESPONSE,
            {
                **SAMPLE_GMAIL_RESPONSE,
                "id": "def456",
                "threadId": "thread789",
                "snippet": "Meeting reminder.",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "Calendar <cal@example.com>"},
                        {"name": "Subject", "value": "Team sync"},
                        {"name": "Date", "value": "Tue, 2 Jan 2024 09:00:00 +0000"},
                    ]
                },
            },
        ]

        results = fetch_recent_gmail_messages(limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["gmail_id"], "abc123")
        self.assertEqual(results[1]["subject"], "Team sync")
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
