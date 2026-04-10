from app.core.profile import build_default_profile
from app.db.models import JobListing
from app.db.repositories import mark_jobs_as_notified, should_notify_for_job
from app.schemas.job import NormalizedJob
from app.services.matcher import MatchedJob, match_jobs


def test_should_notify_until_job_is_marked_notified(session):
    matched_job = MatchedJob(
        job=NormalizedJob(
            source_name="company",
            title="Estagio em Automacao Industrial",
            company="IHM Stefanini",
            location="Belo Horizonte, MG",
            work_model="Presencial",
            employment_type="Estagio",
            url="https://example.com/jobs/1",
            description_text="CLP e IHM",
        ),
        fingerprint="abc123",
        score=0.91,
    )

    assert should_notify_for_job(session, matched_job) is True

    saved = session.query(JobListing).filter_by(fingerprint="abc123").one()
    assert saved.company == "IHM Stefanini"
    assert saved.title == "Estagio em Automacao Industrial"
    assert saved.score == 0.91
    assert saved.notified is False

    assert should_notify_for_job(session, matched_job) is True

    mark_jobs_as_notified(session, [matched_job.fingerprint])

    assert should_notify_for_job(session, matched_job) is False


def test_match_jobs_returns_only_relevant_jobs():
    profile = build_default_profile()
    jobs = [
        NormalizedJob(
            source_name="a",
            title="Estagio em Automacao Industrial",
            company="A",
            location="Belo Horizonte, MG",
            work_model="Presencial",
            employment_type="Estagio",
            url="https://example.com/jobs/1",
            description_text="CLP e IHM",
        ),
        NormalizedJob(
            source_name="b",
            title="Estagio em Marketing",
            company="B",
            location="Belo Horizonte, MG",
            work_model="Presencial",
            employment_type="Estagio",
            url="https://example.com/jobs/2",
            description_text="Midias sociais",
        ),
    ]
    matched = match_jobs(jobs, profile, min_score=0.6)
    assert len(matched) == 1
    assert matched[0].job.company == "A"
