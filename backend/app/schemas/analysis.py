from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EmailAnalysisRequest(BaseModel):
    subject: str
    sender: str
    snippet: str


class EmailAnalysisResponse(BaseModel):
    summary: str
    priority: str
    category: str
    action_items: list[str]


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
