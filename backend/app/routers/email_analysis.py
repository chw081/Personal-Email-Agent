from fastapi import APIRouter

from app.schemas.analysis import (
    BulkEmailAnalysisRequest,
    BulkEmailAnalysisResponse,
    EmailAnalysisRequest,
    EmailAnalysisResponse,
    InboxSummaryResponse,
)
from app.services.email_analysis_service import analyze_email, analyze_emails_bulk
from app.services.inbox_summary_service import summarize_analyzed_emails

router = APIRouter(prefix="/email-analysis", tags=["email-analysis"])


@router.post("/analyze", response_model=EmailAnalysisResponse)
def analyze_email_endpoint(payload: EmailAnalysisRequest) -> EmailAnalysisResponse:
    return analyze_email(payload)


@router.post("/bulk-analyze", response_model=BulkEmailAnalysisResponse)
def bulk_analyze_emails_endpoint(payload: BulkEmailAnalysisRequest) -> BulkEmailAnalysisResponse:
    return BulkEmailAnalysisResponse(results=analyze_emails_bulk(payload.emails))


@router.post("/inbox-summary", response_model=InboxSummaryResponse)
def inbox_summary_endpoint(payload: BulkEmailAnalysisRequest) -> InboxSummaryResponse:
    analyzed = analyze_emails_bulk(payload.emails)
    return summarize_analyzed_emails(analyzed)
