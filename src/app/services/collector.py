from app.schemas.job import NormalizedJob
from app.sources.browser_pages import BrowserPageSource
from app.sources.company_pages import CompanyPageSource
from app.utils.browser import build_browser_fetcher


class StaticCollector:
    def __init__(self, jobs: list[NormalizedJob]):
        self._jobs = jobs

    async def fetch_all(self) -> list[NormalizedJob]:
        return self._jobs


class MultiSourceCollector:
    def __init__(self, sources):
        self._sources = sources

    @classmethod
    def build_from_settings(cls, settings, client_factory):
        sources = []
        browser_fetcher = None
        if getattr(settings, "playwright_mcp_url", ""):
            browser_fetcher = build_browser_fetcher(settings.playwright_mcp_url)

        if getattr(settings, "company_page_source_enabled", False) and getattr(settings, "company_page_source_url", ""):
            sources.append(
                CompanyPageSource(
                    source_name="company-page",
                    page_url=settings.company_page_source_url,
                    client_factory=client_factory,
                    browser_fetcher=browser_fetcher,
                )
            )
        if browser_fetcher and getattr(settings, "browser_page_source_enabled", False) and getattr(settings, "browser_page_source_url", ""):
            sources.append(
                BrowserPageSource(
                    source_name="browser-page",
                    page_url=settings.browser_page_source_url,
                    browser_fetcher=browser_fetcher,
                )
            )
        return cls(sources)

    async def fetch_all(self) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        for source in self._sources:
            jobs.extend(await source.fetch_jobs())
        return jobs
