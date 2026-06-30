"""
Unit tests for email_analysis_service.py.

Run from backend/:
    python tests/test_email_analysis_service.py
    python -m unittest tests.test_email_analysis_service -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.analysis import EmailAnalysisRequest
from app.services.email_analysis_service import analyze_email


class EmailAnalysisServiceTests(unittest.TestCase):
    def test_high_priority_career_email(self) -> None:
        result = analyze_email(
            EmailAnalysisRequest(
                subject="Interview invitation for backend role",
                sender="recruiter@company.example",
                snippet="Please confirm your interview slot by Friday.",
            )
        )

        self.assertEqual(result.priority, "High")
        self.assertEqual(result.category, "Career")
        self.assertEqual(result.action_items, ["Review and respond if relevant."])
        self.assertIn("interview slot", result.summary)

    def test_medium_priority_finance_email(self) -> None:
        result = analyze_email(
            EmailAnalysisRequest(
                subject="Invoice for March services",
                sender="billing@vendor.example",
                snippet="Your invoice is ready. Please schedule payment by month end.",
            )
        )

        self.assertEqual(result.priority, "Medium")
        self.assertEqual(result.category, "Finance")
        self.assertEqual(result.action_items, ["Check financial details."])

    def test_promotion_email(self) -> None:
        result = analyze_email(
            EmailAnalysisRequest(
                subject="Limited time sale",
                sender="promo@store.example",
                snippet="Get 30% off with this exclusive discount offer today.",
            )
        )

        self.assertEqual(result.category, "Promotion")
        self.assertEqual(result.action_items, ["No immediate action needed."])

    def test_empty_snippet_fallback_summary(self) -> None:
        result = analyze_email(
            EmailAnalysisRequest(
                subject="Hello",
                sender="friend@example.com",
                snippet="   ",
            )
        )

        self.assertEqual(result.summary, "No useful preview available.")

    def test_default_other_low_case(self) -> None:
        result = analyze_email(
            EmailAnalysisRequest(
                subject="Weekly newsletter",
                sender="news@community.example",
                snippet="Here are this week's community updates and announcements.",
            )
        )

        self.assertEqual(result.priority, "Low")
        self.assertEqual(result.category, "Other")
        self.assertEqual(result.action_items, ["No immediate action needed."])

    def test_prefers_body_over_snippet_for_classification(self) -> None:
        result = analyze_email(
            EmailAnalysisRequest(
                subject="Weekly newsletter",
                sender="news@community.example",
                snippet="Short preview only.",
                body=(
                    "Interview invitation: please confirm your interview slot by Friday. "
                    "This message requires action."
                ),
            )
        )

        self.assertEqual(result.priority, "High")
        self.assertEqual(result.category, "Career")
        self.assertIn("interview slot", result.summary)


if __name__ == "__main__":
    unittest.main(verbosity=2)
