"""
Unit tests for analysis provider architecture.

Run from backend/:
    python -m unittest tests.test_analysis_providers -v
"""

from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.analysis import EmailAnalysisRequest, EmailAnalysisResponse
from app.services.analysis_providers import LLMEmailAnalysisProvider
from app.services.analysis_providers.base import get_analysis_content
from app.services.analysis_providers.rule_based import RuleBasedEmailAnalysisProvider
from app.services.email_analysis_service import analyze_email, get_analysis_provider


class AnalysisProviderTests(unittest.TestCase):
    def test_default_provider_is_rule_based(self) -> None:
        from app.services.email_analysis_service import DEFAULT_ANALYSIS_PROVIDER

        self.assertIsInstance(DEFAULT_ANALYSIS_PROVIDER, RuleBasedEmailAnalysisProvider)
        self.assertIs(get_analysis_provider(), DEFAULT_ANALYSIS_PROVIDER)

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

    def test_service_has_no_rule_logic_duplication(self) -> None:
        import app.services.email_analysis_service as service_module

        source = Path(service_module.__file__).read_text(encoding="utf-8")
        self.assertNotIn("HIGH_PRIORITY_KEYWORDS", source)
        self.assertNotIn("_determine_priority", source)
        self.assertNotIn("_determine_category", source)

    def test_llm_provider_is_importable(self) -> None:
        self.assertTrue(inspect.isclass(LLMEmailAnalysisProvider))

    def test_llm_provider_follows_same_interface(self) -> None:
        rule_based_sig = inspect.signature(RuleBasedEmailAnalysisProvider.analyze)
        llm_sig = inspect.signature(LLMEmailAnalysisProvider.analyze)

        self.assertEqual(rule_based_sig, llm_sig)
        self.assertEqual(
            llm_sig.return_annotation,
            EmailAnalysisResponse,
        )

    def test_llm_provider_raises_not_implemented(self) -> None:
        email = EmailAnalysisRequest(
            subject="Test subject",
            sender="sender@example.com",
            snippet="Preview text",
        )

        with self.assertRaises(NotImplementedError) as ctx:
            LLMEmailAnalysisProvider().analyze(email)

        self.assertIn("LLMEmailAnalysisProvider", str(ctx.exception))
        self.assertIn("not yet connected", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
