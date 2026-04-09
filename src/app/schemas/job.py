from datetime import datetime

from pydantic import BaseModel, HttpUrl


class NormalizedJob(BaseModel):
    source_name: str
    external_id: str | None = None
    title: str
    company: str
    location: str
    work_model: str
    employment_type: str
    url: HttpUrl
    description_text: str
    posted_at: datetime | None = None
