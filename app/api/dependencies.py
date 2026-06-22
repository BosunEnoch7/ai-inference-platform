from functools import lru_cache

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.exceptions import ConfigurationError
from app.providers.base import LLMProvider
from app.providers.mock import MockLLMProvider
from app.providers.openai import OpenAIProvider
from app.services.inference import InferenceService


@lru_cache
def get_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider == "mock":
        return MockLLMProvider()
    if settings.openai_api_key is None:
        raise ConfigurationError(
            "The OpenAI provider is not configured.",
            code="provider_not_configured",
        )
    client = AsyncOpenAI(
        api_key=settings.openai_api_key.get_secret_value(),
        timeout=settings.inference_timeout_seconds,
        max_retries=settings.openai_max_retries,
    )
    return OpenAIProvider(client=client, model=settings.openai_model)


def get_inference_service() -> InferenceService:
    return InferenceService(
        provider=get_provider(),
        timeout_seconds=get_settings().inference_timeout_seconds,
    )
