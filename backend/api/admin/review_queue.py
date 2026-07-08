from fastapi import APIRouter

router = APIRouter(prefix="/admin/review-queue", tags=["Admin - Review Queue"])

@router.get("/status")
def status():
    return {"status": "admin review queue router working"}
