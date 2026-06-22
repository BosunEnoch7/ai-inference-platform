from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app


@contextmanager
def authentication(api_key: str | None) -> Iterator[None]:
    def settings_override() -> Settings:
        return Settings(
            api_auth_enabled=True,
            inference_api_key=api_key,
        )

    app.dependency_overrides[get_settings] = settings_override
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_settings, None)

def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "0.1.0"}
    assert response.headers["X-Request-ID"]


def test_request_id_is_preserved(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "test-request-123"})
    assert response.headers["X-Request-ID"] == "test-request-123"


def test_invalid_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "invalid request id"})
    assert response.headers["X-Request-ID"] != "invalid request id"


def test_readiness(client: TestClient) -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "provider": "mock"}


def test_inference(client: TestClient) -> None:
    response = client.post("/api/v1/inference", json={"prompt": "Hello platform"})
    body = response.json()
    assert response.status_code == 200
    assert body["output"] == "Mock response: Hello platform"
    assert body["provider"] == "mock"
    assert body["model"] == "mock-model-v1"
    assert body["request_id"]


def test_inference_rejects_empty_prompt(client: TestClient) -> None:
    response = client.post("/api/v1/inference", json={"prompt": ""})
    assert response.status_code == 422


def test_inference_accepts_valid_api_key(client: TestClient) -> None:
    with authentication("test-secret"):
        response = client.post(
            "/api/v1/inference",
            headers={"X-API-Key": "test-secret"},
            json={"prompt": "Hello platform"},
        )

    assert response.status_code == 200


def test_inference_rejects_missing_api_key(client: TestClient) -> None:
    with authentication("test-secret"):
        response = client.post("/api/v1/inference", json={"prompt": "Hello platform"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_api_key"
    assert response.json()["error"]["request_id"]


def test_inference_rejects_invalid_api_key(client: TestClient) -> None:
    with authentication("test-secret"):
        response = client.post(
            "/api/v1/inference",
            headers={"X-API-Key": "wrong-secret"},
            json={"prompt": "Hello platform"},
        )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_api_key"


def test_inference_reports_missing_auth_configuration(client: TestClient) -> None:
    with authentication(None):
        response = client.post("/api/v1/inference", json={"prompt": "Hello platform"})

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "authentication_not_configured"


def test_metrics(client: TestClient) -> None:
    client.get("/health")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text
    assert "inference_requests_total" in response.text
