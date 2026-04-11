from app.core.profile import build_initial_profiles


def test_default_profile_contains_target_domains():
    profile = build_initial_profiles()[0]

    assert "engenharia eletrica" in profile.required_keywords
    assert "clp" in profile.preferred_keywords
    assert "ihm" in profile.preferred_keywords
    assert "trainee" in profile.allowed_contract_terms


def test_default_profile_allows_internship_and_trainee_contract_terms():
    profile = build_initial_profiles()[0]

    assert "estagio" in profile.allowed_contract_terms
    assert "estagiario" in profile.allowed_contract_terms
    assert "internship" in profile.allowed_contract_terms
    assert "trainee" in profile.allowed_contract_terms


def test_default_profile_targets_task_1_locations_and_remote_terms():
    profile = build_initial_profiles()[0]

    assert "belo horizonte" in profile.target_locations
    assert "contagem" in profile.target_locations
    assert "betim" in profile.target_locations
    assert "nova lima" in profile.target_locations
    assert "100% remoto" in profile.allow_remote_terms


def test_default_profile_prefers_electrical_projects_and_industrial_automation():
    profile = build_initial_profiles()[0]

    assert "projetos eletricos" in profile.required_keywords
    assert "automacao industrial" in profile.preferred_keywords
    assert "clp" in profile.preferred_keywords
    assert "ihm" in profile.preferred_keywords
