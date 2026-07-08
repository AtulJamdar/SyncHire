from fastapi import APIRouter

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/telegram")
def telegram_webhook(payload: dict):
    return {"status": "success", "message": "Webhook payload received"}
