# Azure infrastructure

This directory contains resource-group-scoped Bicep templates for a two-stage deployment.

## Structure

- `foundation.bicep`: deploys shared Azure resources through modules.
- `modules/platform.bicep`: Log Analytics, Container Apps environment, managed identity, and Key Vault.
- `modules/monitoring.bicep`: opt-in Azure Monitor log alerts and an email action group.
- `modules/registry.bicep`: Azure Container Registry and managed-identity pull access.
- `app.bicep`: deploys the versioned container image to Azure Container Apps.
- `environments/`: reviewed staging and production foundation parameters.

The split allows the workflow to provision ACR, push an immutable image, and only then create or update the Container App.

## Secret flow

GitHub Actions authenticates with OIDC. Runtime secrets are written to Key Vault and referenced by Container Apps through a user-assigned managed identity. Secrets are not placed in Bicep parameter files, container images, or Azure deployment outputs.

Expected GitHub environment secrets:

- `INFERENCE_API_KEY`
- `OPENAI_API_KEY` when the OpenAI provider is selected
- `REDIS_URL` when distributed rate limiting is enabled

Expected GitHub environment variables:

- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_OBJECT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

## Redis

The application template accepts a Key Vault-backed Redis URL but does not create a managed Redis SKU. Provision the approved managed Redis service separately, store its TLS connection URL as the `REDIS_URL` GitHub environment secret, and enable rate limiting during deployment.

Production monitoring is deliberately opt-in. Set `monitoringEnabled = true` and provide
`monitoringAlertEmail` in the production parameter file before deployment. This creates
alerts for application error logs and Container Apps system warnings/errors.
