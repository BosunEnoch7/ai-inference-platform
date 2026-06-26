# AI Inference Platform

A production-inspired, cloud-ready FastAPI service that exposes AI inference through a stable, provider-independent API.

## Project status

Local development uses a deterministic mock LLM provider by default. An optional OpenAI adapter uses the Responses API while keeping CI and local setup credential-free.

The staging platform is deployed on Azure Container Apps and passed live health, readiness, authentication, inference, and metrics smoke tests. GitHub Actions CI and the passwordless Azure OIDC deployment workflow are green.

- Staging URL: `https://ai-inference-platform.icydune-429b6614.northeurope.azurecontainerapps.io`
- [Successful CI run](https://github.com/BosunEnoch7/ai-inference-platform/actions/runs/28193108353)
- [Successful Azure deployment](https://github.com/BosunEnoch7/ai-inference-platform/actions/runs/28195026390)

## Architecture

```text
Client
  -> FastAPI API layer
  -> Inference service
  -> LLM provider interface
  -> Mock or OpenAI provider
  -> Standardized response
```

The API, orchestration logic, and provider adapter are separated so each layer can be tested and changed independently.

## Current capabilities

- FastAPI application factory and generated OpenAPI documentation
- Liveness and readiness endpoints
- Versioned inference endpoint
- Validated request and response schemas
- Provider abstraction with a deterministic mock implementation
- Provider timeout and error translation
- Correlation IDs through the `X-Request-ID` header
- Structured JSON application logging
- Optional API-key authentication with constant-time verification
- Optional distributed Redis rate limiting with atomic counters
- Environment-based configuration
- Unit and integration tests
- Non-root Docker image and Docker Compose setup
- GitHub Actions lint, test, coverage, and container-build jobs
- CI dependency and filesystem security scanning
- Optional OpenAI provider with retries, timeouts, and safe error translation
- Prometheus HTTP and inference metrics
- Provisioned Grafana datasource and inference dashboard
- Modular Azure Container Apps Bicep infrastructure
- GitHub Actions deployment with OIDC and Key Vault references
- Post-deployment smoke tests for health, readiness, and inference authentication
- Production deployment gate requiring an explicit confirmation and version tag

## Repository structure

```text
app/
  api/          HTTP routes and dependencies
  core/         Configuration, logging, and application errors
  models/       Request, response, and internal schemas
  providers/    LLM provider interfaces and adapters
  services/     Provider-independent inference orchestration
tests/          Unit and API integration tests
docs/           Architecture, API, deployment, and operations guides
monitoring/     Prometheus and Grafana configuration
deploy/azure/   Azure Bicep deployment definitions
.github/        Continuous integration workflows
```

## Local setup

Python 3.11 or newer is required.

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies and start the API:

```bash
python -m pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Useful local URLs:

- API documentation: `http://localhost:8000/docs`
- Liveness: `http://localhost:8000/health`
- Readiness: `http://localhost:8000/ready`

## Inference API

`POST /api/v1/inference`

```json
{
  "prompt": "Explain model serving in one sentence.",
  "max_tokens": 256,
  "temperature": 0.7
}
```

The mock provider returns a deterministic response plus a request ID, provider name, and model name.

## Configuration and secrets

Copy `.env.example` to `.env` for local overrides. Never commit `.env` or real credentials.

```powershell
Copy-Item .env.example .env
```

Production secrets are injected using managed identity and Azure Key Vault instead of being stored in source control or container images.

To enable OpenAI locally, set `LLM_PROVIDER=openai`, `OPENAI_API_KEY`, and `OPENAI_MODEL` in your untracked `.env` file. The mock provider remains the safe default.

To protect inference, set `API_AUTH_ENABLED=true` and inject `INFERENCE_API_KEY`. Clients must then send the key in the `X-API-Key` header. Health, readiness, API documentation, and metrics remain unprotected for platform integration; restrict their network exposure at the ingress layer in production.

Distributed rate limiting is disabled by default. Set `RATE_LIMIT_ENABLED=true`, choose the request/window limits, and provide `REDIS_URL`. Authenticated requests are bucketed by a one-way API-key fingerprint; unauthenticated requests use the direct client address. Redis failures reject requests by default. Set `RATE_LIMIT_FAIL_OPEN=true` only when availability is more important than enforcement.

## Quality checks

```bash
ruff check .
pytest --cov=app --cov-report=term-missing
```

## Docker

Set a local Grafana administrator password in `.env` before starting the stack:

```text
GRAFANA_ADMIN_PASSWORD=replace-with-a-strong-local-password
```

```bash
docker compose up --build
```

The API image runs as a non-root user and exposes port `8000` with a container health check. Prometheus and Grafana are bound to the local machine only:

- API: `http://localhost:8000`
- Metrics: `http://localhost:8000/metrics`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

## Roadmap

- Configure GitHub production environment reviewer approval
- Add Azure-native alert rules
- Add managed Redis provisioning for production rate limiting
- Add private Azure networking, Front Door, or WAF where required

Additional detail is available in [architecture](docs/architecture.md), [API](docs/api.md), [deployment](docs/deployment.md), [production readiness](docs/production-readiness.md), [staging evidence](docs/deployment-evidence.md), [Azure OIDC setup](docs/azure-oidc-setup.md), [operations](docs/operations.md), [project status](docs/project-status.md), [screenshot evidence guide](docs/screenshots.md), and the [incident/blocker log](docs/incidents.md).
