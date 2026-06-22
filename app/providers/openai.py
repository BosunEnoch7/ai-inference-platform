from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    RateLimitError,
)

from app.core.exceptions import InferenceError
from app.models.inference import InferenceRequest, ProviderResult
from app.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, client: AsyncOpenAI, model: str) -> None:
        self.client = client
        self.model = model

    async def generate(self, request: InferenceRequest) -> ProviderResult:
        try:
            response = await self.client.responses.create(
                model=self.model,
                input=request.prompt,
                max_output_tokens=request.max_tokens,
                temperature=request.temperature,
                store=False,
            )
        except RateLimitError as exc:
            raise InferenceError(
                "The inference provider is rate limited.",
                code="provider_rate_limited",
                status_code=429,
            ) from exc
        except APITimeoutError as exc:
            raise InferenceError(
                "The inference provider timed out.",
                code="provider_timeout",
                status_code=504,
            ) from exc
        except APIConnectionError as exc:
            raise InferenceError(
                "The inference provider is unavailable.",
                code="provider_unavailable",
                status_code=503,
            ) from exc
        except APIStatusError as exc:
            raise InferenceError("The inference provider rejected the request.") from exc

        if not response.output_text:
            raise InferenceError(
                "The inference provider returned an empty response.",
                code="empty_provider_response",
            )

        return ProviderResult(
            text=response.output_text,
            model=response.model or self.model,
        )
