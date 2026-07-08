from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    
    # Required Core Infrastructure Settings
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET_KEY: str
    NEXTAUTH_SECRET: str

    # Third Party Credentials / Configurations
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    STRONG_MODEL: str = "llama-3.3-70b-versatile"
    FAST_MODEL: str = "llama-3.1-8b-instant"
    
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_SECRET: Optional[str] = None
    ADMIN_TELEGRAM_CHAT_ID: Optional[str] = None
    
    RESEND_API_KEY: Optional[str] = None
    EMAIL_FROM_ADDRESS: str = "alerts@jobfinderai.com"
    EMAIL_FROM_NAME: str = "Job Finder AI"
    
    R2_ENDPOINT_URL: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    R2_BUCKET_NAME: str = "jobfinderai-resumes"
    
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"
    NEXTAUTH_URL: str = "http://localhost:3000"
    
    SCRAPE_BATCH_SIZE: int = 20
    MAX_JOBS_PER_COMPANY: int = 50
    SCRAPE_INTERVAL_MINUTES: int = 15
    
    SENTRY_DSN: Optional[str] = None

    # Load from .env file at the workspace / application root
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),  # check parent first, then current folder
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("DATABASE_URL", "REDIS_URL", "JWT_SECRET_KEY", "NEXTAUTH_SECRET")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or v.strip() in ("", "...", "sk-...", "sk-ant-..."):
            raise ValueError("Field cannot be empty or contain placeholder values.")
        return v

# Instantiate settings to trigger validation on startup.
# This ensures a fail-fast behavior if required variables are missing.
try:
    settings = Settings()
except Exception as e:
    import sys
    print(f"CRITICAL CONFIGURATION ERROR: {e}", file=sys.stderr)
    sys.exit(1)
