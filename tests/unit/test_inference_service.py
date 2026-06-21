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


@pytest.mark.asyncio
async def test_provider_timeout_is_translated() -> None:
    service = InferenceService(SlowProvider(), timeout_seconds=0.001)
    with pytest.raises(InferenceError) as error:
        await service.infer(InferenceRequest(prompt="hello"))
    assert error.value.code == "provider_timeout"
    assert error.value.status_code == 504

