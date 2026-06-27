# Security and least-privilege review

## Deployment identity findings

The GitHub Actions deployment service principal currently has:

- `Contributor` at subscription scope;
- `User Access Administrator` at subscription scope.

These assignments support initial bootstrap because the workflow creates resource
groups and Bicep creates role assignments. They are broader than the steady-state
access required by one application.

## Recommended steady-state model

Use a separate administrator-controlled bootstrap process to create the staging
and production resource groups. Then scope the GitHub deployment identity to:

- `Contributor` on `rg-ai-inference-staging`;
- `Contributor` on `rg-ai-inference-production`;
- `User Access Administrator` on those two resource groups only, if Bicep
  continues to create role assignments;
- the minimum ACR and Key Vault data-plane roles required by the deployment.

After the resource groups and scoped assignments are verified:

1. remove resource-group creation from the deployment workflow;
2. test a staging deployment using only resource-group-scoped access;
3. remove subscription-level `Contributor`;
4. remove subscription-level `User Access Administrator`;
5. verify that staging deployment and rollback still succeed;
6. apply the same model to production.

Do not remove the subscription assignments before the scoped replacements are
tested. Doing so can lock the deployment identity out or break role-assignment
deployment.

## Runtime identity

The Container App uses a separate user-assigned managed identity. It receives:

- `AcrPull` on the project registry;
- `Key Vault Secrets User` on the project vault.

This separation keeps cloud deployment permissions out of the running
application.

## Review status

The access inventory and remediation design are complete. Role removal is a
controlled production-governance action and remains pending until the production
resource group exists and a staging regression deployment has passed.
