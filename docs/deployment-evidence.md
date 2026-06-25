# Staging deployment evidence

The staging platform was deployed and verified on June 25, 2026.

## Deployment

- Azure resource group: `rg-ai-inference-staging`
- Azure Container Apps environment: `aiinfer-staging-dz6yrr-cae-ne`
- Region: North Europe
- Container App: `ai-inference-platform`
- Revision: `ai-inference-platform--0000001`
- Image tag: `a3b3d9aa657eededdf21456ef24bf3ebde87a97c`
- Runtime provider: `mock`
- API authentication: enabled
- Rate limiting: disabled until managed Redis is provisioned
- URL: `https://ai-inference-platform.icydune-429b6614.northeurope.azurecontainerapps.io`

## Smoke-test results

| Check | Expected | Result |
| --- | ---: | ---: |
| `GET /health` | 200 | 200 |
| `GET /ready` | 200 | 200 |
| Unauthenticated `POST /api/v1/inference` | 401 | 401 |
| Authenticated `POST /api/v1/inference` | 200 | 200 |
| `GET /metrics` | 200 | 200 |

The authenticated inference request returned the mock provider, `mock-model-v1`, and the expected deterministic response. The API key was retrieved from Azure Key Vault for the test and was not printed or stored in this document.

## Automation evidence

- CI workflow: [successful run 28193108353](https://github.com/BosunEnoch7/ai-inference-platform/actions/runs/28193108353)
- Azure deployment workflow: [successful run 28195026390](https://github.com/BosunEnoch7/ai-inference-platform/actions/runs/28195026390)
- CI jobs passed: quality, container, security, and infrastructure
- Deployment steps passed: OIDC login, foundation, Key Vault secrets, image build/push, Container App deployment, and smoke tests
