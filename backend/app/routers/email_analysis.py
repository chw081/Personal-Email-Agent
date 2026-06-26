from fastapi import APIRouter

from app.schemas.analysis import (
    BulkEmailAnalysisRequest,
    BulkEmailAnalysisResponse,
    EmailAnalysisRequest,
    EmailAnalysisResponse,
)
from app.services.email_analysis_service import analyze_email, analyze_emails_bulk

router = APIRouter(prefix="/email-analysis", tags=["email-analysis"])


@router.post("/analyze", response_model=EmailAnalysisResponse)
def analyze_email_endpoint(payload: EmailAnalysisRequest) -> EmailAnalysisResponse:
    return analyze_email(payload)


@router.post("/bulk-analyze", response_model=BulkEmailAnalysisResponse)
def bulk_analyze_emails_endpoint(payload: BulkEmailAnalysisRequest) -> BulkEmailAnalysisResponse:
    return BulkEmailAnalysisResponse(results=analyze_emails_bulk(payload.emails))
