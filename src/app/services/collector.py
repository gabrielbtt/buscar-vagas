from app.schemas.job import NormalizedJob


class StaticCollector:
    def __init__(self, jobs: list[NormalizedJob]):
        self._jobs = jobs

    async def fetch_all(self) -> list[NormalizedJob]:
        return self._jobs
