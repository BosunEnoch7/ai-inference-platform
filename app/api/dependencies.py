from functools import lru_cache

from app.core.config import get_settings
from app.providers.base import LLMProvider
from app.providers.mock import MockLLMProvider
from app.services.inference import InferenceService


@lru_cache
def get_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider == "mock":
        return MockLLMProvider()
    raise RuntimeError(f"Unsupported LLM provider: {settings.llm_provider}")


def get_inference_service() -> InferenceService:
    return InferenceService(
        provider=get_provider(),
        timeout_seconds=get_settings().inference_timeout_seconds,
    )

