# Operations guide

- Liveness: `GET /health`
- Readiness: `GET /ready`
- Prometheus metrics: `GET /metrics`
- Local API docs: `GET /docs`
- Logs: standard output and standard error

Never store credentials in source control, Compose files, or container images. Local `.env` files are developer-only. Production secrets will be supplied by the cloud secret manager.

Set `API_AUTH_ENABLED=true` and inject `INFERENCE_API_KEY` to protect inference. Rotate the key through the deployment secret manager rather than rebuilding the image. In Azure, prefer Key Vault references and managed identity for secret delivery.

Set `RATE_LIMIT_ENABLED=true` to enforce distributed limits through Redis. Tune `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS` together. `RATE_LIMIT_FAIL_OPEN=false` is the secure default: Redis outages return 503 instead of bypassing enforcement.

Docker Compose exposes Prometheus on local port `9090` and Grafana on local port `3000`. Both ports bind to loopback by default. Grafana credentials are injected from `.env`; the password has no committed default.

The default `mock` provider requires no credentials. For OpenAI, set `LLM_PROVIDER=openai`, inject `OPENAI_API_KEY` through the runtime secret manager, and choose the deployed model with `OPENAI_MODEL`.

## Deployment smoke checks

After each Azure deployment, verify:

- `GET /health`
- `GET /ready`
- unauthenticated `POST /api/v1/inference` returns `401`
- authenticated `POST /api/v1/inference` returns `200`

The GitHub Actions Azure deployment workflow runs these checks automatically after the Container App deployment.
