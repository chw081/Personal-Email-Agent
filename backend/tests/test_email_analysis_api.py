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

    def test_bulk_analyze_returns_200_with_expected_shape(self) -> None:
        payload = {
            "emails": [
                {
                    "subject": "Interview invitation",
                    "sender": "recruiter@company.example",
                    "snippet": "Please confirm your interview slot.",
                },
                {
                    "subject": "Invoice for March",
                    "sender": "billing@vendor.example",
                    "snippet": "Your invoice is ready.",
                },
            ]
        }

        response = client.post("/email-analysis/bulk-analyze", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["original_email"]["subject"], "Interview invitation")
        self.assertEqual(data["results"][0]["analysis"]["category"], "Career")
        self.assertEqual(data["results"][1]["original_email"]["subject"], "Invoice for March")
        self.assertEqual(data["results"][1]["analysis"]["category"], "Finance")

    def test_bulk_analyze_empty_list_returns_empty_results(self) -> None:
        response = client.post("/email-analysis/bulk-analyze", json={"emails": []})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"results": []})

    def test_bulk_analyze_rejects_more_than_max_emails(self) -> None:
        payload = {
            "emails": [
                {
                    "subject": f"Email {index}",
                    "sender": "sender@example.com",
                    "snippet": "Preview text.",
                }
                for index in range(51)
            ]
        }

        response = client.post("/email-analysis/bulk-analyze", json=payload)

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main(verbosity=2)
