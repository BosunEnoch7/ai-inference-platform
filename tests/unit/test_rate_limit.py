import pytest
from redis.exceptions import RedisError
from starlette.requests import Request

from app.api import rate_limit as rate_limit_module
from app.core.config import Settings
from app.core.exceptions import ConfigurationError, RateLimitExceededError
from app.services.rate_limit import RedisRateLimiter


class FakeRedis:
    def __init__(
        self,
        result: list[int] | None = None,
        error: RedisError | None = None,
    ) -> None:
        self.result = result or [1, 60]
        self.error = error
        self.keys: list[str] = []

    async def eval(self, script: str, number_of_keys: int, key: str, window: int) -> list[int]:
        self.keys.append(key)
        if self.error:
            raise self.error
        return self.result


def limiter(redis: FakeRedis, *, fail_open: bool = False) -> RedisRateLimiter:
    return RedisRateLimiter(  # type: ignore[arg-type]
        redis,
        request_limit=2,
        window_seconds=60,
        fail_open=fail_open,
    )


@pytest.mark.asyncio
async def test_rate_limiter_allows_request_within_limit() -> None:
    redis = FakeRedis(result=[2, 42])

    await limiter(redis).enforce("identity")

    assert redis.keys[0].startswith("rate-limit:identity:")


@pytest.mark.asyncio
async def test_rate_limiter_rejects_request_above_limit() -> None:
    redis = FakeRedis(result=[3, 42])

    with pytest.raises(RateLimitExceededError) as error:
        await limiter(redis).enforce("identity")

    assert error.value.status_code == 429
    assert error.value.headers["Retry-After"] == "42"


@pytest.mark.asyncio
async def test_rate_limiter_fails_closed_by_default() -> None:
    redis = FakeRedis(error=RedisError("unavailable"))

    with pytest.raises(ConfigurationError) as error:
        await limiter(redis).enforce("identity")

    assert error.value.code == "rate_limiter_unavailable"


@pytest.mark.asyncio
async def test_rate_limiter_can_fail_open() -> None:
    redis = FakeRedis(error=RedisError("unavailable"))

    await limiter(redis, fail_open=True).enforce("identity")


@pytest.mark.asyncio
async def test_api_dependency_hashes_api_key_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    identities: list[str] = []

    class CapturingLimiter:
        async def enforce(self, identity: str) -> None:
            identities.append(identity)

    def limiter_override(*args: object) -> CapturingLimiter:
        return CapturingLimiter()

    monkeypatch.setattr(rate_limit_module, "build_rate_limiter", limiter_override)
    request = Request({"type": "http", "client": ("192.0.2.1", 1234), "headers": []})
    settings = Settings(rate_limit_enabled=True)

    await rate_limit_module.enforce_rate_limit(request, settings, api_key="secret-api-key")

    assert len(identities[0]) == 64
    assert "secret-api-key" not in identities[0]
