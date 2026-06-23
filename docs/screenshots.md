# Screenshot evidence guide

Use this guide to capture final proof that the platform works as a production-style AI infrastructure project.

Store screenshots in the `screenshots/` directory.

## Recommended screenshots

| File name | Evidence |
| --- | --- |
| `github-actions-ci.png` | CI workflow passing on `main`. |
| `github-actions-azure-deploy.png` | Azure deployment workflow completed successfully. |
| `azure-container-app.png` | Azure Container App overview showing running revision. |
| `azure-key-vault.png` | Key Vault exists with secret names visible, not secret values. |
| `azure-container-registry.png` | ACR repository with immutable image tag. |
| `api-docs.png` | FastAPI `/docs` page. |
| `health-endpoint.png` | `/health` response from deployed app. |
| `ready-endpoint.png` | `/ready` response from deployed app. |
| `inference-auth-failure.png` | `/api/v1/inference` returns `401` without `X-API-Key`. |
| `inference-success.png` | `/api/v1/inference` returns success with `X-API-Key`. |
| `metrics-endpoint.png` | `/metrics` endpoint response. |
| `grafana-dashboard.png` | Grafana inference dashboard. |

## Safety rules

- Do not capture real secret values.
- Blur subscription IDs if sharing publicly.
- Blur API keys, tenant IDs, and client IDs if needed.
- Prefer showing resource names, workflow status, endpoint status, and high-level logs.

## Suggested final demo flow

1. Show GitHub repository and README.
2. Show CI passing.
3. Show Azure deployment workflow passing.
4. Show Azure resources.
5. Show `/health` and `/ready`.
6. Show inference rejecting unauthenticated requests.
7. Show inference succeeding with an API key.
8. Show metrics/Grafana.
9. Show incident log and explain how blockers were handled.

