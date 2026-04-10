from app.core.profile import build_default_profile


def test_default_profile_contains_target_domains():
    profile = build_default_profile()

    assert "engenharia eletrica" in profile.required_keywords
    assert "clp" in profile.preferred_keywords
    assert "ihm" in profile.preferred_keywords
    assert "trainee" in profile.allowed_contract_terms


def test_default_profile_allows_internship_and_trainee_contract_terms():
    profile = build_default_profile()

    assert "estagio" in profile.allowed_contract_terms
    assert "estagiario" in profile.allowed_contract_terms
    assert "internship" in profile.allowed_contract_terms
    assert "trainee" in profile.allowed_contract_terms


def test_default_profile_targets_task_1_locations_and_remote_terms():
    profile = build_default_profile()

    assert profile.target_locations == (
        "belo horizonte",
        "contagem",
        "betim",
        "nova lima",
    )
    assert "100% remoto" in profile.allow_remote_terms


def test_default_profile_prefers_electrical_projects_and_industrial_automation():
    profile = build_default_profile()

    assert "projetos eletricos" in profile.required_keywords
    assert "automacao industrial" in profile.preferred_keywords
    assert "clp" in profile.preferred_keywords
    assert "ihm" in profile.preferred_keywords
