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
    def __init__(self, sources, browser_fetcher=None):
        self._sources = sources
        self._browser_fetcher = browser_fetcher

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

            search_terms = [kw.strip().replace(" ", "+") for kw in profile.required_keywords if kw.strip()]
            search_query = "+".join(search_terms)

            if search_query:
                # Gupy via Browser/Playwright
                if getattr(profile, "use_gupy", True) and browser_fetcher:
                    gupy_search_url = f"https://portal.gupy.io/job-search/term={search_query}"
                    sources.append(
                        GupySource(
                            source_name=f"gupy-{profile.id}",
                            page_url=gupy_search_url,
                            browser_fetcher=browser_fetcher,
                            profile_name=profile.name,
                        )
                    )

                # Suporte para Vagas.com (Novo)
                if getattr(profile, "use_vagas", False):
                    from app.sources.vagas import VagasSource

                    vagas_search_url = f"https://www.vagas.com.br/vagas-de-{search_query}"
                    sources.append(
                        VagasSource(
                            source_name=f"vagas-{profile.id}",
                            page_url=vagas_search_url,
                            client_factory=client_factory,
                            profile_name=profile.name,
                        )
                    )

            # Adicionar fontes personalizadas do perfil
            for url in getattr(profile, "custom_sources", []):
                if url.strip():
                    sources.append(
                        CompanyPageSource(
                            source_name=f"manual-{profile.id}",
                            page_url=url.strip(),
                            client_factory=client_factory,
                            browser_fetcher=browser_fetcher,
                        )
                    )

        # Fontes legadas/gerais (se ativadas)
        for index, url in enumerate(getattr(settings, "global_sources", []), start=1):
            if not url:
                continue
            sources.append(
                CompanyPageSource(
                    source_name=f"global-{index}",
                    page_url=url.strip(),
                    client_factory=client_factory,
                    browser_fetcher=browser_fetcher,
                )
            )

        if getattr(settings, "company_page_source_enabled", False) and getattr(settings, "company_page_source_url", ""):
            sources.append(
                CompanyPageSource(
                    source_name="company-page",
                    page_url=settings.company_page_source_url,
                    client_factory=client_factory,
                    browser_fetcher=browser_fetcher,
                )
            )

        if (
            browser_fetcher
            and getattr(settings, "browser_page_source_enabled", False)
            and getattr(settings, "browser_page_source_url", "")
        ):
            sources.append(
                BrowserPageSource(
                    source_name="browser-page",
                    page_url=settings.browser_page_source_url,
                    browser_fetcher=browser_fetcher,
                )
            )
        
        return cls(sources, browser_fetcher)

    async def fetch_all(self) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        for source in self._sources:
            try:
                jobs.extend(await source.fetch_jobs())
            except Exception as e:
                # Logar erro sem interromper as outras fontes
                print(f"Erro ao buscar na fonte {source.source_name}: {e}")
        
        if self._browser_fetcher:
            await self._browser_fetcher.aclose()
            
        return jobs
