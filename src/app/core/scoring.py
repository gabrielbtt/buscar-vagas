from app.core.filters import normalize_text
from app.core.profile import JobProfile
from app.schemas.job import NormalizedJob


def score_job(job: NormalizedJob, profile: JobProfile) -> float:
    haystack = normalize_text(f"{job.title} {job.description_text}")
    score = 0.0
    if any(term in haystack for term in profile.required_keywords):
        score += 0.4
    preferred_hits = sum(1 for term in profile.preferred_keywords if term in haystack)
    score += min(preferred_hits * 0.15, 0.45)
    if any(term in haystack for term in profile.blocked_keywords):
        score -= 0.5
    if "remoto" in normalize_text(job.work_model) or "belo horizonte" in normalize_text(job.location):
        score += 0.15
    return max(0.0, min(score, 1.0))
