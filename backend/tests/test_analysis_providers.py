"""
Unit tests for analysis provider architecture.

Run from backend/:
    python -m unittest tests.test_analysis_providers -v
"""

from __future__ import annotations

import inspect
import json
import os
import sys
import unittest
from pathlib import Path
from typing import get_type_hints
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import Settings, get_settings
from app.schemas.analysis import EmailAnalysisRequest, EmailAnalysisResponse
from app.services.analysis_providers import LLMEmailAnalysisProvider
from app.services.analysis_providers.base import get_analysis_content
from app.services.analysis_providers.llm import (
    LLMAnalysisError,
    parse_llm_analysis_response,
    strip_json_fences,
)
from app.services.analysis_providers.rule_based import RuleBasedEmailAnalysisProvider
from app.services import email_analysis_service
from app.services.email_analysis_service import analyze_email, get_analysis_provider


def _rule_based_settings() -> Settings:
    settings = Settings()
    settings.analysis_provider = "rule_based"
    return settings


class AnalysisProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        email_analysis_service.reset_analysis_provider_cache()
        get_settings.cache_clear()

    def tearDown(self) -> None:
        email_analysis_service.reset_analysis_provider_cache()
        get_settings.cache_clear()

    @patch("app.services.email_analysis_service.get_settings", return_value=_rule_based_settings())
    def test_default_provider_is_rule_based(self, _mock_settings: MagicMock) -> None:
        provider = get_analysis_provider()
        self.assertIsInstance(provider, RuleBasedEmailAnalysisProvider)
        self.assertIs(get_analysis_provider(), provider)

    def test_get_analysis_content_prefers_body(self) -> None:
        email = EmailAnalysisRequest(
            subject="Test",
            sender="sender@example.com",
            snippet="snippet text",
            body="full body text",
        )
        self.assertEqual(get_analysis_content(email), "full body text")

    @patch("app.services.email_analysis_service.get_settings", return_value=_rule_based_settings())
    def test_rule_based_provider_matches_service_behavior(self, _mock_settings: MagicMock) -> None:
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
        source = Path(email_analysis_service.__file__).read_text(encoding="utf-8")
        self.assertNotIn("HIGH_PRIORITY_KEYWORDS", source)
        self.assertNotIn("_determine_priority", source)
        self.assertNotIn("_determine_category", source)

    def test_llm_provider_is_importable(self) -> None:
        self.assertTrue(inspect.isclass(LLMEmailAnalysisProvider))

    def test_llm_provider_follows_same_interface(self) -> None:
        rule_based_hints = get_type_hints(RuleBasedEmailAnalysisProvider.analyze)
        llm_hints = get_type_hints(LLMEmailAnalysisProvider.analyze)

        self.assertEqual(rule_based_hints, llm_hints)

    def test_llm_provider_raises_when_api_key_missing(self) -> None:
        settings = Settings()
        settings.gemini_api_key = None
        with patch("app.services.analysis_providers.llm.get_settings", return_value=settings):
            with self.assertRaises(RuntimeError) as ctx:
                LLMEmailAnalysisProvider()

        self.assertIn("GEMINI_API_KEY", str(ctx.exception))

    def test_strip_json_fences(self) -> None:
        raw = '```json\n{"summary": "Hi", "priority": "Low", "category": "Other", "action_items": ["x"]}\n```'
        cleaned = strip_json_fences(raw)
        self.assertTrue(cleaned.startswith("{"))

    def test_parse_llm_analysis_response_validates_schema(self) -> None:
        payload = json.dumps(
            {
                "summary": "Interview invite",
                "priority": "High",
                "category": "Career",
                "action_items": ["Confirm interview slot."],
            }
        )
        result = parse_llm_analysis_response(payload)
        self.assertEqual(result.priority, "High")
        self.assertEqual(result.category, "Career")

    def test_parse_llm_analysis_response_rejects_invalid_json(self) -> None:
        with self.assertRaises(LLMAnalysisError):
            parse_llm_analysis_response("not json")

    @patch("app.services.email_analysis_service.get_settings")
    def test_llm_init_failure_falls_back_to_rule_based_provider(
        self,
        mock_settings: MagicMock,
    ) -> None:
        settings = Settings()
        settings.analysis_provider = "llm"
        settings.gemini_api_key = None
        mock_settings.return_value = settings

        provider = get_analysis_provider()
        self.assertIsInstance(provider, RuleBasedEmailAnalysisProvider)

    @patch("app.services.analysis_providers.llm.get_settings")
    @patch("app.services.email_analysis_service.get_settings")
    def test_llm_provider_selected_when_configured(
        self,
        mock_service_settings: MagicMock,
        mock_llm_settings: MagicMock,
    ) -> None:
        settings = Settings()
        settings.analysis_provider = "llm"
        settings.gemini_api_key = "test-key"
        mock_service_settings.return_value = settings
        mock_llm_settings.return_value = settings

        with patch("app.services.analysis_providers.llm.genai.Client"):
            provider = get_analysis_provider()

        self.assertIsInstance(provider, LLMEmailAnalysisProvider)

    @patch("app.services.email_analysis_service.get_settings")
    def test_llm_failure_falls_back_to_rule_based(self, mock_settings: MagicMock) -> None:
        settings = Settings()
        settings.analysis_provider = "llm"
        settings.gemini_api_key = "test-key"
        mock_settings.return_value = settings

        email = EmailAnalysisRequest(
            subject="Interview invitation",
            sender="recruiter@company.example",
            snippet="Please confirm your interview slot by Friday.",
        )
        expected = RuleBasedEmailAnalysisProvider().analyze(email)

        mock_llm = MagicMock()
        mock_llm.analyze.side_effect = LLMAnalysisError("Gemini unavailable")

        with patch(
            "app.services.email_analysis_service._build_primary_provider",
            return_value=mock_llm,
        ):
            email_analysis_service.reset_analysis_provider_cache()
            result = analyze_email(email)

        self.assertEqual(result, expected)
        mock_llm.analyze.assert_called_once_with(email)


if __name__ == "__main__":
    unittest.main(verbosity=2)
