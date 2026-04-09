from pydantic import BaseModel


class RecentJobsResponse(BaseModel):
    items: list[dict]
