targetScope = 'resourceGroup'

@description('Short lowercase project prefix used for globally unique resource names.')
@minLength(3)
@maxLength(12)
param namePrefix string = 'aiinfer'

@allowed([
  'staging'
  'production'
])
param environmentName string = 'staging'

param location string = resourceGroup().location
param containerAppsLocation string = location
param managedEnvironmentNameOverride string = ''
param monitoringEnabled bool = false
param monitoringAlertEmail string = ''

@description('Object ID of the GitHub Actions deployment service principal. Used to grant Key Vault secret write permissions.')
param deploymentPrincipalObjectId string = ''

param tags object = {
  application: 'ai-inference-platform'
  environment: environmentName
  managedBy: 'bicep'
}

var suffix = take(uniqueString(resourceGroup().id), 6)
var baseName = toLower('${namePrefix}-${environmentName}-${suffix}')
var compactName = replace(baseName, '-', '')
var identityName = '${baseName}-identity'
var keyVaultName = take('${compactName}kv', 24)
var logAnalyticsName = '${baseName}-logs'
var managedEnvironmentName = empty(managedEnvironmentNameOverride)
  ? '${baseName}-cae'
  : managedEnvironmentNameOverride
var registryName = take('${compactName}acr', 50)

module platform './modules/platform.bicep' = {
  name: 'platform-resources'
  params: {
    location: location
    managedEnvironmentLocation: containerAppsLocation
    logAnalyticsName: logAnalyticsName
    managedEnvironmentName: managedEnvironmentName
    identityName: identityName
    keyVaultName: keyVaultName
    deploymentPrincipalObjectId: deploymentPrincipalObjectId
    tags: tags
  }
}

module registry './modules/registry.bicep' = {
  name: 'registry-resources'
  params: {
    location: location
    registryName: registryName
    identityPrincipalId: platform.outputs.identityPrincipalId
    tags: tags
  }
}

module monitoring './modules/monitoring.bicep' = {
  name: 'monitoring-resources'
  params: {
    location: location
    logAnalyticsWorkspaceId: platform.outputs.logAnalyticsId
    namePrefix: baseName
    alertEmail: monitoringAlertEmail
    enabled: monitoringEnabled
    tags: tags
  }
}

output registryName string = registry.outputs.registryName
output registryLoginServer string = registry.outputs.registryLoginServer
output identityName string = platform.outputs.identityName
output keyVaultName string = platform.outputs.keyVaultName
output managedEnvironmentName string = platform.outputs.managedEnvironmentName
output managedEnvironmentLocation string = platform.outputs.managedEnvironmentLocation
output logAnalyticsName string = platform.outputs.logAnalyticsName
output monitoringNotificationsEnabled bool = monitoring.outputs.notificationsEnabled
