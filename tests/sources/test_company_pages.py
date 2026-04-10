from pathlib import Path
import asyncio

from app.sources.company_pages import CompanyPageSource, parse_company_jobs_html


def test_parse_company_jobs_html_extracts_single_listing():
    html = Path("tests/sources/fixtures/company_page_sample.html").read_text(encoding="utf-8")
    jobs = parse_company_jobs_html(html, source_name="ihm")
    assert len(jobs) == 1
    assert jobs[0].title == "Estagio de Automacao Eletrica"
    assert jobs[0].company == "IHM Stefanini"


def test_company_page_source_uses_browser_fallback_when_http_page_has_no_jobs():
    class FakeResponse:
        text = "<html><body><p>sem vagas</p></body></html>"

        def raise_for_status(self) -> None:
            return None

    class FakeClient:
        async def get(self, url: str):
            return FakeResponse()

        async def aclose(self) -> None:
            return None

    class FakeBrowserFetcher:
        def __init__(self, html: str):
            self.html = html
            self.calls = []

        async def fetch_page(self, url: str):
            self.calls.append(url)
            return type("Page", (), {"html": self.html})()

    fallback_html = Path("tests/sources/fixtures/company_page_sample.html").read_text(encoding="utf-8")
    browser_fetcher = FakeBrowserFetcher(fallback_html)
    source = CompanyPageSource(
        source_name="ihm",
        page_url="https://example.com/jobs",
        client_factory=lambda: FakeClient(),
        browser_fetcher=browser_fetcher,
    )

    jobs = asyncio.run(source.fetch_jobs())

    assert len(jobs) == 1
    assert browser_fetcher.calls == ["https://example.com/jobs"]


def test_company_page_source_uses_browser_fallback_when_http_request_fails():
    class FakeClient:
        async def get(self, url: str):
            raise RuntimeError("http failed")

        async def aclose(self) -> None:
            return None

    class FakeBrowserFetcher:
        def __init__(self, html: str):
            self.html = html
            self.calls = []

        async def fetch_page(self, url: str):
            self.calls.append(url)
            return type("Page", (), {"html": self.html})()

    fallback_html = Path("tests/sources/fixtures/company_page_sample.html").read_text(encoding="utf-8")
    browser_fetcher = FakeBrowserFetcher(fallback_html)
    source = CompanyPageSource(
        source_name="ihm",
        page_url="https://example.com/jobs",
        client_factory=lambda: FakeClient(),
        browser_fetcher=browser_fetcher,
    )

    jobs = asyncio.run(source.fetch_jobs())

    assert len(jobs) == 1
    assert browser_fetcher.calls == ["https://example.com/jobs"]
