# Project status

This document summarizes the current delivery state of `ai-inference-platform`.

## Current completion estimate

The repository implementation is approximately **90% complete**.

The full cloud project is approximately **80% complete** because the remaining work requires live Azure and GitHub environment configuration.

## Completed

- FastAPI application structure
- Health and readiness endpoints
- Versioned inference endpoint
- Provider-independent AI service layer
- Mock LLM provider
- Optional OpenAI provider integration
- Environment-based configuration
- Secure local secret pattern with `.env.example`
- Stable error envelope
- Request correlation IDs
- Structured JSON logging
- API key authentication
- Redis-backed distributed rate limiting
- Prometheus metrics endpoint
- Local Prometheus and Grafana setup
- Dockerfile and Docker Compose support
- GitHub Actions CI
- Python lint/test/coverage workflow
- Container build validation
- Dependency and filesystem security scanning
- Modular Azure Bicep infrastructure
- Azure Container Apps deployment workflow
- GitHub OIDC deployment design
- Azure Key Vault secret flow
- Post-deployment smoke tests
- Incident and blocker log

## Remaining before live staging

- Create Azure subscription/resource access if not already available.
- Create GitHub Actions OIDC identity in Microsoft Entra ID.
- Add federated credentials for GitHub `staging` and `production` environments.
- Add GitHub environment variables:
  - `AZURE_CLIENT_ID`
  - `AZURE_CLIENT_OBJECT_ID`
  - `AZURE_TENANT_ID`
  - `AZURE_SUBSCRIPTION_ID`
- Add GitHub environment secret:
  - `INFERENCE_API_KEY`
- Run the `Deploy to Azure` workflow for `staging`.
- Capture deployment evidence screenshots.

## Remaining before production

- Protect the GitHub `production` environment with reviewer approval.
- Decide whether production uses `mock` or `openai`.
- If using OpenAI, add `OPENAI_API_KEY`.
- Decide whether distributed rate limiting should be enabled.
- If enabling rate limiting, provision managed Redis and add `REDIS_URL`.
- Review Azure permissions and reduce bootstrap privileges.
- Add Azure-native alerts.
- Optionally add private networking.

## Final acceptance criteria

The project can be considered complete when:

- CI passes on `main`.
- Azure staging deployment completes successfully.
- Smoke tests pass against the deployed URL.
- Screenshots are captured in `screenshots/`.
- README and docs accurately describe the final deployed state.
- The incident log includes all known blockers and resolutions.

