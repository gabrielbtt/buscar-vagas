from fastapi import APIRouter

router = APIRouter(prefix="/admin")


@router.get("/jobs/recent")
def recent_jobs() -> dict[str, list]:
    return {"items": []}
