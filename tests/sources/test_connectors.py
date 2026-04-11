from types import SimpleNamespace

from app.services.collector import MultiSourceCollector


def test_multi_source_collector_passes_browser_fetcher_to_company_page_source(monkeypatch):
    captured = {}

    class FakeSource:
        def __init__(self, source_name, page_url, client_factory, browser_fetcher=None):
            captured["source_name"] = source_name
            captured["page_url"] = page_url
            captured["client_factory"] = client_factory
            captured["browser_fetcher"] = browser_fetcher

    settings = SimpleNamespace(
        profiles=[],
        company_page_source_enabled=True,
        company_page_source_url="https://example.com/company/jobs",
        playwright_mcp_url="http://localhost:8931",
    )

    monkeypatch.setattr("app.services.collector.CompanyPageSource", FakeSource)
    monkeypatch.setattr("app.services.collector.build_browser_fetcher", lambda base_url: "browser-fetcher")

    collector = MultiSourceCollector.build_from_settings(settings, client_factory=lambda: "client")

    assert collector is not None
    assert captured == {
        "source_name": "company-page",
        "page_url": "https://example.com/company/jobs",
        "client_factory": captured["client_factory"],
        "browser_fetcher": "browser-fetcher",
    }


def test_multi_source_collector_adds_browser_page_source_when_enabled(monkeypatch):
    created_sources = []

    class FakeGupySource:
        def __init__(self, **kwargs):
            created_sources.append(("gupy", kwargs))

    class FakeCompanySource:
        def __init__(self, **kwargs):
            created_sources.append(("company", kwargs))

    class FakeBrowserSource:
        def __init__(self, **kwargs):
            created_sources.append(("browser", kwargs))

    profile = SimpleNamespace(
        id=1,
        name="Backend",
        active=True,
        required_keywords=["python", "fastapi"]
    )

    settings = SimpleNamespace(
        profiles=[profile],
        company_page_source_enabled=True,
        company_page_source_url="https://example.com/company/jobs",
        browser_page_source_enabled=True,
        browser_page_source_url="https://example.com/dynamic/jobs",
        playwright_mcp_url="http://localhost:8931",
    )

    monkeypatch.setattr("app.services.collector.GupySource", FakeGupySource)
    monkeypatch.setattr("app.services.collector.CompanyPageSource", FakeCompanySource)
    monkeypatch.setattr("app.services.collector.BrowserPageSource", FakeBrowserSource)
    monkeypatch.setattr("app.services.collector.build_browser_fetcher", lambda base_url: "browser-fetcher")

    MultiSourceCollector.build_from_settings(settings, client_factory=lambda: "client")

    assert created_sources == [
        (
            "gupy",
            {
                "source_name": "gupy-1",
                "page_url": "https://portal.gupy.io/job-search/term=python+fastapi",
                "browser_fetcher": "browser-fetcher",
                "profile_name": "Backend",
            },
        ),
        (
            "company",
            {
                "source_name": "company-page",
                "page_url": "https://example.com/company/jobs",
                "client_factory": created_sources[1][1]["client_factory"],
                "browser_fetcher": "browser-fetcher",
            },
        ),
    ]


def test_multi_source_collector_skips_browser_page_source_without_mcp_url(monkeypatch):
    created_sources = []

    class FakeCompanySource:
        def __init__(self, **kwargs):
            created_sources.append(("company", kwargs))

    class FakeBrowserSource:
        def __init__(self, **kwargs):
            created_sources.append(("browser", kwargs))

    settings = SimpleNamespace(
        profiles=[],
        company_page_source_enabled=True,
        company_page_source_url="https://example.com/company/jobs",
        browser_page_source_enabled=True,
        browser_page_source_url="https://example.com/dynamic/jobs",
        playwright_mcp_url="",
    )

    monkeypatch.setattr("app.services.collector.CompanyPageSource", FakeCompanySource)
    monkeypatch.setattr("app.services.collector.BrowserPageSource", FakeBrowserSource)

    MultiSourceCollector.build_from_settings(settings, client_factory=lambda: "client")

    assert [kind for kind, _ in created_sources] == ["company"]
