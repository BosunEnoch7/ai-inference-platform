# Production readiness guide

This guide defines what must be true before `ai-inference-platform` is promoted from staging to production.

## Current production posture

The platform is staging-ready and release-tagged. Production deployment is intentionally gated and should only run from a version tag after the checklist below is complete.

The first production infrastructure release will use the deterministic `mock`
provider. This validates the production platform without introducing an external
LLM credential or usage cost. Promotion to `openai` is a separate controlled
configuration change.

The current Azure subscription permits one Container Apps managed environment.
Production therefore shares the existing North Europe managed environment with
staging while retaining separate application resources, identity, registry,
Key Vault, secrets, monitoring rules, and resource group. Alert queries target
the shared environment's Log Analytics workspace because it receives both
staging and production container logs.

## Production deployment controls

The Azure deployment workflow protects production with two controls:

- the GitHub `production` environment must be selected;
- the workflow input `production_confirmation` must be exactly `DEPLOY PRODUCTION`;
- the workflow must be executed from a version tag such as `v1.0.0`.
- Azure Monitor alerts must be enabled with an operations email.
- required secrets are validated before Azure authentication or resource creation.

Recommended GitHub environment settings:

- require reviewer approval for `production`;
- restrict who can approve production deployments;
- keep production secrets separate from staging secrets;
- avoid sharing API keys across environments.

## Required production secrets

Set these in the GitHub `production` environment:

- `INFERENCE_API_KEY`: required for protected inference.
- `OPENAI_API_KEY`: required only when deploying with `llm_provider=openai`.
- `REDIS_URL`: required only when deploying with `rate_limit_enabled=true`.

Production secrets are written to Azure Key Vault during deployment and referenced by the Container App through managed identity.

## Pre-production checklist

- CI is green on `main`.
- A staging deployment has passed smoke tests.
- A version tag has been created from the tested commit.
- `production` GitHub environment has reviewer protection enabled.
- Production `INFERENCE_API_KEY` has been created and stored in GitHub environment secrets. (Complete)
- LLM provider decision is documented: initial release uses `mock`. (Complete)
- If using OpenAI, `OPENAI_API_KEY` is present and model choice is approved.
- If enabling rate limiting, managed Redis is provisioned and `REDIS_URL` is present.
- Azure permissions are reviewed and reduced after bootstrap where possible.
- Alerting expectations are defined for availability, error rate, latency, and container restarts.
- `monitoringEnabled` is set to `true` and `monitoringAlertEmail` identifies the operations owner.
- Rollback procedure is understood before deployment.

## Production deployment procedure

1. Create a release tag from the commit already proven in staging.
2. Open the `Deploy to Azure` GitHub Actions workflow.
3. Select the release tag as the workflow ref.
4. Choose `environment=production`.
5. Choose the production provider and rate-limit settings.
6. Enable monitoring and enter the operations alert email.
7. Enter `DEPLOY PRODUCTION` in `production_confirmation`.
8. Start the workflow and wait for reviewer approval if configured.
9. Confirm the workflow smoke tests pass.
10. Record the production URL, image tag, revision, and workflow run in `docs/deployment-evidence.md`.

## Rollback procedure

Azure Container Apps supports revision-based rollback.

Recommended rollback steps:

1. Identify the last known good revision.
2. Switch traffic back to the known good revision or redeploy the last known good image tag.
3. Run smoke tests against `/health`, `/ready`, and `/api/v1/inference`.
4. Document the incident in `docs/incidents.md`.
5. Open a follow-up task for root-cause analysis.

## Production monitoring targets

Minimum production signals:

- API liveness and readiness status.
- HTTP 5xx rate.
- Inference error rate.
- P95 request latency.
- Container restart count.
- Replica count and scaling activity.
- Key Vault secret reference failures.
- Redis connectivity failures when rate limiting is enabled.
- OpenAI provider failures when `llm_provider=openai`.

## Production hardening backlog

- Enable the Azure Monitor alert rules already defined in Bicep with the production operations email.
- Extend alerts with latency and availability thresholds after production traffic establishes a baseline.
- Add managed Redis infrastructure through Bicep.
- Add private ingress, Front Door, or WAF if public exposure is not acceptable.
- Replace broad bootstrap Azure roles with least-privilege custom roles where practical.
- Add release notes automation.
- Add synthetic uptime checks from outside Azure.
