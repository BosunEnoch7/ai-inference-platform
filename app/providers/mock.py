from app.models.inference import InferenceRequest, ProviderResult
from app.providers.base import LLMProvider


class MockLLMProvider(LLMProvider):
    name = "mock"

    async def generate(self, request: InferenceRequest) -> ProviderResult:
        return ProviderResult(
            text=f"Mock response: {request.prompt}",
            model="mock-model-v1",
        )

