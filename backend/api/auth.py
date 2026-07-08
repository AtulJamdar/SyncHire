from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/status")
def status():
    return {"status": "auth router working"}
