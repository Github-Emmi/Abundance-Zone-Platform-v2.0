"""
Redis Configuration Module
Upstash Redis client setup for caching and Celery broker
"""

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from app.core.config import settings


# ─── Create Async Redis Connection Pool ─────────────────────────────────────
redis_pool = ConnectionPool.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,  # Optimize for Upstash free tier (500K commands/month)
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
)

# ─── Create Async Redis Client ───────────────────────────────────────────────
redis_client = redis.Redis(connection_pool=redis_pool)


# ─── Redis Helper Functions ──────────────────────────────────────────────────
async def get_redis() -> redis.Redis:
    """
    FastAPI dependency that provides Redis client.

    Usage:
        @router.get("/cached-data")
        async def get_cached_data(redis: Redis = Depends(get_redis)):
            cached = await redis.get("key")
    """
    return redis_client


async def close_redis_connections() -> None:
    """
    Close all Redis connections.
    Called during app shutdown.
    """
    await redis_client.close()
    await redis_pool.disconnect()


# ─── Cache Helper Functions ──────────────────────────────────────────────────
async def set_cache(key: str, value: str, ttl: int | None = None) -> bool:
    """
    Set a value in Redis cache with optional TTL.

    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized)
        ttl: Time to live in seconds (None = no expiration)

    Returns:
        True if successful
    """
    if ttl:
        return await redis_client.setex(key, ttl, value)
    return await redis_client.set(key, value)


async def get_cache(key: str) -> str | None:
    """
    Get a value from Redis cache.

    Args:
        key: Cache key

    Returns:
        Cached value or None if not found
    """
    return await redis_client.get(key)


async def delete_cache(key: str) -> bool:
    """
    Delete a value from Redis cache.

    Args:
        key: Cache key

    Returns:
        True if key was deleted
    """
    return bool(await redis_client.delete(key))


async def invalidate_pattern(pattern: str) -> int:
    """
    Delete all keys matching a pattern.

    Args:
        pattern: Redis key pattern (e.g., "youth:*")

    Returns:
        Number of keys deleted
    """
    keys = []
    async for key in redis_client.scan_iter(match=pattern):
        keys.append(key)

    if keys:
        return await redis_client.delete(*keys)
    return 0


async def increment_counter(key: str, amount: int = 1) -> int:
    """
    Increment a counter in Redis (useful for rate limiting).

    Args:
        key: Counter key
        amount: Increment amount (default: 1)

    Returns:
        New counter value
    """
    return await redis_client.incrby(key, amount)


async def set_expiry(key: str, seconds: int) -> bool:
    """
    Set expiration time on an existing key.

    Args:
        key: Redis key
        seconds: TTL in seconds

    Returns:
        True if expiry was set
    """
    return await redis_client.expire(key, seconds)
