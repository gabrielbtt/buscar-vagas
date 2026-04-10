from app.schemas.job import NormalizedJob
from app.sources.company_pages import parse_company_jobs_html


class BrowserPageSource:
    def __init__(self, source_name: str, page_url: str, browser_fetcher):
        self.source_name = source_name
        self.page_url = page_url
        self.browser_fetcher = browser_fetcher

    async def fetch_jobs(self) -> list[NormalizedJob]:
        page = await self.browser_fetcher.fetch_page(self.page_url)
        return parse_company_jobs_html(page.html, source_name=self.source_name)
