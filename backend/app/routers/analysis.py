from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.analysis import EmailAnalysis
from app.models.email import Email
from app.schemas.analysis import EmailAnalysisRead
from app.services.classifier_service import classify_email

router = APIRouter(prefix="/emails", tags=["analysis"])


@router.post("/{email_id}/analyze", response_model=EmailAnalysisRead)
def analyze_email(email_id: str, db: Session = Depends(get_db)) -> EmailAnalysis:
    email = db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")

    result = classify_email(email)

    if email.analysis:
        db.delete(email.analysis)
        db.flush()

    analysis = EmailAnalysis(
        email_id=email.id,
        domain=result.domain,
        subcategory=result.subcategory,
        priority=result.priority,
        action=result.action,
        confidence=result.confidence,
        reason=result.reason,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("/{email_id}/analysis", response_model=EmailAnalysisRead)
def get_email_analysis(email_id: str, db: Session = Depends(get_db)) -> EmailAnalysis:
    email = db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    if not email.analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return email.analysis
