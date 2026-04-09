from typing import Protocol

from app.schemas.job import NormalizedJob


class JobSource(Protocol):
    source_name: str

    async def fetch_jobs(self) -> list[NormalizedJob]:
        ...
