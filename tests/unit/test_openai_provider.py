from types import SimpleNamespace

import httpx
import pytest
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

from app.core.exceptions import InferenceError
from app.models.inference import InferenceRequest
from app.providers.openai import OpenAIProvider


class FakeResponses:
    def __init__(self, output_text: str = "", error: Exception | None = None) -> None:
        self.output_text = output_text
        self.error = error
        self.kwargs: dict[str, object] = {}

    async def create(self, **kwargs: object) -> SimpleNamespace:
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return SimpleNamespace(output_text=self.output_text, model="test-model")


class FakeClient:
    def __init__(self, output_text: str = "", error: Exception | None = None) -> None:
        self.responses = FakeResponses(output_text, error)


@pytest.mark.asyncio
async def test_openai_provider_maps_response() -> None:
    client = FakeClient("provider output")
    provider = OpenAIProvider(client=client, model="configured-model")  # type: ignore[arg-type]

    result = await provider.generate(InferenceRequest(prompt="hello", max_tokens=50))

    assert result.text == "provider output"
    assert result.model == "test-model"
    assert client.responses.kwargs["store"] is False
    assert client.responses.kwargs["max_output_tokens"] == 50


@pytest.mark.asyncio
async def test_openai_provider_rejects_empty_output() -> None:
    client = FakeClient("")
    provider = OpenAIProvider(client=client, model="configured-model")  # type: ignore[arg-type]

    with pytest.raises(InferenceError) as error:
        await provider.generate(InferenceRequest(prompt="hello"))

    assert error.value.code == "empty_provider_response"


def provider_errors() -> list[tuple[Exception, str, int]]:
    request = httpx.Request("POST", "https://api.openai.com/v1/responses")
    rate_limit_response = httpx.Response(429, request=request)
    server_response = httpx.Response(500, request=request)
    return [
        (
            RateLimitError("rate limited", response=rate_limit_response, body=None),
            "provider_rate_limited",
            429,
        ),
        (APITimeoutError(request=request), "provider_timeout", 504),
        (
            APIConnectionError(message="connection failed", request=request),
            "provider_unavailable",
            503,
        ),
        (
            APIStatusError("provider failed", response=server_response, body=None),
            "inference_failed",
            502,
        ),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(("provider_error", "code", "status_code"), provider_errors())
async def test_openai_provider_translates_errors(
    provider_error: Exception,
    code: str,
    status_code: int,
) -> None:
    client = FakeClient(error=provider_error)
    provider = OpenAIProvider(client=client, model="configured-model")  # type: ignore[arg-type]

    with pytest.raises(InferenceError) as error:
        await provider.generate(InferenceRequest(prompt="hello"))

    assert error.value.code == code
    assert error.value.status_code == status_code
