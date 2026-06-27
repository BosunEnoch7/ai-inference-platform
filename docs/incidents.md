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
| INC-010 | Container image build | Resolved | Local Docker build failed during PyPI dependency downloads because of transient network/DNS instability. |
| INC-011 | ACR cloud build | Accepted / workaround required | Azure Container Registry Tasks are not permitted for the current registry/subscription. |
| INC-012 | Azure deployment polling | Resolved | Long-running Azure deployments exceeded the local command timeout while continuing server-side. |
| INC-013 | Container Apps environment | Resolved | The staging Container Apps environment reported `ManagedClusterSuspended`, preventing a revision from starting. |
| INC-014 | Azure CLI connectivity | Mitigated | DNS resolution for Microsoft Azure endpoints failed intermittently during deployment diagnostics and cleanup. |
| INC-015 | GitHub Actions dependencies | Resolved | CI referenced an unavailable Bicep setup action and an unpublished Trivy action tag. |
| INC-016 | Development dependency security | Resolved | `pip-audit` detected CVE-2025-71176 in pytest 8.4.2. |
| INC-017 | GitHub OIDC issuer matching | Resolved | Entra federated credentials used a trailing slash that did not exactly match GitHub's token issuer. |
| INC-018 | Azure resource-group location | Resolved | A deployment retry supplied North Europe for an existing West Europe resource group. |
| INC-019 | Azure RBAC inventory | Resolved | A broad role-assignment query exceeded the local command timeout. |
| INC-020 | Production secret generation | Resolved | The initial PowerShell RNG method was unavailable, so the secret was immediately regenerated and rotated. |
| INC-021 | Container Apps environment quota | Resolved | Production could not create a second managed environment under the subscription quota. |

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

### Resolution

The cached, pinned wheelhouse build completed successfully. Image `41e7f27` was pushed to Azure Container Registry.

## INC-011: ACR Tasks not permitted

### What happened

`az acr build` failed with `TasksOperationsNotAllowed` for the current registry/subscription.

### Impact

Azure Container Registry cloud build cannot be used as a fallback image build path in this environment.

### Treatment

The fallback path shifted back to local Docker build/push with improved dependency pinning and pip retry behavior.

### Follow-up

If cloud builds are required later, confirm subscription policy/support for ACR Tasks or use GitHub Actions hosted runners to build and push the image.

## INC-012: Local timeout while Azure deployment continued

### What happened

The staging application deployment exceeded the local Azure CLI command timeout. Azure Resource Manager continued processing the deployment after the local command exited.

### Impact

The local timeout could have been mistaken for a failed deployment.

### Treatment

The deployment was checked directly in Azure using its deployment name instead of submitting a duplicate deployment.

### Resolution

The server-side state was polled independently. The first deployment eventually reported its terminal failure clearly, and the recovery deployment completed successfully.

## INC-013: Azure Container Apps managed environment suspended

### What happened

The application deployment created the Container App resource, but Azure reported `ManagedClusterSuspended` for the staging managed environment. The Container App remained `InProgress` without an FQDN or ready revision.

### Impact

The deployed image could not start, so live smoke tests could not yet run.

### Treatment

The immutable image was successfully built and pushed to ACR as `ai-inference-platform:41e7f27`. The failed Container App and suspended West Europe environment were removed. Because the subscription allowed only one Container Apps environment, the quota was released before creating a replacement in North Europe.

### Resolution

The replacement environment `aiinfer-staging-dz6yrr-cae-ne` reached `Succeeded`. The Container App deployed with a healthy running revision, and every live smoke test passed.

## INC-014: Azure CLI authentication endpoint DNS failure

### What happened

During diagnostics, the local machine temporarily failed to resolve `login.microsoftonline.com`.

### Impact

Azure environment and activity-log queries could not complete during that attempt.

### Treatment

No cloud state was inferred from a timed-out local command. Each operation was followed by an explicit Azure resource-state query, and safe retries continued after connectivity recovered.

### Resolution

The deployment recovery completed despite intermittent DNS and management endpoint timeouts. Network instability remains an environmental risk to monitor.

## INC-015: Invalid GitHub Actions dependencies

### What happened

The CI infrastructure job referenced `azure/setup-bicep@v2`, which is unavailable, and the security job referenced unpublished tag `aquasecurity/trivy-action@0.32.0`.

### Impact

GitHub Actions failed during job setup before Bicep compilation or filesystem scanning could run.

### Treatment

The infrastructure job now installs and invokes Bicep through the Azure CLI available on GitHub-hosted runners. Trivy was updated to published release `v0.36.0`.

### Resolution

CI uses resolvable tooling and is rerun against `main`.

## INC-016: Vulnerable pytest development dependency

### What happened

After CI tooling was repaired, `pip-audit` detected CVE-2025-71176 in pytest 8.4.2.

### Impact

The security job correctly blocked the pipeline even though the vulnerable package is used only for development and testing.

### Treatment

The supported pytest range was moved to patched release 9.0.3 or newer while remaining below the next major version. `pytest-asyncio` was upgraded to the compatible 1.x line.

### Resolution

CI dependency resolution now selects a pytest release containing the published security fix.

## INC-017: GitHub OIDC issuer mismatch

### What happened

GitHub produced the expected staging subject claim, but Azure login returned `AADSTS700211`. The Entra federated credentials used issuer `https://token.actions.githubusercontent.com/`, while the token issuer was `https://token.actions.githubusercontent.com`.

### Impact

Passwordless GitHub Actions authentication could not complete even though the client, tenant, subscription, audience, and subject were correct.

### Treatment

The staging and production federated credential issuers were updated to remove the trailing slash.

### Resolution

GitHub Actions authenticated successfully to Azure through OIDC without a client secret.

## INC-018: Existing resource-group location mismatch

### What happened

The first authenticated workflow retry passed North Europe to `az group create`, but `rg-ai-inference-staging` already existed in West Europe. Azure resource-group locations cannot be changed.

### Impact

The workflow stopped immediately after successful OIDC authentication.

### Treatment

The workflow was rerun with West Europe as the resource-group location. The staging Bicep parameters continued to place the recovered Container Apps environment in North Europe.

### Resolution

The complete GitHub deployment passed, including foundation deployment, secret injection, image build and push, Container App deployment, and live smoke tests.

## INC-019: Azure RBAC inventory timeout

### What happened

The first subscription-wide Azure role-assignment inventory exceeded the local
command timeout.

### Impact

No Azure state changed, but the least-privilege review could not be completed
from that query.

### Treatment

The active subscription was verified first, then the inventory was repeated with
the known deployment principal and explicit subscription scope.

### Resolution

The narrower query completed and identified subscription-scoped `Contributor`
and `User Access Administrator` assignments. The safe reduction plan is recorded
in `docs/security.md`.

## INC-020: Production inference-key generation compatibility

### What happened

The local PowerShell/.NET runtime did not support the static
`RandomNumberGenerator.Fill` method. PowerShell continued after that method
failed, so the first value supplied to GitHub was not cryptographically random.

### Impact

An invalid production inference key briefly existed in the GitHub production
environment. It was never displayed, distributed, or used by a deployment.

### Treatment

The key was immediately regenerated with the compatible
`RandomNumberGenerator.Create().GetBytes(...)` API, checked for the expected
length, and written over the earlier value.

### Resolution

GitHub confirmed the rotated `INFERENCE_API_KEY` update timestamp. Future
PowerShell secret-generation commands must stop on errors and validate generated
material before writing it to an external secret store.

## INC-021: Production Container Apps environment quota

### What happened

The first `v1.0.0` production deployment failed Azure preflight validation with
`MaxNumberOfGlobalEnvironmentsInSubExceeded`. The subscription permits only one
Container Apps managed environment, already used by staging.

### Impact

The production resource group was created, but the foundation deployment stopped
before application secrets, images, or the Container App were deployed.

### Treatment

The Bicep templates were extended to support an existing managed environment in
another resource group. Production now references the healthy staging-managed
environment in North Europe while retaining separate production resources.

### Resolution

The quota blocker is handled as an explicit environment parameter rather than by
deleting staging or repeatedly submitting an impossible second environment.
