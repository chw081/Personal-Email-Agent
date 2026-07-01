"""
Unit tests for analysis provider architecture.

Run from backend/:
    python -m unittest tests.test_analysis_providers -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.analysis import EmailAnalysisRequest
from app.services.analysis_providers.base import get_analysis_content
from app.services.analysis_providers.rule_based import RuleBasedEmailAnalysisProvider
from app.services.email_analysis_service import analyze_email, get_analysis_provider


class AnalysisProviderTests(unittest.TestCase):
    def test_default_provider_is_rule_based(self) -> None:
        self.assertIsInstance(get_analysis_provider(), RuleBasedEmailAnalysisProvider)

    def test_get_analysis_content_prefers_body(self) -> None:
        email = EmailAnalysisRequest(
            subject="Test",
            sender="sender@example.com",
            snippet="snippet text",
            body="full body text",
        )
        self.assertEqual(get_analysis_content(email), "full body text")

    def test_rule_based_provider_matches_service_behavior(self) -> None:
        email = EmailAnalysisRequest(
            subject="Interview invitation",
            sender="recruiter@company.example",
            snippet="Preview",
            body="Please confirm your interview slot by Friday.",
        )

        provider_result = RuleBasedEmailAnalysisProvider().analyze(email)
        service_result = analyze_email(email)

        self.assertEqual(provider_result, service_result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
