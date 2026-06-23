# Incident and blocker log

This document records project incidents, blockers, and engineering decisions that affected delivery.

It is intentionally kept as a living operations artifact. Each new blocker should include:

- what happened;
- impact;
- root cause or likely cause;
- how it was handled;
- prevention or follow-up action.

## Incident summary

| ID | Area | Status | Summary |
| --- | --- | --- | --- |
| INC-001 | Dependency validation | Mitigated | Full local dependency installation was unreliable because network/package registry access was blocked or inconsistent. |
| INC-002 | Git operations | Mitigated | Commit and push operations required elevated filesystem/network permission. |
| INC-003 | Azure CLI local config | Resolved | Azure CLI attempted to read/write the default user profile path and hit permission errors. |
| INC-004 | Bicep template validation | Resolved | Initial Azure Bicep compilation surfaced unsupported or unstable resource properties. |
| INC-005 | Azure managed Redis scope | Accepted / deferred | Managed Redis provisioning was deferred because the Azure Redis service/API surface is change-prone and could not be verified safely during this phase. |
| INC-006 | Key Vault secret write permission | Resolved | GitHub deployment identity needed explicit Key Vault data-plane permission to write runtime secrets. |
| INC-007 | YAML validation | Accepted / monitored | Local YAML validation tools were unavailable in the environment. |
| INC-008 | Azure OIDC bootstrap | Resolved | Azure federated credential creation failed with inline JSON quoting in PowerShell. |
| INC-009 | GitHub environment automation | Open / user action required | GitHub CLI is not installed in the workspace, so repository environments must be configured manually or with another authenticated GitHub tool. |
| INC-010 | Container image build | Mitigated | Local Docker build failed during PyPI dependency downloads because of transient network/DNS instability. |
| INC-011 | ACR cloud build | Accepted / workaround required | Azure Container Registry Tasks are not permitted for the current registry/subscription. |

## INC-001: Dependency installation and full test execution instability

### What happened

Network/package registry access was unreliable during development. This prevented consistent full dependency installation and made full local test execution unreliable.

### Impact

The project could not always be validated with the complete local Python test toolchain in the working environment.

### Treatment

We used the strongest available local checks that did not depend on external package downloads:

- Python compile checks with `python -m compileall`;
- static repository checks such as `git diff --check`;
- Bicep template compilation;
- GitHub Actions configuration for full CI validation in a connected runner.

### Follow-up

When registry access is available, run:

```bash
python -m pip install -r requirements-dev.txt
ruff check .
pytest --cov=app --cov-report=term-missing
```

## INC-002: Git commit and push permission requirements

### What happened

Git operations that write to `.git` or push to GitHub required elevated permission in the workspace.

### Impact

Commits and pushes could not be completed with normal sandbox permissions.

### Treatment

Git write/push operations were performed only after explicit approval. Successful commits were pushed to GitHub and verified with `git status --short` and `git log -1 --oneline`.

### Follow-up

Continue treating commit and push as controlled release actions.

## INC-003: Azure CLI local configuration permission error

### What happened

Azure CLI attempted to access the default profile path:

```text
C:\Users\USER\.azure\azureProfile.json
```

This caused permission errors in the local execution environment.

### Impact

Azure CLI commands failed before reaching the intended Bicep or Azure validation step.

### Treatment

We redirected Azure CLI configuration to a writable temporary directory:

```powershell
$env:AZURE_CONFIG_DIR = Join-Path $env:TEMP 'codex-azure-config'
```

### Follow-up

Use this environment variable for local Azure CLI checks in this workspace unless the default Azure profile path becomes writable.

## INC-004: Bicep template compilation issues

### What happened

Initial Azure Bicep compilation surfaced template issues, including:

- unsupported Azure Container Registry property usage;
- role assignment naming that depended on runtime-only principal values.

### Impact

Infrastructure templates could not be considered deployment-ready until compilation succeeded.

### Treatment

The unsupported property was removed. Role assignment naming was changed to use stable resource identifiers while still assigning the correct runtime principal.

Bicep validation then passed for:

- `deploy/azure/foundation.bicep`;
- `deploy/azure/app.bicep`;
- `deploy/azure/environments/staging.bicepparam`;
- `deploy/azure/environments/production.bicepparam`.

### Follow-up

Keep Bicep compilation in CI before deployment.

## INC-005: Managed Redis provisioning deferred

### What happened

Distributed Redis rate limiting exists at the application level, but Azure managed Redis provisioning was not added to Bicep in this phase.

### Impact

Rate limiting can be enabled only when an approved external Redis URL is provided.

### Treatment

The Azure app deployment accepts `REDIS_URL` through Key Vault when rate limiting is enabled. The infrastructure documentation explicitly states that managed Redis should be provisioned separately for now.

### Follow-up

Add managed Redis provisioning later after confirming the preferred Azure service, SKU, networking model, and API version.

## INC-006: Key Vault secret write permission for GitHub deployment identity

### What happened

The deployment workflow writes `INFERENCE_API_KEY`, `OPENAI_API_KEY`, and `REDIS_URL` into Azure Key Vault. With Key Vault RBAC enabled, the GitHub deployment identity needs an explicit data-plane role assignment.

### Impact

Without this permission, infrastructure deployment could succeed but secret injection could fail.

### Treatment

The foundation Bicep template now accepts `deploymentPrincipalObjectId` and grants that principal `Key Vault Secrets Officer` scoped to the project Key Vault. The GitHub workflow passes `AZURE_CLIENT_OBJECT_ID` into the deployment.

### Follow-up

Set `AZURE_CLIENT_OBJECT_ID` as a GitHub environment variable for both `staging` and `production`.

## INC-007: Local YAML parser unavailable

### What happened

Local Ruby and Node-based YAML validation options were not available in the execution environment.

### Impact

GitHub Actions YAML syntax could not be fully parsed locally with those tools.

### Treatment

Workflow files were manually reviewed and committed with CI-side validation expected to run on GitHub.

### Follow-up

Add `actionlint` to the local or CI toolchain in a future hardening phase.

## INC-008: Azure federated credential JSON quoting

### What happened

During live Azure OIDC bootstrap, `az ad app federated-credential create` failed when PowerShell parsed the inline JSON argument.

### Impact

The Azure Entra application and service principal were created, but the GitHub federated credentials were not created in the first attempt.

### Treatment

The federated credential parameters were written to temporary JSON files and passed to Azure CLI as file paths. This avoided shell quoting issues and successfully created:

- `github-staging`;
- `github-production`.

### Follow-up

Prefer JSON parameter files for Azure CLI commands that require structured JSON when running from PowerShell.

## INC-009: GitHub CLI unavailable for environment automation

### What happened

The workspace does not have the GitHub CLI available as `gh`.

### Impact

GitHub repository environments, variables, and secrets cannot be configured automatically from this workspace without installing/authenticating an additional GitHub tool.

### Treatment

Azure-side OIDC setup was completed. GitHub-side setup must be completed manually in the GitHub web UI or from a machine with authenticated GitHub CLI/API access.

### Follow-up

Create GitHub environments named `staging` and `production`, then add the Azure variables and runtime secrets described in `docs/azure-oidc-setup.md`.

## INC-010: Local Docker build dependency download failure

### What happened

The local Docker build failed while installing Python dependencies from PyPI. The build logs showed transient DNS/name-resolution failures and incomplete package metadata downloads.

### Impact

The staging container image could not be built and pushed from the local machine on the first attempt.

### Treatment

Runtime dependencies were pinned to make Docker and CI builds more reproducible. The Dockerfile pip install step was updated with stronger retry, timeout, resume, and binary-preference options.

### Follow-up

Retry the local Docker build and push. If the local network remains unstable, run the deployment through GitHub Actions after configuring the GitHub `staging` environment.

## INC-011: ACR Tasks not permitted

### What happened

`az acr build` failed with `TasksOperationsNotAllowed` for the current registry/subscription.

### Impact

Azure Container Registry cloud build cannot be used as a fallback image build path in this environment.

### Treatment

The fallback path shifted back to local Docker build/push with improved dependency pinning and pip retry behavior.

### Follow-up

If cloud builds are required later, confirm subscription policy/support for ACR Tasks or use GitHub Actions hosted runners to build and push the image.
