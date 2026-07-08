from fastapi import APIRouter

router = APIRouter(prefix="/saved-jobs", tags=["Saved Jobs"])

@router.get("/status")
def status():
    return {"status": "saved jobs router working"}
