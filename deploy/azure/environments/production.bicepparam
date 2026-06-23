using '../foundation.bicep'

param namePrefix = 'aiinfer'
param environmentName = 'production'
param tags = {
  application: 'ai-inference-platform'
  environment: 'production'
  managedBy: 'bicep'
  costCenter: 'engineering'
}

