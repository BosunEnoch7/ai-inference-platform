# Operations guide

- Liveness: `GET /health`
- Readiness: `GET /ready`
- Local API docs: `GET /docs`
- Logs: standard output and standard error

Never store credentials in source control, Compose files, or container images. Local `.env` files are developer-only. Production secrets will be supplied by the cloud secret manager.

Prometheus metrics and Grafana dashboards are reserved for a later phase.

The default `mock` provider requires no credentials. For OpenAI, set `LLM_PROVIDER=openai`, inject `OPENAI_API_KEY` through the runtime secret manager, and choose the deployed model with `OPENAI_MODEL`.
