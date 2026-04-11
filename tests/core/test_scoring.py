from app.core.profile import build_initial_profiles
from app.core.scoring import score_job
from app.schemas.job import NormalizedJob


def test_scores_industrial_automation_job_higher():
    profile = build_initial_profiles()[0]
    job = NormalizedJob(
        source_name="company",
        title="Estagio em Automacao Industrial com CLP e IHM",
        company="IHM Stefanini",
        location="Belo Horizonte, MG",
        work_model="Presencial",
        employment_type="Estagio",
        url="https://example.com/jobs/1",
        description_text="Atuacao com CLP, IHM, comandos eletricos e projetos.",
    )
    assert score_job(job, profile) >= 0.8
