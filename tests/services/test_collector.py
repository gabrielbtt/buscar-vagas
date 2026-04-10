import asyncio
from pathlib import Path
from types import SimpleNamespace

from app.schemas.job import NormalizedJob
from app.services.collector import MultiSourceCollector, StaticCollector


def test_static_collector_fetches_all_jobs():
    jobs = [
        NormalizedJob(
            source_name="company-page",
            title="Estagio em Engenharia Eletrica",
            company="Empresa X",
            location="Belo Horizonte, MG",
            work_model="Presencial",
            employment_type="Estagio",
            url="https://example.com/job/1",
            description_text="engenharia eletrica clp ihm",
        )
    ]

    collector = StaticCollector(jobs)

    assert asyncio.run(collector.fetch_all()) == jobs


def test_multi_source_collector_builds_runtime_sources_from_settings():
    html = Path("tests/sources/fixtures/company_page_sample.html").read_text(encoding="utf-8")

    class FakeResponse:
        def __init__(self, text: str):
            self.text = text

        def raise_for_status(self) -> None:
            return None

    class FakeClient:
        async def get(self, url: str):
            assert url == "https://example.com/company/jobs"
            return FakeResponse(html)

    settings = SimpleNamespace(
        company_page_source_enabled=True,
        company_page_source_url="https://example.com/company/jobs",
    )

    collector = MultiSourceCollector.build_from_settings(settings, lambda: FakeClient())
    jobs = asyncio.run(collector.fetch_all())

    assert len(jobs) == 1
    assert jobs[0].title == "Estagio de Automacao Eletrica"
