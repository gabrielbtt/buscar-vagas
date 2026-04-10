from dataclasses import dataclass


@dataclass(frozen=True)
class JobProfile:
    required_keywords: tuple[str, ...]
    preferred_keywords: tuple[str, ...]
    blocked_keywords: tuple[str, ...]
    allowed_contract_terms: tuple[str, ...]
    target_locations: tuple[str, ...]
    allow_remote_terms: tuple[str, ...]


def build_default_profile() -> JobProfile:
    return JobProfile(
        required_keywords=("engenharia eletrica", "projetos eletricos", "automacao"),
        preferred_keywords=(
            "clp",
            "ihm",
            "automacao industrial",
            "painel eletrico",
            "comandos eletricos",
        ),
        blocked_keywords=("n8n", "marketing", "vendas", "telemarketing"),
        allowed_contract_terms=("estagio", "estagiario", "internship", "trainee"),
        target_locations=("belo horizonte", "contagem", "betim", "nova lima"),
        allow_remote_terms=("remoto", "remote", "home office", "100% remoto"),
    )
