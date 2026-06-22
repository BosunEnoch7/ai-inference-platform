from functools import lru_cache
from hashlib import sha256
from typing import Annotated

from fastapi import Depends, Header, Request
from redis.asyncio import Redis

from app.core.config import Settings, get_settings
from app.services.rate_limit import RedisRateLimiter


@lru_cache
def build_rate_limiter(
    redis_url: str,
    request_limit: int,
    window_seconds: int,
    fail_open: bool,
) -> RedisRateLimiter:
    redis = Redis.from_url(redis_url, decode_responses=True)
    return RedisRateLimiter(
        redis,
        request_limit=request_limit,
        window_seconds=window_seconds,
        fail_open=fail_open,
    )


async def enforce_rate_limit(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    if not settings.rate_limit_enabled:
        return

    client_host = request.client.host if request.client else "unknown"
    identity_source = api_key or client_host
    identity = sha256(identity_source.encode("utf-8")).hexdigest()
    limiter = build_rate_limiter(
        settings.redis_url.get_secret_value(),
        settings.rate_limit_requests,
        settings.rate_limit_window_seconds,
        settings.rate_limit_fail_open,
    )
    await limiter.enforce(identity)
