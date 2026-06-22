from fastapi.testclient import TestClient


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
