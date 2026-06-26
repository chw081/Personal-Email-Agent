"""
Unit tests for bulk email analysis in email_analysis_service.py.

Run from backend/:
    python -m unittest tests.test_email_analysis_bulk_service -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.analysis import EmailAnalysisRequest
from app.services.email_analysis_service import analyze_emails_bulk


class BulkEmailAnalysisServiceTests(unittest.TestCase):
    def test_empty_list_returns_empty_results(self) -> None:
        self.assertEqual(analyze_emails_bulk([]), [])

    def test_returns_same_number_of_results_as_input(self) -> None:
        emails = [
            EmailAnalysisRequest(
                subject="Interview invitation",
                sender="recruiter@company.example",
                snippet="Please confirm your interview slot.",
            ),
            EmailAnalysisRequest(
                subject="Invoice for March",
                sender="billing@vendor.example",
                snippet="Your invoice is ready.",
            ),
            EmailAnalysisRequest(
                subject="Weekly newsletter",
                sender="news@community.example",
                snippet="Community updates this week.",
            ),
        ]

        results = analyze_emails_bulk(emails)

        self.assertEqual(len(results), len(emails))

    def test_preserves_input_order(self) -> None:
        emails = [
            EmailAnalysisRequest(
                subject="Weekly newsletter",
                sender="news@community.example",
                snippet="Community updates.",
            ),
            EmailAnalysisRequest(
                subject="Interview invitation",
                sender="recruiter@company.example",
                snippet="Confirm your interview slot.",
            ),
            EmailAnalysisRequest(
                subject="Limited time sale",
                sender="promo@store.example",
                snippet="Get 30% off today.",
            ),
        ]

        results = analyze_emails_bulk(emails)

        self.assertEqual(results[0].original_email.subject, "Weekly newsletter")
        self.assertEqual(results[1].original_email.subject, "Interview invitation")
        self.assertEqual(results[2].original_email.subject, "Limited time sale")

    def test_handles_mixed_categories_and_priorities(self) -> None:
        emails = [
            EmailAnalysisRequest(
                subject="Interview invitation for backend role",
                sender="recruiter@company.example",
                snippet="Please confirm your interview slot by Friday.",
            ),
            EmailAnalysisRequest(
                subject="Invoice for March services",
                sender="billing@vendor.example",
                snippet="Your invoice is ready. Please schedule payment.",
            ),
            EmailAnalysisRequest(
                subject="Limited time sale",
                sender="promo@store.example",
                snippet="Get 30% off with this exclusive discount offer.",
            ),
        ]

        results = analyze_emails_bulk(emails)

        self.assertEqual(results[0].analysis.priority, "High")
        self.assertEqual(results[0].analysis.category, "Career")
        self.assertEqual(results[1].analysis.priority, "Medium")
        self.assertEqual(results[1].analysis.category, "Finance")
        self.assertEqual(results[2].analysis.category, "Promotion")

    def test_preserves_original_email_data(self) -> None:
        email = EmailAnalysisRequest(
            subject="Interview invitation",
            sender="recruiter@company.example",
            snippet="Please confirm your interview slot.",
        )

        results = analyze_emails_bulk([email])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].original_email, email)
        self.assertEqual(results[0].original_email.subject, "Interview invitation")
        self.assertEqual(results[0].original_email.sender, "recruiter@company.example")
        self.assertEqual(results[0].original_email.snippet, "Please confirm your interview slot.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
