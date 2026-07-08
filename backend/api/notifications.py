from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/status")
def status():
    return {"status": "notifications router working"}
