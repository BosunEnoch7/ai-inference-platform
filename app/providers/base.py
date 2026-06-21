from abc import ABC, abstractmethod

from app.models.inference import InferenceRequest, ProviderResult


class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def generate(self, request: InferenceRequest) -> ProviderResult:
        """Generate text for a validated inference request."""

