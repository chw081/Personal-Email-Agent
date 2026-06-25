from fastapi import APIRouter

from app.schemas.analysis import EmailAnalysisRequest, EmailAnalysisResponse
from app.services.email_analysis_service import analyze_email

router = APIRouter(prefix="/email-analysis", tags=["email-analysis"])


@router.post("/analyze", response_model=EmailAnalysisResponse)
def analyze_email_endpoint(payload: EmailAnalysisRequest) -> EmailAnalysisResponse:
    return analyze_email(payload)
