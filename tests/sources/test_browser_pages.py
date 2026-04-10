import asyncio
from pathlib import Path

from app.sources.browser_pages import BrowserPageSource
from app.utils.browser import BrowserPageResult, build_browser_fetcher


def test_build_browser_fetcher_supports_dynamic_sources():
    fetcher = build_browser_fetcher(base_url="http://localhost:8931")

    result = fetcher.parse_result(
        {
            "url": "https://example.com/jobs/1",
            "title": "Estagio em Automacao Industrial",
            "html": "<html></html>",
        }
    )

    assert result == BrowserPageResult(
        url="https://example.com/jobs/1",
        title="Estagio em Automacao Industrial",
        html="<html></html>",
    )


def test_browser_fetcher_fetch_page_posts_to_fetch_endpoint():
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "url": "https://example.com/jobs/2",
                "title": "Trainee em Automacao",
                "html": "<html><body>vaga</body></html>",
            }

    class FakeClient:
        def __init__(self):
            self.calls = []

        async def post(self, url: str, json: dict):
            self.calls.append((url, json))
            return FakeResponse()

    client = FakeClient()
    fetcher = build_browser_fetcher(base_url="http://localhost:8931", client=client)

    result = asyncio.run(fetcher.fetch_page("https://example.com/jobs/2"))

    assert client.calls == [
        ("http://localhost:8931/fetch", {"url": "https://example.com/jobs/2"})
    ]
    assert result == BrowserPageResult(
        url="https://example.com/jobs/2",
        title="Trainee em Automacao",
        html="<html><body>vaga</body></html>",
    )


def test_browser_page_source_parses_jobs_from_browser_fetcher_html():
    class FakeBrowserFetcher:
        def __init__(self, html: str):
            self.html = html
            self.calls = []

        async def fetch_page(self, url: str):
            self.calls.append(url)
            return BrowserPageResult(url=url, title="Vagas", html=self.html)

    html = Path("tests/sources/fixtures/company_page_sample.html").read_text(encoding="utf-8")
    source = BrowserPageSource(
        source_name="browser-page",
        page_url="https://example.com/dynamic/jobs",
        browser_fetcher=FakeBrowserFetcher(html),
    )

    jobs = asyncio.run(source.fetch_jobs())

    assert len(jobs) == 1
    assert jobs[0].title == "Estagio de Automacao Eletrica"


def test_browser_fetcher_fetch_page_closes_owned_client_and_normalizes_fetch_url(monkeypatch):
    events = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "url": "https://example.com/jobs/3",
                "title": "Vaga dinamica",
                "html": "<html></html>",
            }

    class FakeClient:
        async def post(self, url: str, json: dict):
            events.append(("post", url, json))
            return FakeResponse()

        async def aclose(self) -> None:
            events.append(("close",))

    monkeypatch.setattr("app.utils.browser.build_http_client", lambda: FakeClient())

    fetcher = build_browser_fetcher(base_url="http://localhost:8931/")
    result = asyncio.run(fetcher.fetch_page("https://example.com/jobs/3"))

    assert result.title == "Vaga dinamica"
    assert events == [
        ("post", "http://localhost:8931/fetch", {"url": "https://example.com/jobs/3"}),
        ("close",),
    ]
