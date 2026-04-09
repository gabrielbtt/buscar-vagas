from dataclasses import dataclass

from app.core.dedupe import build_job_fingerprint
from app.core.filters import matches_contract_type, matches_location
from app.core.profile import JobProfile
from app.core.scoring import score_job
from app.schemas.job import NormalizedJob


@dataclass(frozen=True)
class MatchedJob:
    job: NormalizedJob
    fingerprint: str
    score: float


def match_jobs(jobs: list[NormalizedJob], profile: JobProfile, min_score: float) -> list[MatchedJob]:
    matched: list[MatchedJob] = []
    for job in jobs:
        if not matches_contract_type(f"{job.title} {job.employment_type}", profile):
            continue
        if not matches_location(job.location, job.work_model, profile):
            continue
        score = score_job(job, profile)
        if score < min_score:
            continue
        matched.append(
            MatchedJob(
                job=job,
                fingerprint=build_job_fingerprint(job.company, job.title, str(job.url)),
                score=score,
            )
        )
    return matched
