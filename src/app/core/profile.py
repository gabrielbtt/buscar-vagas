from dataclasses import dataclass


@dataclass(frozen=True)
class JobProfile:
    id: str
    name: str
    active: bool
    required_keywords: tuple[str, ...]
    preferred_keywords: tuple[str, ...]
    blocked_keywords: tuple[str, ...]
    allowed_contract_terms: tuple[str, ...]
    target_locations: tuple[str, ...]
    allow_remote_terms: tuple[str, ...]


def build_initial_profiles() -> list[JobProfile]:
    return [
        JobProfile(
            id="eng-eletrica-bh",
            name="Engenharia Elétrica (BH/Estágio/Trainee)",
            active=True,
            required_keywords=("engenharia eletrica", "projetos eletricos", "automacao"),
            preferred_keywords=(
                "clp",
                "ihm",
                "automacao industrial",
                "painel eletrico",
                "comandos eletricos",
                "plc",
                "hmi",
            ),
            blocked_keywords=("n8n", "marketing", "vendas", "telemarketing", "social media"),
            allowed_contract_terms=("estagio", "estagiario", "internship", "trainee"),
            target_locations=("belo horizonte", "contagem", "betim", "nova lima", "sabara", "santa luzia", "ribeirao das neves", "vespasiano"),
            allow_remote_terms=("remoto", "remote", "home office", "100% remoto"),
        ),
        JobProfile(
            id="default",
            name="Perfil Padrão (Geral)",
            active=False,
            required_keywords=("desenvolvedor", "software", "tecnologia"),
            preferred_keywords=("python", "fastapi", "react", "typescript"),
            blocked_keywords=("vendas", "telemarketing"),
            allowed_contract_terms=("clt", "pj", "estagio"),
            target_locations=("remoto",),
            allow_remote_terms=("remoto", "remote", "home office"),
        )
    ]
