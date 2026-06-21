# AI Inference Platform

A production-inspired, cloud-ready FastAPI service for exposing AI inference behind a stable API contract.

## Architecture

```text
Client -> FastAPI routes -> Inference service -> LLM provider -> Response
```

The initial implementation uses a deterministic mock provider. This makes the complete request path testable without credentials while preserving a clean boundary for a future OpenAI adapter.

## Quick start

Requires Python 3.11 or newer.

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for generated API documentation.

## API

- `GET /health` — process liveness
- `GET /ready` — service readiness and active provider
- `POST /api/v1/inference` — validated text inference

## Configuration and secrets

Copy `.env.example` to `.env` for local configuration. Production secrets should be injected by the deployment platform; Azure Key Vault integration is planned for a later phase.

## Containers

```bash
docker compose up --build
```

The image runs as a non-root user and includes a health check.

## Quality checks

```bash
ruff check .
pytest --cov=app --cov-report=term-missing
```

GitHub Actions runs linting, tests, coverage enforcement, and a container build.

## Roadmap

- OpenAI provider with retries and secure secret injection
- Prometheus metrics and Grafana dashboards
- Azure deployment infrastructure
- Supply-chain and container security checks

See [architecture documentation](docs/architecture.md) and [operations guide](docs/operations.md).

