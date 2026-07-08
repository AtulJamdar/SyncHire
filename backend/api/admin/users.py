from fastapi import APIRouter

router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])

@router.get("/status")
def status():
    return {"status": "admin users router working"}
