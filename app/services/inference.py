import asyncio
from time import perf_counter
from uuid import uuid4

from app.core.exceptions import InferenceError
from app.core.metrics import INFERENCE_DURATION, INFERENCE_REQUESTS
from app.models.inference import InferenceRequest, InferenceResponse
from app.providers.base import LLMProvider


class InferenceService:
    def __init__(self, provider: LLMProvider, timeout_seconds: float) -> None:
        self.provider = provider
        self.timeout_seconds = timeout_seconds

    async def infer(self, request: InferenceRequest) -> InferenceResponse:
        provider = self.provider.name
        started_at = perf_counter()
        try:
            result = await asyncio.wait_for(
                self.provider.generate(request),
                timeout=self.timeout_seconds,
            )
        except TimeoutError as exc:
            INFERENCE_REQUESTS.labels(provider=provider, outcome="provider_timeout").inc()
            raise InferenceError(
                "The inference provider timed out.",
                code="provider_timeout",
                status_code=504,
            ) from exc
        except InferenceError as exc:
            INFERENCE_REQUESTS.labels(provider=provider, outcome=exc.code).inc()
            raise
        except Exception as exc:
            INFERENCE_REQUESTS.labels(provider=provider, outcome="inference_failed").inc()
            raise InferenceError("The inference provider failed.") from exc
        else:
            INFERENCE_REQUESTS.labels(provider=provider, outcome="success").inc()
        finally:
            INFERENCE_DURATION.labels(provider=provider).observe(perf_counter() - started_at)

        return InferenceResponse(
            request_id=str(uuid4()),
            output=result.text,
            model=result.model,
            provider=self.provider.name,
        )
