from pathlib import Path

from app.sources.company_pages import parse_company_jobs_html


def test_parse_company_jobs_html_extracts_single_listing():
    html = Path("tests/sources/fixtures/company_page_sample.html").read_text(encoding="utf-8")
    jobs = parse_company_jobs_html(html, source_name="ihm")
    assert len(jobs) == 1
    assert jobs[0].title == "Estagio de Automacao Eletrica"
    assert jobs[0].company == "IHM Stefanini"
