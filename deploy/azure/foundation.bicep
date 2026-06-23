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
var managedEnvironmentName = '${baseName}-cae'
var registryName = take('${compactName}acr', 50)

module platform './modules/platform.bicep' = {
  name: 'platform-resources'
  params: {
    location: location
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

output registryName string = registry.outputs.registryName
output registryLoginServer string = registry.outputs.registryLoginServer
output identityName string = platform.outputs.identityName
output keyVaultName string = platform.outputs.keyVaultName
output managedEnvironmentName string = platform.outputs.managedEnvironmentName
output logAnalyticsName string = platform.outputs.logAnalyticsName
