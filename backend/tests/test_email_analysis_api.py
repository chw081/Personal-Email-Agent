"""
API tests for the email analysis router.

Run from backend/:
    python -m unittest tests.test_email_analysis_api -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


class EmailAnalysisApiTests(unittest.TestCase):
    def test_analyze_returns_200_with_expected_fields(self) -> None:
        response = client.post(
            "/email-analysis/analyze",
            json={
                "subject": "Weekly newsletter",
                "sender": "news@community.example",
                "snippet": "Here are this week's community updates.",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("summary", data)
        self.assertIn("priority", data)
        self.assertIn("category", data)
        self.assertIn("action_items", data)
        self.assertIsInstance(data["action_items"], list)

    def test_career_interview_email_returns_high_priority_and_career_category(self) -> None:
        response = client.post(
            "/email-analysis/analyze",
            json={
                "subject": "Interview invitation for backend role",
                "sender": "recruiter@company.example",
                "snippet": "Please confirm your interview slot by Friday.",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["priority"], "High")
        self.assertEqual(data["category"], "Career")
        self.assertEqual(data["action_items"], ["Review and respond if relevant."])


if __name__ == "__main__":
    unittest.main(verbosity=2)
