using '../foundation.bicep'

param namePrefix = 'aiinfer'
param environmentName = 'production'
// Set both values before the first production deployment.
param monitoringEnabled = false
param monitoringAlertEmail = ''
param tags = {
  application: 'ai-inference-platform'
  environment: 'production'
  managedBy: 'bicep'
  costCenter: 'engineering'
}
