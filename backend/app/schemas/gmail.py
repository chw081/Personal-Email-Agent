from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class GmailRecentEmail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    gmail_id: str
    thread_id: str
    from_: str = Field(
        validation_alias=AliasChoices("from", "sender"),
        serialization_alias="from",
    )
    subject: str = ""
    date: str = ""
    snippet: str = ""
    internal_date_ms: int = 0


class GmailRecentResponse(BaseModel):
    source: str = "gmail"
    count: int
    emails: list[GmailRecentEmail]
