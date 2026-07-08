from fastapi import APIRouter

router = APIRouter(prefix="/admin/companies", tags=["Admin - Companies"])

@router.get("/status")
def status():
    return {"status": "admin companies router working"}

@router.post("/{id}/run-now")
def run_now(id: str):
    return {"status": f"Scraper run triggered for company {id}"}
