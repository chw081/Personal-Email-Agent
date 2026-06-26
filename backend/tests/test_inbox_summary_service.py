"""
Unit tests for inbox_summary_service.py.

Run from backend/:
    python -m unittest tests.test_inbox_summary_service -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.analysis import AnalyzedEmail, EmailAnalysisRequest, EmailAnalysisResponse
from app.services.inbox_summary_service import summarize_analyzed_emails


def _analyzed_email(
    subject: str,
    sender: str,
    snippet: str,
    *,
    priority: str,
    category: str,
    action_items: list[str],
) -> AnalyzedEmail:
    return AnalyzedEmail(
        original_email=EmailAnalysisRequest(
            subject=subject,
            sender=sender,
            snippet=snippet,
        ),
        analysis=EmailAnalysisResponse(
            summary=snippet,
            priority=priority,
            category=category,
            action_items=action_items,
        ),
    )


class InboxSummaryServiceTests(unittest.TestCase):
    def test_empty_input_returns_expected_empty_summary(self) -> None:
        summary = summarize_analyzed_emails([])

        self.assertEqual(summary.total_emails, 0)
        self.assertEqual(summary.priority_counts, {})
        self.assertEqual(summary.category_counts, {})
        self.assertEqual(summary.top_action_items, [])
        self.assertEqual(summary.summary, "No emails to summarize.")

    def test_total_emails_matches_input_length(self) -> None:
        results = [
            _analyzed_email(
                "Interview invitation",
                "recruiter@company.example",
                "Confirm your interview slot.",
                priority="High",
                category="Career",
                action_items=["Review and respond if relevant."],
            ),
            _analyzed_email(
                "Invoice for March",
                "billing@vendor.example",
                "Your invoice is ready.",
                priority="Medium",
                category="Finance",
                action_items=["Check financial details."],
            ),
        ]

        summary = summarize_analyzed_emails(results)

        self.assertEqual(summary.total_emails, 2)

    def test_summary_correctly_counts_priorities(self) -> None:
        results = [
            _analyzed_email(
                f"High priority email {index}",
                "sender@example.com",
                "Urgent interview follow up.",
                priority="High",
                category="Career",
                action_items=["Review and respond if relevant."],
            )
            for index in range(2)
        ] + [
            _analyzed_email(
                f"Medium priority email {index}",
                "sender@example.com",
                "Schedule a meeting about invoice.",
                priority="Medium",
                category="Finance",
                action_items=["Check financial details."],
            )
            for index in range(3)
        ] + [
            _analyzed_email(
                f"Low priority email {index}",
                "sender@example.com",
                "Weekly newsletter update.",
                priority="Low",
                category="Other",
                action_items=["No immediate action needed."],
            )
            for index in range(5)
        ]

        summary = summarize_analyzed_emails(results)

        self.assertEqual(summary.priority_counts, {"High": 2, "Medium": 3, "Low": 5})
        self.assertIn(
            "You have 10 emails: 2 high priority, 3 medium priority, and 5 low priority.",
            summary.summary,
        )

    def test_summary_correctly_counts_categories(self) -> None:
        results = [
            _analyzed_email(
                "Limited time sale",
                "promo@store.example",
                "Get 30% off today.",
                priority="Low",
                category="Promotion",
                action_items=["No immediate action needed."],
            ),
            _analyzed_email(
                "Another sale",
                "promo@store.example",
                "Exclusive discount offer.",
                priority="Low",
                category="Promotion",
                action_items=["No immediate action needed."],
            ),
            _analyzed_email(
                "Interview invitation",
                "recruiter@company.example",
                "Confirm your interview slot.",
                priority="High",
                category="Career",
                action_items=["Review and respond if relevant."],
            ),
            _analyzed_email(
                "Application update",
                "jobs@company.example",
                "Your job application status.",
                priority="Low",
                category="Career",
                action_items=["Review and respond if relevant."],
            ),
            _analyzed_email(
                "Invoice ready",
                "billing@vendor.example",
                "Please review payment details.",
                priority="Medium",
                category="Finance",
                action_items=["Check financial details."],
            ),
        ]

        summary = summarize_analyzed_emails(results)

        self.assertEqual(summary.category_counts, {"Promotion": 2, "Career": 2, "Finance": 1})
        self.assertIn("Top categories are Career and Promotion.", summary.summary)

    def test_action_items_are_deduplicated(self) -> None:
        results = [
            _analyzed_email(
                "Interview invitation",
                "recruiter@company.example",
                "Confirm your interview slot.",
                priority="High",
                category="Career",
                action_items=["Review and respond if relevant."],
            ),
            _analyzed_email(
                "Application update",
                "jobs@company.example",
                "Your job application status.",
                priority="Low",
                category="Career",
                action_items=["Review and respond if relevant."],
            ),
            _analyzed_email(
                "Invoice ready",
                "billing@vendor.example",
                "Please review payment details.",
                priority="Medium",
                category="Finance",
                action_items=["Check financial details."],
            ),
            _analyzed_email(
                "Weekly newsletter",
                "news@community.example",
                "Community updates.",
                priority="Low",
                category="Other",
                action_items=["No immediate action needed."],
            ),
        ]

        summary = summarize_analyzed_emails(results)

        self.assertEqual(
            summary.top_action_items,
            [
                "Review and respond if relevant.",
                "Check financial details.",
                "No immediate action needed.",
            ],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
