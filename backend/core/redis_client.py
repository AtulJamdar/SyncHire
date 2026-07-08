import logging
import redis.asyncio as aioredis
from config import settings

logger = logging.getLogger("redis_client")

# Create connection pool and client
pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=50  # Limit pool size for resource management
)
redis_client = aioredis.Redis(connection_pool=pool)
redis = redis_client  # Alias for consistency

async def check_redis_health() -> bool:
    """
    Pings the Redis server to verify the connection is active and healthy.
    Returns True if healthy, False if there is any connection error.
    """
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False
