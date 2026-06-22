# API contract

Interactive OpenAPI documentation is available at `/docs` while the application runs.

The inference contract is versioned under `/api/v1`. Health endpoints remain unversioned because they are operational contracts consumed by deployment infrastructure.

Provider failures use a stable error envelope with an error code and safe message.

Provider-related responses include `provider_rate_limited` (429), `provider_unavailable` (503), `provider_timeout` (504), and a generic `inference_failed` (502). Every handled error includes a request ID for log correlation.

Inference authentication is optional and disabled by default. When enabled, `POST /api/v1/inference` requires `X-API-Key`. Missing and invalid keys receive the same `invalid_api_key` response to avoid disclosing authentication details.

When distributed rate limiting is enabled, exceeded requests return `rate_limit_exceeded` with status 429 and a `Retry-After` header.
