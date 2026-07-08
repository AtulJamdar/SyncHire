from fastapi import APIRouter

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/status")
def status():
    return {"status": "profile router working"}
