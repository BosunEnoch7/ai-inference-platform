using '../foundation.bicep'

param namePrefix = 'aiinfer'
param environmentName = 'production'
param containerAppsLocation = 'northeurope'
param managedEnvironmentNameOverride = 'aiinfer-staging-dz6yrr-cae-ne'
param deployManagedEnvironment = false
param existingManagedEnvironmentResourceGroup = 'rg-ai-inference-staging'
param monitoringWorkspaceNameOverride = 'aiinfer-staging-dz6yrr-logs'
param monitoringWorkspaceResourceGroupOverride = 'rg-ai-inference-staging'
// Set both values before the first production deployment.
param monitoringEnabled = false
param monitoringAlertEmail = ''
param tags = {
  application: 'ai-inference-platform'
  environment: 'production'
  managedBy: 'bicep'
  costCenter: 'engineering'
}
