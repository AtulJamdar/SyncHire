from fastapi import APIRouter

router = APIRouter(prefix="/admin/scraper-health", tags=["Admin - Scraper Health"])

@router.get("")
def get_health():
    return {"status": "scraper health is good"}
