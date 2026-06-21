# Architecture

The platform separates transport, orchestration, and provider integration:

1. FastAPI routes validate HTTP input and return documented response models.
2. `InferenceService` controls timeouts and translates provider failures.
3. `LLMProvider` defines the contract implemented by provider adapters.
4. Configuration comes from environment variables through one validated settings object.

The service is stateless, supporting horizontal scaling. Liveness is separate from readiness so platforms can restart failed processes without routing traffic to an unready instance.

Future iterations will add structured logging, Prometheus metrics, provider retries, authentication, rate limiting, Azure infrastructure, and managed secret injection.

