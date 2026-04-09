from app.schemas.job import NormalizedJob
from app.services.run_jobs import process_job_batch


def test_process_job_batch_returns_only_new_matches():
    jobs = [
        NormalizedJob(
            source_name="company",
            title="Estagio em Automacao Industrial",
            company="IHM Stefanini",
            location="Belo Horizonte, MG",
            work_model="Presencial",
            employment_type="Estagio",
            url="https://example.com/jobs/1",
            description_text="CLP e IHM",
        )
    ]
    first = process_job_batch(jobs)
    second = process_job_batch(jobs)
    assert len(first) == 1
    assert second == []
