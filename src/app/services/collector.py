from app.schemas.job import NormalizedJob
from app.sources.browser_pages import BrowserPageSource
from app.sources.company_pages import CompanyPageSource
from app.sources.gupy import GupySource
from app.utils.browser import build_browser_fetcher


class StaticCollector:
    def __init__(self, jobs: list[NormalizedJob]):
        self._jobs = jobs

    async def fetch_all(self) -> list[NormalizedJob]:
        return self._jobs


class MultiSourceCollector:
    def __init__(self, sources):
        self._sources = sources

    @classmethod
    def build_from_settings(cls, settings, client_factory):
        sources = []
        browser_fetcher = None
        playwright_url = getattr(settings, "playwright_mcp_url", "")
        if playwright_url:
            browser_fetcher = build_browser_fetcher(playwright_url)

        # Se houver perfis configurados, cria fontes para cada perfil ativo
        profiles = getattr(settings, "profiles", [])
        for profile in profiles:
            if not getattr(profile, "active", False):
                continue

            # Para cada perfil ativo, podemos adicionar fontes específicas ou genéricas.
            # No caso da Gupy, podemos gerar uma URL de busca baseada no nome do perfil ou keywords.
            search_query = "+".join(profile.required_keywords).replace(" ", "+")
            gupy_search_url = f"https://portal.gupy.io/job-search/term={search_query}"
            
            if browser_fetcher:
                sources.append(
                    GupySource(
                        source_name=f"gupy-{profile.id}",
                        page_url=gupy_search_url,
                        browser_fetcher=browser_fetcher,
                        profile_name=profile.name
                    )
                )

        # Fontes legadas/gerais (se ativadas)
        if getattr(settings, "company_page_source_enabled", False) and getattr(settings, "company_page_source_url", ""):
            sources.append(
                CompanyPageSource(
                    source_name="company-page",
                    page_url=settings.company_page_source_url,
                    client_factory=client_factory,
                    browser_fetcher=browser_fetcher,
                )
            )
        
        return cls(sources)

    async def fetch_all(self) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        for source in self._sources:
            try:
                jobs.extend(await source.fetch_jobs())
            except Exception as e:
                # Logar erro sem interromper as outras fontes
                print(f"Erro ao buscar na fonte {source.source_name}: {e}")
        return jobs
