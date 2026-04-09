from app.core.profile import build_default_profile


def test_default_profile_contains_target_domains():
    profile = build_default_profile()

    assert "engenharia eletrica" in profile.required_keywords
    assert "clp" in profile.preferred_keywords
    assert "ihm" in profile.preferred_keywords
    assert "trainee" in profile.allowed_contract_terms
