# Project status

This document summarizes the current delivery state of `ai-inference-platform`.

## Current completion estimate

The repository implementation is **complete for the staging scope** and production hardening has started.

The full staging project is **100% complete**. CI, GitHub OIDC deployment, Azure runtime, smoke tests, documentation, and visual evidence are complete.

The full production-grade platform is approximately **85% complete**. The remaining work is mostly production governance, alerting, least-privilege review, and optional managed services such as Redis/private networking.

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
- Live Azure foundation deployment
- Microsoft.App provider registration
- Staging container image build
- Staging image push to Azure Container Registry
- Recovery from a suspended Container Apps managed environment
- Healthy North Europe Container Apps environment
- Live Azure Container App deployment
- Healthy running revision (`ai-inference-platform--0000001`)
- Live health, readiness, authentication, inference, and metrics smoke tests
- Green GitHub Actions quality, container, security, and infrastructure jobs
- GitHub `staging` and `production` environments
- Passwordless GitHub-to-Azure OIDC authentication
- Successful GitHub Actions staging deployment
- GitHub deployment smoke tests
- Production deployment gate requiring explicit confirmation
- Production deployments restricted to version tags
- Production readiness guide and rollback checklist

## Remaining

No work remains for the agreed staging scope. Production rollout and advanced hardening are separate follow-on phases.

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
