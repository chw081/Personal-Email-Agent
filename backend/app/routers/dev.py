from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.email import EmailRead
from app.services.mock_data import seed_mock_emails

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/seed", response_model=list[EmailRead])
def seed_database(db: Session = Depends(get_db)) -> list:
    return seed_mock_emails(db)
