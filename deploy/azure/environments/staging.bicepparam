using '../foundation.bicep'

param namePrefix = 'aiinfer'
param environmentName = 'staging'
param containerAppsLocation = 'northeurope'
param managedEnvironmentNameOverride = 'aiinfer-staging-dz6yrr-cae-ne'
param tags = {
  application: 'ai-inference-platform'
  environment: 'staging'
  managedBy: 'bicep'
  costCenter: 'engineering'
}
