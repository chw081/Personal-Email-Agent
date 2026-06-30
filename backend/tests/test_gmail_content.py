"""
Unit tests for gmail_content.py.

Run from backend/:
    python -m unittest tests.test_gmail_content -v
"""

from __future__ import annotations

import base64
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.gmail_content import decode_body_data, extract_message_content, html_to_text


def _b64(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode()).decode().rstrip("=")


class GmailContentTests(unittest.TestCase):
    def test_decode_body_data_round_trip(self) -> None:
        original = "Hello, inbox."
        self.assertEqual(decode_body_data(_b64(original)), original)

    def test_html_to_text_strips_tags(self) -> None:
        html = "<html><body><p>Invoice due</p><p>Please pay by Friday.</p></body></html>"
        text = html_to_text(html)
        self.assertIn("Invoice due", text)
        self.assertIn("Please pay by Friday.", text)
        self.assertNotIn("<p>", text)

    def test_extract_prefers_plain_text_part(self) -> None:
        payload = {
            "mimeType": "multipart/alternative",
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": _b64("Please confirm your interview slot by Friday.")},
                },
                {
                    "mimeType": "text/html",
                    "body": {"data": _b64("<p>Please confirm your interview slot by Friday.</p>")},
                },
            ],
        }

        body_text, has_attachment = extract_message_content(payload)

        self.assertEqual(body_text, "Please confirm your interview slot by Friday.")
        self.assertFalse(has_attachment)

    def test_extract_falls_back_to_html_when_plain_missing(self) -> None:
        payload = {
            "mimeType": "multipart/alternative",
            "parts": [
                {
                    "mimeType": "text/html",
                    "body": {"data": _b64("<p>Your invoice is ready for payment.</p>")},
                },
            ],
        }

        body_text, has_attachment = extract_message_content(payload)

        self.assertIn("invoice is ready", body_text.lower())
        self.assertFalse(has_attachment)

    def test_extract_detects_attachments(self) -> None:
        payload = {
            "mimeType": "multipart/mixed",
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": _b64("Receipt attached.")},
                },
                {
                    "mimeType": "application/pdf",
                    "filename": "receipt.pdf",
                    "headers": [{"name": "Content-Disposition", "value": "attachment; filename=receipt.pdf"}],
                    "body": {"size": 1234},
                },
            ],
        }

        body_text, has_attachment = extract_message_content(payload)

        self.assertEqual(body_text, "Receipt attached.")
        self.assertTrue(has_attachment)


if __name__ == "__main__":
    unittest.main(verbosity=2)
