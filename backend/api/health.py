from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from core.database import SessionLocal
from core.redis_client import check_redis_health

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """
    Liveness and readiness check.
    Pings both the primary PostgreSQL database and Redis cache.
    Returns 200 OK if both are connected, or 503 degraded if either is down.
    """
    checks = {
        "database": "unknown",
        "redis": "unknown",
    }
    
    # 1. Database connectivity check
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception:
        checks["database"] = "disconnected"

    # 2. Redis connectivity check
    redis_healthy = await check_redis_health()
    checks["redis"] = "connected" if redis_healthy else "disconnected"

    # Calculate status and status code
    status = "ok" if all(v == "connected" for v in checks.values()) else "degraded"
    status_code = 200 if status == "ok" else 503

    return JSONResponse(
        content={
            "status": status,
            **checks,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        status_code=status_code
    )
