# Deployment readiness

The application is packaged as a non-root container and configured through environment variables. It can later target Azure Container Apps, App Service, or Kubernetes without changing the API layer.

Production should use a managed registry, immutable image tags, TLS ingress, managed identity, Key Vault references, autoscaling limits, and centralized logs.

