"""Gemini-powered LLM email analysis provider."""

from __future__ import annotations

import json
import logging
import re

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types
from pydantic import ValidationError

from app.config import get_settings
from app.schemas.analysis import EmailAnalysisRequest, EmailAnalysisResponse
from app.services.analysis_providers.base import get_analysis_content

logger = logging.getLogger(__name__)

BODY_MAX_CHARS = 8000

SYSTEM_PROMPT = """You are an email triage assistant for a personal Gmail inbox.

Analyze the email and return ONLY valid JSON matching this exact structure:
{
  "summary": "<one clear sentence, max 180 characters>",
  "priority": "<High | Medium | Low>",
  "category": "<Career | Finance | Promotion | Other>",
  "action_items": ["<short suggested action>", "..."]
}

Priority rules:
- High: requires a reply/action soon, has a deadline, interview, job opportunity, payment issue, account/security issue, bill due, or important personal/official matter.
- Medium: useful or relevant but not urgent; may need review later.
- Low: newsletters, ads, receipts with no issue, automated updates, FYI messages, or anything safely ignorable.

Category rules:
- Career: jobs, recruiters, interviews, applications, work, school/career opportunities.
- Finance: banking, bills, invoices, payments, refunds, taxes, subscriptions, insurance, financial alerts.
- Promotion: marketing, discounts, sales, coupons, product recommendations, newsletters mainly trying to sell something.
- Other: anything that does not clearly fit the above.

Action item rules:
- Give 1-3 practical action items.
- If no action is needed, return exactly: ["No immediate action needed."]
- Do not invent deadlines, amounts, people, or facts not present in the email.
- If the email is suspicious or asks for sensitive info, mention verifying the sender before acting.

Summary rules:
- Be specific and useful.
- Mention the sender/company only if helpful.
- Do not include phrases like "This email says" or "The email is about".

Return ONLY the JSON object. No markdown, no code fences, no explanation."""

_JSON_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


class LLMAnalysisError(Exception):
    """Raised when Gemini analysis or response parsing fails."""


def _truncate_content(content: str, max_chars: int = BODY_MAX_CHARS) -> str:
    cleaned = content.strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars] + "…"


def _build_user_prompt(email: EmailAnalysisRequest) -> str:
    content = _truncate_content(get_analysis_content(email))
    return (
        f"From: {email.sender}\n"
        f"Subject: {email.subject}\n"
        f"Snippet: {email.snippet.strip() or '(empty)'}\n"
        f"Body:\n{content or '(empty)'}"
    )


def strip_json_fences(text: str) -> str:
    """Remove optional markdown code fences from an LLM response."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = _JSON_FENCE_PATTERN.sub("", cleaned).strip()
    return cleaned


def parse_llm_analysis_response(text: str) -> EmailAnalysisResponse:
    """Parse and validate a Gemini JSON response into EmailAnalysisResponse."""
    cleaned = strip_json_fences(text)
    if not cleaned:
        raise LLMAnalysisError("Gemini returned an empty response")

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMAnalysisError(f"Gemini response is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise LLMAnalysisError("Gemini response must be a JSON object")

    try:
        return EmailAnalysisResponse.model_validate(data)
    except ValidationError as exc:
        raise LLMAnalysisError(f"Gemini response failed schema validation: {exc}") from exc


class LLMEmailAnalysisProvider:
    """Gemini-powered email analysis via the google-genai SDK."""

    def __init__(self) -> None:
        settings = get_settings()
        api_key = settings.gemini_api_key
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Set it in backend/.env to use the LLM analysis provider."
            )
        self._model = settings.gemini_model
        self._client = genai.Client(api_key=api_key)

    def analyze(self, email: EmailAnalysisRequest) -> EmailAnalysisResponse:
        prompt = _build_user_prompt(email)

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
        except genai_errors.APIError as exc:
            raise LLMAnalysisError(f"Gemini API request failed: {exc}") from exc
        except Exception as exc:
            raise LLMAnalysisError(f"Gemini API request failed: {exc}") from exc

        response_text = (response.text or "").strip()
        if not response_text:
            raise LLMAnalysisError("Gemini returned an empty response")

        return parse_llm_analysis_response(response_text)
