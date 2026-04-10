from pydantic import BaseModel


class RecentJobItem(BaseModel):
    company: str
    title: str
    location: str
    employment_type: str
    score: float
    url: str
    notified: bool
    source_name: str


class RecentJobsResponse(BaseModel):
    items: list[RecentJobItem]
