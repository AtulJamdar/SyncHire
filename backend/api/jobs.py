from fastapi import APIRouter

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("")
def get_jobs():
    return {"message": "List of jobs", "items": [], "total": 0}

@router.get("/{id}")
def get_job(id: str):
    return {"id": id, "title": "Mock Job", "company": "Mock Company"}
