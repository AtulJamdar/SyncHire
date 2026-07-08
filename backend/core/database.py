import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import settings

# Setup logging
logger = logging.getLogger("database")
logging.basicConfig(level=logging.INFO)

# Create Async Engine
# We use settings.DATABASE_URL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

# Async Session Factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# get_db Dependency
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# wait_for_db function
async def wait_for_db(max_attempts: int = 30):
    logger.info("Waiting for database connection...")
    for attempt in range(max_attempts):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully.")
            return
        except Exception as e:
            logger.warning(f"Database not ready (attempt {attempt + 1}/{max_attempts}): {e}")
            await asyncio.sleep(2)
    raise RuntimeError("Could not connect to database after 60 seconds")
