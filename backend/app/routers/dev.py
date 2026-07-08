from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.email import EmailRead
from app.schemas.gmail import GmailRecentEmail, GmailRecentResponse
from app.services.gmail_service import (
    GmailCredentialsNotFoundError,
    GmailServiceError,
    fetch_recent_gmail_messages,
)
from app.services.mock_data import seed_mock_emails

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/seed", response_model=list[EmailRead])
def seed_database(db: Session = Depends(get_db)) -> list:
    return seed_mock_emails(db)


@router.get("/gmail/recent", response_model=GmailRecentResponse, response_model_by_alias=True)
def get_recent_gmail_messages(
    limit: int = Query(default=20, ge=1, le=50, description="Number of inbox messages to fetch"),
) -> GmailRecentResponse:
    try:
        emails = fetch_recent_gmail_messages(limit=limit)
    except GmailCredentialsNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except GmailServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return GmailRecentResponse(
        source="gmail",
        count=len(emails),
        emails=[GmailRecentEmail.model_validate(email) for email in emails],
    )
