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

SAMPLE_BULK_PAYLOAD = {
    "emails": [
        {
            "subject": "Interview invitation for backend role",
            "sender": "recruiter@company.example",
            "snippet": "Please confirm your interview slot by Friday.",
        },
        {
            "subject": "Invoice for March services",
            "sender": "billing@vendor.example",
            "snippet": "Your invoice is ready. Please schedule payment.",
        },
        {
            "subject": "Limited time sale",
            "sender": "promo@store.example",
            "snippet": "Get 30% off with this exclusive discount offer today.",
        },
    ]
}


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


class BulkAnalyzeApiTests(unittest.TestCase):
    def test_bulk_analyze_returns_200(self) -> None:
        response = client.post("/email-analysis/bulk-analyze", json=SAMPLE_BULK_PAYLOAD)

        self.assertEqual(response.status_code, 200)

    def test_bulk_analyze_returns_same_number_of_results_as_input(self) -> None:
        response = client.post("/email-analysis/bulk-analyze", json=SAMPLE_BULK_PAYLOAD)

        data = response.json()
        self.assertEqual(len(data["results"]), len(SAMPLE_BULK_PAYLOAD["emails"]))

    def test_bulk_analyze_preserves_original_email_data(self) -> None:
        response = client.post("/email-analysis/bulk-analyze", json=SAMPLE_BULK_PAYLOAD)

        data = response.json()
        for index, email in enumerate(SAMPLE_BULK_PAYLOAD["emails"]):
            original = data["results"][index]["original_email"]
            self.assertEqual(original["subject"], email["subject"])
            self.assertEqual(original["sender"], email["sender"])
            self.assertEqual(original["snippet"], email["snippet"])

    def test_bulk_analyze_includes_analysis_fields(self) -> None:
        response = client.post("/email-analysis/bulk-analyze", json=SAMPLE_BULK_PAYLOAD)

        analysis = response.json()["results"][0]["analysis"]
        self.assertIn("summary", analysis)
        self.assertIn("priority", analysis)
        self.assertIn("category", analysis)
        self.assertIn("action_items", analysis)
        self.assertEqual(analysis["priority"], "High")
        self.assertEqual(analysis["category"], "Career")

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

    def test_bulk_analyze_rejects_invalid_request_body(self) -> None:
        response = client.post(
            "/email-analysis/bulk-analyze",
            json={"emails": [{"subject": "Missing fields"}]},
        )

        self.assertEqual(response.status_code, 422)


class InboxSummaryApiTests(unittest.TestCase):
    def test_inbox_summary_returns_200(self) -> None:
        response = client.post("/email-analysis/inbox-summary", json=SAMPLE_BULK_PAYLOAD)

        self.assertEqual(response.status_code, 200)

    def test_inbox_summary_returns_expected_fields(self) -> None:
        response = client.post("/email-analysis/inbox-summary", json=SAMPLE_BULK_PAYLOAD)

        data = response.json()
        self.assertIn("total_emails", data)
        self.assertIn("priority_counts", data)
        self.assertIn("category_counts", data)
        self.assertIn("top_action_items", data)
        self.assertIn("summary", data)

    def test_inbox_summary_counts_priorities_and_categories(self) -> None:
        response = client.post("/email-analysis/inbox-summary", json=SAMPLE_BULK_PAYLOAD)

        data = response.json()
        self.assertEqual(data["total_emails"], 3)
        self.assertEqual(data["priority_counts"], {"High": 1, "Medium": 1, "Low": 1})
        self.assertEqual(data["category_counts"], {"Career": 1, "Finance": 1, "Promotion": 1})

    def test_inbox_summary_returns_deduplicated_action_items(self) -> None:
        response = client.post("/email-analysis/inbox-summary", json=SAMPLE_BULK_PAYLOAD)

        data = response.json()
        self.assertEqual(
            data["top_action_items"],
            [
                "Review and respond if relevant.",
                "Check financial details.",
                "No immediate action needed.",
            ],
        )

    def test_inbox_summary_returns_human_readable_summary(self) -> None:
        response = client.post("/email-analysis/inbox-summary", json=SAMPLE_BULK_PAYLOAD)

        data = response.json()
        self.assertIn("You have 3 emails:", data["summary"])
        self.assertIn("1 high priority", data["summary"])
        self.assertIn("1 medium priority", data["summary"])
        self.assertIn("1 low priority", data["summary"])

    def test_inbox_summary_empty_input_returns_empty_summary(self) -> None:
        response = client.post("/email-analysis/inbox-summary", json={"emails": []})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_emails"], 0)
        self.assertEqual(data["priority_counts"], {})
        self.assertEqual(data["category_counts"], {})
        self.assertEqual(data["top_action_items"], [])
        self.assertEqual(data["summary"], "No emails to summarize.")

    def test_inbox_summary_rejects_more_than_max_emails(self) -> None:
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

        response = client.post("/email-analysis/inbox-summary", json=payload)

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main(verbosity=2)
