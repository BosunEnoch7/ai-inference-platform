using '../foundation.bicep'

param namePrefix = 'aiinfer'
param environmentName = 'staging'
param tags = {
  application: 'ai-inference-platform'
  environment: 'staging'
  managedBy: 'bicep'
  costCenter: 'engineering'
}

