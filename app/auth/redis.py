# app/auth/redis.py
"""Utility helpers for optional Redis-based token blacklisting."""

from app.core.config import get_settings

try:
    import aioredis  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    aioredis = None

settings = get_settings()


async def get_redis():
    """Return a cached Redis client when aioredis is available."""
    if aioredis is None:
        return None

    if not hasattr(get_redis, "redis"):
        get_redis.redis = await aioredis.from_url(  # type: ignore[attr-defined]
            settings.REDIS_URL or "redis://localhost"
        )
    return getattr(get_redis, "redis", None)


async def add_to_blacklist(jti: str, exp: int) -> None:
    """Add a token's JTI to the blacklist when Redis support is available."""
    redis = await get_redis()
    if redis is None:
        return
    await redis.set(f"blacklist:{jti}", "1", ex=exp)


async def is_blacklisted(jti: str) -> bool:
    """Check whether a token is blacklisted, defaulting to False without Redis."""
    redis = await get_redis()
    if redis is None:
        return False
    return await redis.exists(f"blacklist:{jti}")