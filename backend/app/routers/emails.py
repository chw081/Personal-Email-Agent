from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.email import Email
from app.schemas.email import EmailCreate, EmailRead

router = APIRouter(prefix="/emails", tags=["emails"])


@router.post("", response_model=EmailRead, status_code=status.HTTP_201_CREATED)
def create_email(payload: EmailCreate, db: Session = Depends(get_db)) -> Email:
    if payload.gmail_message_id:
        existing = (
            db.query(Email)
            .filter(Email.gmail_message_id == payload.gmail_message_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email with this gmail_message_id already exists",
            )

    email = Email(**payload.model_dump())
    db.add(email)
    db.commit()
    db.refresh(email)
    return email


@router.get("", response_model=list[EmailRead])
def list_emails(db: Session = Depends(get_db)) -> list[Email]:
    return db.query(Email).order_by(Email.received_at.desc().nullslast(), Email.created_at.desc()).all()


@router.get("/{email_id}", response_model=EmailRead)
def get_email(email_id: str, db: Session = Depends(get_db)) -> Email:
    email = db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    return email
