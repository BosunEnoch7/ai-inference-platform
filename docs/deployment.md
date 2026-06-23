# Azure deployment

The project targets Azure Container Apps using modular Bicep and GitHub Actions OIDC authentication.

## Deployed foundation

- Azure Container Registry with local administrator access disabled
- Azure Container Apps managed environment
- Log Analytics workspace
- User-assigned managed identity
- Azure Key Vault with RBAC, purge protection, and soft delete
- `AcrPull` and `Key Vault Secrets User` assignments for the application identity

The application deployment adds HTTPS ingress, liveness and readiness probes, HTTP concurrency autoscaling, resource limits, immutable image tags, and Key Vault-backed secret references.

## One-time OIDC bootstrap

Create a Microsoft Entra application or user-assigned identity for GitHub Actions and add federated credentials for this repository's `staging` and `production` GitHub environments. Configure these GitHub environment variables:

- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_OBJECT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

The deployment principal needs permission to create the target resource group and resources, assign the application identity's scoped roles, push to ACR, and write Key Vault secrets. Use a tightly scoped custom role where possible. A bootstrap administrator may temporarily grant Contributor plus role-assignment permissions, then reduce the scope after the resource group exists.

Configure environment protection rules so production requires reviewer approval.

See [Azure OIDC setup](azure-oidc-setup.md) for the step-by-step bootstrap runbook.

## GitHub secrets

- `INFERENCE_API_KEY` is required because Azure deployments enable inference authentication.
- `OPENAI_API_KEY` is required only when `llm_provider=openai`.
- `REDIS_URL` is required only when distributed rate limiting is enabled.

The workflow writes these values directly to Key Vault. It never passes them as image build arguments or stores them in repository files.

## Deployment sequence

1. Manually run the `Deploy to Azure` workflow.
2. Select staging or production, region, provider, and rate-limiting mode.
3. OIDC exchanges the GitHub identity for a short-lived Azure token.
4. Bicep deploys the foundation.
5. The workflow injects environment secrets into Key Vault.
6. Docker builds and pushes an immutable SHA-tagged image to ACR.
7. Bicep deploys the Container App and reports its HTTPS URL.
8. The workflow runs smoke tests against `/health`, `/ready`, and authenticated inference.

## Validation

The CI workflow compiles both Bicep templates and all environment parameter files. Local validation uses:

```powershell
$env:AZURE_CONFIG_DIR = Join-Path $env:TEMP 'ai-inference-azure'
az bicep build --file deploy/azure/foundation.bicep --stdout | Out-Null
az bicep build --file deploy/azure/app.bicep --stdout | Out-Null
```

No Azure deployment is performed automatically on a push. Production deployment remains an explicit, protected workflow action.

## Smoke tests

The Azure deployment workflow verifies the deployed application before marking the run complete:

- `GET /health` must return success.
- `GET /ready` must return success.
- unauthenticated `POST /api/v1/inference` must return `401`.
- authenticated `POST /api/v1/inference` must return success using the configured `INFERENCE_API_KEY`.

When `llm_provider=openai`, the authenticated smoke test performs one small real provider call.
