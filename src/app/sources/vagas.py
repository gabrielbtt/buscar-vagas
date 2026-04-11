import asyncio
from app.schemas.job import NormalizedJob
from app.sources.base import JobSource
from app.utils.html import parse_job_elements
import httpx


class VagasSource(JobSource):
    def __init__(
        self,
        source_name: str,
        page_url: str,
        client_factory: callable,
        profile_name: str = ""
    ):
        self.source_name = source_name
        self._page_url = page_url
        self._client_factory = client_factory
        self._profile_name = profile_name

    async def fetch_jobs(self) -> list[NormalizedJob]:
        try:
            async with self._client_factory() as client:
                # Vagas.com às vezes bloqueia bots simples, pode ser necessário um User-Agent.
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = await client.get(self._page_url, headers=headers)
                if response.status_code != 200:
                    print(f"Erro ao buscar no Vagas.com: {response.status_code}")
                    return []
                
                html = response.text
                
                # Seletores comuns no Vagas.com
                jobs = parse_job_elements(
                    html,
                    source_name=f"Vagas.com ({self._profile_name})" if self._profile_name else "Vagas.com",
                    item_selector="li.vaga",
                    title_selector="h2.cargo, a.link-detalhes-vaga",
                    location_selector="span.vaga-local",
                    company_selector="span.empr",
                    url_selector="a.link-detalhes-vaga"
                )
                
                # Vagas.com URLs as vezes são relativas
                for job in jobs:
                    if job.url and str(job.url).startswith('/'):
                        job.url = f"https://www.vagas.com.br{job.url}"
                
                return jobs
        except Exception as e:
            print(f"Erro na fonte Vagas.com {self.source_name}: {e}")
            return []
