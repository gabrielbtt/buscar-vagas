from dataclasses import dataclass

from app.utils.http import build_http_client


@dataclass(frozen=True)
class BrowserPageResult:
    url: str
    title: str
    html: str


class BrowserFetcher:
    def __init__(self, base_url: str, client=None):
        self.base_url = base_url.rstrip("/")
        self.client = client
        self._owns_client = client is None

    def parse_result(self, payload: dict) -> BrowserPageResult:
        return BrowserPageResult(
            url=payload["url"],
            title=payload["title"],
            html=payload["html"],
        )

    async def fetch_page(self, url: str) -> BrowserPageResult:
        client = self.client or build_http_client()
        try:
            response = await client.post(f"{self.base_url}/fetch", json={"url": url})
            response.raise_for_status()
            return self.parse_result(response.json())
        finally:
            if self._owns_client:
                close = getattr(client, "aclose", None)
                if close is not None:
                    await close()

    async def aclose(self) -> None:
        if self._owns_client or self.client is None:
            return

        close = getattr(self.client, "aclose", None)
        if close is not None:
            await close()


def build_browser_fetcher(base_url: str, client=None) -> BrowserFetcher:
    return BrowserFetcher(base_url=base_url, client=client)
