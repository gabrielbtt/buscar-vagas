from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserPageResult:
    url: str
    title: str
    html: str


class BrowserFetcher:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def parse_result(self, payload: dict) -> BrowserPageResult:
        return BrowserPageResult(
            url=payload["url"],
            title=payload["title"],
            html=payload["html"],
        )


def build_browser_fetcher(base_url: str) -> BrowserFetcher:
    return BrowserFetcher(base_url=base_url)
