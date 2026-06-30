from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EmailAnalysisRequest(BaseModel):
    subject: str
    sender: str
    snippet: str = ""
    body: str | None = Field(
        default=None,
        description="Full extracted email body; preferred over snippet for analysis when present.",
    )


class EmailAnalysisResponse(BaseModel):
    summary: str
    priority: str
    category: str
    action_items: list[str]


BULK_EMAIL_ANALYSIS_MAX_SIZE = 50


class BulkEmailAnalysisRequest(BaseModel):
    emails: list[EmailAnalysisRequest] = Field(default_factory=list, max_length=BULK_EMAIL_ANALYSIS_MAX_SIZE)


class AnalyzedEmail(BaseModel):
    original_email: EmailAnalysisRequest
    analysis: EmailAnalysisResponse


class BulkEmailAnalysisResponse(BaseModel):
    results: list[AnalyzedEmail]


class InboxSummaryResponse(BaseModel):
    total_emails: int
    priority_counts: dict[str, int]
    category_counts: dict[str, int]
    top_action_items: list[str]
    summary: str


class EmailAnalysisCreate(BaseModel):
    domain: str
    subcategory: str
    priority: str
    action: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str | None = None
    model_name: str = "mock-classifier-v1"
    schema_version: str = "v1"


class EmailAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email_id: str
    domain: str
    subcategory: str
    priority: str
    action: str
    confidence: float
    reason: str | None
    model_name: str
    schema_version: str
    created_at: datetime
