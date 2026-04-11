import asyncio
from app.schemas.job import NormalizedJob
from app.sources.base import JobSource
from app.utils.browser import BrowserFetcher


class GupySource(JobSource):
    def __init__(
        self,
        source_name: str,
        page_url: str,
        browser_fetcher: BrowserFetcher,
        profile_name: str = ""
    ):
        self.source_name = source_name
        self._page_url = page_url
        self._browser_fetcher = browser_fetcher
        self._profile_name = profile_name

    async def fetch_jobs(self) -> list[NormalizedJob]:
        # Gupy muitas vezes requer scroll ou espera para carregar vagas.
        # O Playwright MCP ajuda a lidar com o JS pesado.
        result = await self._browser_fetcher.fetch_page(self._page_url)
        if not result or not result.html:
            return []

        html = result.html

        # Por enquanto, uma implementação básica de parsing.
        # No futuro, podemos usar seletores específicos da Gupy.
        # A Gupy costuma usar [data-testid="job-list-item"] ou similares.
        from app.utils.html import parse_job_elements
        
        # Exemplo de seletor comum na Gupy
        jobs = parse_job_elements(
            html, 
            source_name=f"Gupy ({self._profile_name})" if self._profile_name else "Gupy",
            item_selector="[data-testid='job-list-item'], a[href*='/job/']",
            title_selector="h3, [class*='JobTitle']",
            location_selector="[class*='JobLocation'], span:contains(' - ')"
        )
        return jobs
