import time
import logging
from fastapi import Request, HTTPException
from core.redis_client import redis

logger = logging.getLogger("rate_limit")

# Define rate limit rules based on 13_SECURITY.md Section 8.2 Table
# Format: (path, method): (key_prefix, limit, window_seconds)
RATE_LIMIT_RULES = {
    ("/api/auth/login", "POST"): ("auth_login", 5, 60),
    ("/api/auth/register", "POST"): ("auth_register", 5, 3600),
    ("/api/auth/forgot-password", "POST"): ("auth_forgot", 3, 3600),
    ("/api/auth/resend-verification", "POST"): ("auth_resend", 3, 3600),
    ("/api/auth/reset-password", "POST"): ("auth_reset", 10, 3600),
    ("/api/jobs", "GET"): ("jobs_list", 120, 60),
    ("/api/telegram/generate-link-code", "POST"): ("telegram_code", 10, 3600),
}

async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method
    rule = None
    
    # Exact match check
    if (path, method) in RATE_LIMIT_RULES:
        rule = RATE_LIMIT_RULES[(path, method)]
    elif path.startswith("/api/jobs/") and method == "GET":
        # Match /api/jobs/{id}
        # Avoid matching /api/jobs/ (covered above) or other nested routes
        parts = path.strip("/").split("/")
        if len(parts) == 3: # e.g. ["api", "jobs", "123"]
            rule = ("job_detail", 120, 60)
    elif path.startswith("/api/admin/companies/") and path.endswith("/run-now") and method == "POST":
        # Match /api/admin/companies/{id}/run-now
        rule = ("admin_run_now", 10, 3600)
        
    if rule:
        key_prefix, limit, window_seconds = rule
        ip = request.client.host if request.client else "unknown"
        # Extract user_id if attached by authentication middleware
        user_id = getattr(request.state, "user", {}).get("id") if hasattr(request.state, "user") else None
        key = f"rl:{key_prefix}:{user_id or ip}"
        
        now = time.time()
        window_start = now - window_seconds
        
        try:
            pipe = redis.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)     # Remove old entries
            pipe.zadd(key, {str(now): now})                  # Add current request
            pipe.zcard(key)                                  # Count requests in window
            pipe.expire(key, window_seconds + 1)
            results = await pipe.execute()
            
            count = results[2]
            if count > limit:
                logger.warning(f"Rate limit exceeded for key={key} on {path} ({count}/{limit})")
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests",
                    headers={"Retry-After": str(window_seconds)}
                )
        except HTTPException as he:
            raise he
        except Exception as e:
            # Graceful degradation: log the error, don't fail the request if redis is down
            logger.error(f"Redis rate limiting connection failed: {e}")

    response = await call_next(request)
    return response
