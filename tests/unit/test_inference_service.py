import asyncio

import pytest

from app.core.exceptions import InferenceError
from app.models.inference import InferenceRequest, ProviderResult
from app.providers.base import LLMProvider
from app.services.inference import InferenceService


class SlowProvider(LLMProvider):
    name = "slow"

    async def generate(self, request: InferenceRequest) -> ProviderResult:
        await asyncio.sleep(0.05)
        return ProviderResult(text=request.prompt, model="slow-model")


class FailingProvider(LLMProvider):
    name = "failing"

    def __init__(self, error: Exception) -> None:
        self.error = error

    async def generate(self, request: InferenceRequest) -> ProviderResult:
        raise self.error


@pytest.mark.asyncio
async def test_provider_timeout_is_translated() -> None:
    service = InferenceService(SlowProvider(), timeout_seconds=0.001)
    with pytest.raises(InferenceError) as error:
        await service.infer(InferenceRequest(prompt="hello"))
    assert error.value.code == "provider_timeout"
    assert error.value.status_code == 504


@pytest.mark.asyncio
async def test_provider_error_is_preserved() -> None:
    provider_error = InferenceError(
        "Provider unavailable.",
        code="provider_unavailable",
        status_code=503,
    )
    service = InferenceService(FailingProvider(provider_error), timeout_seconds=1)

    with pytest.raises(InferenceError) as error:
        await service.infer(InferenceRequest(prompt="hello"))

    assert error.value is provider_error


@pytest.mark.asyncio
async def test_unexpected_provider_error_is_translated() -> None:
    service = InferenceService(FailingProvider(ValueError("boom")), timeout_seconds=1)

    with pytest.raises(InferenceError) as error:
        await service.infer(InferenceRequest(prompt="hello"))

    assert error.value.code == "inference_failed"
    assert error.value.status_code == 502
