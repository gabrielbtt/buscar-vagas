from datetime import datetime, timezone

from app.schemas.job import NormalizedJob
from app.utils.html import parse_html


def parse_company_jobs_html(html: str, source_name: str) -> list[NormalizedJob]:
    soup = parse_html(html)
    jobs: list[NormalizedJob] = []
    for card in soup.select("article.job-card"):
        jobs.append(
            NormalizedJob(
                source_name=source_name,
                title=card.select_one("h2").get_text(strip=True),
                company=card.select_one(".company").get_text(strip=True),
                location=card.select_one(".location").get_text(strip=True),
                work_model="Presencial",
                employment_type="Estagio",
                url=card.select_one("a")["href"],
                description_text=card.select_one("p").get_text(strip=True),
                posted_at=datetime.now(timezone.utc),
            )
        )
    return jobs


class CompanyPageSource:
    def __init__(self, source_name: str, page_url: str, client_factory, browser_fetcher=None):
        self.source_name = source_name
        self.page_url = page_url
        self.client_factory = client_factory
        self.browser_fetcher = browser_fetcher

    async def fetch_jobs(self) -> list[NormalizedJob]:
        client = self.client_factory()
        try:
            try:
                response = await client.get(self.page_url)
                response.raise_for_status()
                jobs = parse_company_jobs_html(response.text, source_name=self.source_name)
                if jobs or self.browser_fetcher is None:
                    return jobs
            except Exception:
                if self.browser_fetcher is None:
                    raise

            browser_page = await self.browser_fetcher.fetch_page(self.page_url)
            return parse_company_jobs_html(browser_page.html, source_name=self.source_name)
        finally:
            close = getattr(client, "aclose", None)
            if close is not None:
                await close()
