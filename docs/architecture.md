# Architecture

The platform separates transport, orchestration, and provider integration:

1. FastAPI routes validate HTTP input and return documented response models.
2. `InferenceService` controls timeouts and translates provider failures.
3. `LLMProvider` defines the contract implemented by provider adapters.
4. Configuration comes from environment variables through one validated settings object.

The service is stateless, supporting horizontal scaling. Liveness is separate from readiness so platforms can restart failed processes without routing traffic to an unready instance.

The OpenAI adapter is selected through configuration and uses the same provider contract as the mock adapter. It applies SDK retries, request timeouts, and safe provider-error translation without exposing upstream error details.

Prometheus scrapes bounded-cardinality HTTP and inference metrics from `/metrics`. Grafana is provisioned from version-controlled datasource and dashboard definitions.

Inference can be protected by an API-key dependency without coupling authentication to provider logic. Production ingress should restrict operational endpoints separately.

Future iterations will add distributed API rate limiting, Azure infrastructure, and managed secret injection.
