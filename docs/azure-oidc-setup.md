# Azure OIDC setup runbook

This runbook connects GitHub Actions to Azure without storing a long-lived Azure password in GitHub.

The deployment workflow uses GitHub OIDC to request a short-lived Azure token, then deploys the platform with Bicep.

## Target repository

Use this repository subject when creating federated credentials:

```text
repo:BosunEnoch7/ai-inference-platform:environment:staging
repo:BosunEnoch7/ai-inference-platform:environment:production
```

These values must match the GitHub environment names used by `.github/workflows/deploy-azure.yml`.

## Recommended setup order

1. Choose an Azure subscription.
2. Create a Microsoft Entra app registration for GitHub Actions.
3. Create a service principal for that app.
4. Add one federated credential for `staging`.
5. Add one federated credential for `production`.
6. Grant the service principal deployment permissions.
7. Add GitHub environment variables and secrets.
8. Run the `Deploy to Azure` workflow for `staging`.

## Azure CLI bootstrap

Run these commands from a secure admin terminal where you are logged in to Azure.

Replace:

- `<SUBSCRIPTION_ID>` with your Azure subscription ID.
- `<TENANT_ID>` with your Microsoft Entra tenant ID.
- `<LOCATION>` with your preferred Azure region, for example `westeurope`.

```bash
az login
az account set --subscription "<SUBSCRIPTION_ID>"

APP_NAME="github-ai-inference-platform"
REPO="BosunEnoch7/ai-inference-platform"

APP_ID=$(az ad app create \
  --display-name "$APP_NAME" \
  --query appId \
  --output tsv)

az ad sp create --id "$APP_ID"

az ad app federated-credential create \
  --id "$APP_ID" \
  --parameters "{
    \"name\": \"github-staging\",
    \"issuer\": \"https://token.actions.githubusercontent.com/\",
    \"subject\": \"repo:$REPO:environment:staging\",
    \"audiences\": [\"api://AzureADTokenExchange\"]
  }"

az ad app federated-credential create \
  --id "$APP_ID" \
  --parameters "{
    \"name\": \"github-production\",
    \"issuer\": \"https://token.actions.githubusercontent.com/\",
    \"subject\": \"repo:$REPO:environment:production\",
    \"audiences\": [\"api://AzureADTokenExchange\"]
  }"

echo "AZURE_CLIENT_ID=$APP_ID"
echo "AZURE_TENANT_ID=<TENANT_ID>"
echo "AZURE_SUBSCRIPTION_ID=<SUBSCRIPTION_ID>"
echo "AZURE_CLIENT_OBJECT_ID=$(az ad sp show --id "$APP_ID" --query id --output tsv)"
```

## Azure permissions

For the first deployment, the GitHub identity must be able to:

- create the resource group;
- deploy Bicep resources;
- create role assignments for the application managed identity;
- push the container image to Azure Container Registry;
- write runtime secrets into Key Vault.

A simple bootstrap approach is to assign the service principal `Contributor` and `User Access Administrator` at subscription scope, then reduce permissions after the first successful deployment.

```bash
SP_OBJECT_ID=$(az ad sp show --id "$APP_ID" --query id --output tsv)
SUBSCRIPTION_SCOPE="/subscriptions/<SUBSCRIPTION_ID>"

az role assignment create \
  --assignee-object-id "$SP_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --role Contributor \
  --scope "$SUBSCRIPTION_SCOPE"

az role assignment create \
  --assignee-object-id "$SP_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "User Access Administrator" \
  --scope "$SUBSCRIPTION_SCOPE"
```

For a tighter production setup, replace subscription-wide permissions with a custom role scoped to the deployment resource groups.

## GitHub environment configuration

Create two GitHub environments:

- `staging`
- `production`

For each environment, add these environment variables:

- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_OBJECT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

For each environment, add these secrets:

- `INFERENCE_API_KEY`
- `OPENAI_API_KEY` only when deploying with `llm_provider=openai`
- `REDIS_URL` only when enabling distributed rate limiting

Protect `production` with required reviewers before deployment.

## First deployment recommendation

Start with the safest staging deployment:

- environment: `staging`
- location: your chosen Azure region
- llm_provider: `mock`
- rate_limit_enabled: `false`

After deployment, verify:

- the workflow completes successfully;
- the Container App URL is shown in the workflow summary;
- `/health` returns healthy;
- `/ready` returns ready;
- `/api/v1/inference` rejects requests without `X-API-Key`;
- `/api/v1/inference` succeeds with the configured `INFERENCE_API_KEY`.
