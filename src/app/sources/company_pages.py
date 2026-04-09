from datetime import datetime, timezone

from app.schemas.job import NormalizedJob
from app.utils.html import parse_html


def parse_company_jobs_html(html: str, source_name: str) -> list[NormalizedJob]:
    soup = parse_html(html)
    jobs: list[NormalizedJob] = []
    for card in soup.select("article.job-card"):
        jobs.append(
            NormalizedJob(
                source_name=source_name,
                title=card.select_one("h2").get_text(strip=True),
                company=card.select_one(".company").get_text(strip=True),
                location=card.select_one(".location").get_text(strip=True),
                work_model="Presencial",
                employment_type="Estagio",
                url=card.select_one("a")["href"],
                description_text=card.select_one("p").get_text(strip=True),
                posted_at=datetime.now(timezone.utc),
            )
        )
    return jobs
