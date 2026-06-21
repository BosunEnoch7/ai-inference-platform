import asyncio
from uuid import uuid4

from app.core.exceptions import InferenceError
from app.models.inference import InferenceRequest, InferenceResponse
from app.providers.base import LLMProvider


class InferenceService:
    def __init__(self, provider: LLMProvider, timeout_seconds: float) -> None:
        self.provider = provider
        self.timeout_seconds = timeout_seconds

    async def infer(self, request: InferenceRequest) -> InferenceResponse:
        try:
            result = await asyncio.wait_for(
                self.provider.generate(request),
                timeout=self.timeout_seconds,
            )
        except TimeoutError as exc:
            raise InferenceError(
                "The inference provider timed out.",
                code="provider_timeout",
                status_code=504,
            ) from exc
        except InferenceError:
            raise
        except Exception as exc:
            raise InferenceError("The inference provider failed.") from exc

        return InferenceResponse(
            request_id=str(uuid4()),
            output=result.text,
            model=result.model,
            provider=self.provider.name,
        )

