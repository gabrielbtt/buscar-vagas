from app.core.filters import matches_contract_type, matches_location
from app.core.profile import build_initial_profiles


def test_matches_belo_horizonte_region():
    profile = build_initial_profiles()[0]
    assert matches_location("Betim, MG", "presencial", profile) is True


def test_matches_remote_jobs_anywhere():
    profile = build_initial_profiles()[0]
    assert matches_location("Curitiba, PR", "100% remoto", profile) is True


def test_rejects_unrelated_contract_type():
    profile = build_initial_profiles()[0]
    assert matches_contract_type("analista pleno", profile) is False
