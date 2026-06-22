from time import time

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.exceptions import ConfigurationError, RateLimitExceededError

RATE_LIMIT_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('TTL', KEYS[1])
return {current, ttl}
"""


class RedisRateLimiter:
    def __init__(
        self,
        redis: Redis,
        *,
        request_limit: int,
        window_seconds: int,
        fail_open: bool,
    ) -> None:
        self.redis = redis
        self.request_limit = request_limit
        self.window_seconds = window_seconds
        self.fail_open = fail_open

    async def enforce(self, identity: str) -> None:
        window = int(time()) // self.window_seconds
        key = f"rate-limit:{identity}:{window}"
        try:
            result = await self.redis.eval(
                RATE_LIMIT_SCRIPT,
                1,
                key,
                self.window_seconds,
            )
        except RedisError as exc:
            if self.fail_open:
                return
            raise ConfigurationError(
                "The rate limiter is unavailable.",
                code="rate_limiter_unavailable",
            ) from exc

        count, ttl = int(result[0]), max(int(result[1]), 1)
        if count > self.request_limit:
            raise RateLimitExceededError(retry_after=ttl)
