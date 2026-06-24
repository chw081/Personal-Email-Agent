from pydantic import BaseModel, ConfigDict, Field


class GmailRecentEmail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    gmail_id: str
    thread_id: str
    sender: str = Field(alias="from")
    subject: str
    date: str
    snippet: str


class GmailRecentResponse(BaseModel):
    source: str = "gmail"
    count: int
    emails: list[GmailRecentEmail]
