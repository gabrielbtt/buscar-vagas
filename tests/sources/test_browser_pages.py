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
