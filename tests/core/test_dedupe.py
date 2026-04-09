from app.core.dedupe import build_job_fingerprint


def test_build_job_fingerprint_is_stable():
    value = build_job_fingerprint("IHM Stefanini", "Estagio em Automacao", "https://example.com/jobs/1?ref=abc")
    assert value == build_job_fingerprint("IHM Stefanini", "Estagio em Automacao", "https://example.com/jobs/1")
