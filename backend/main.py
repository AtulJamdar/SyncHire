from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from core.database import wait_for_db
from core.logging import setup_logging
from middleware.security_headers import security_headers_middleware
from middleware.logging_middleware import logging_middleware
from middleware.rate_limit_middleware import rate_limit_middleware

# Initialize structured logging before other services start
setup_logging()

# Import routers
from api import auth, profile, jobs, saved_jobs, notifications, health
from api.admin import companies, scraper_health, review_queue, users
from api.webhooks import telegram

app = FastAPI(
    title="Job Finder AI API",
    description="Backend API for Job Finder AI",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Note on Middleware Execution Order in FastAPI/Starlette:
# Middlewares are executed in the reverse order of registration (stack: Last-In, First-Out).
# Outermost (runs first) -> Innermost (runs last, closest to route handler).
#
# Registering logging_middleware last makes it the outermost wrapper, ensuring
# that every request gets a trace_id assigned before CORS, security headers, or
# rate limits are processed, and that any exceptions thrown by downstream middlewares
# are caught and logged with the request's trace_id.

# 1. Innermost: Rate Limiting
app.middleware("http")(rate_limit_middleware)

# 2. Security Headers
app.middleware("http")(security_headers_middleware)

# 3. CORS Middleware (built-in)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this using settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Outermost: Logging & Request Tracing (creates trace_id)
app.middleware("http")(logging_middleware)


# Startup Event
@app.on_event("startup")
async def startup_event():
    # Run the database connection retry loop
    await wait_for_db()


# Base / Health endpoints
app.include_router(health.router)


# Register all API routers
app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(saved_jobs.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(scraper_health.router, prefix="/api")
app.include_router(review_queue.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(telegram.router, prefix="/api")
