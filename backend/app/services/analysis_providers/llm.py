"""LLM-based email analysis provider (placeholder — not yet connected to an API)."""

from app.schemas.analysis import EmailAnalysisRequest, EmailAnalysisResponse


class LLMEmailAnalysisProvider:
    """LLM-powered email analysis. Implementation pending external API integration."""

    def analyze(self, email: EmailAnalysisRequest) -> EmailAnalysisResponse:
        """Analyze a single email using an LLM. Not yet implemented."""
        raise NotImplementedError(
            "LLMEmailAnalysisProvider is not yet connected to an external LLM API. "
            "Implement analyze() in llm.py and set DEFAULT_ANALYSIS_PROVIDER when ready."
        )
