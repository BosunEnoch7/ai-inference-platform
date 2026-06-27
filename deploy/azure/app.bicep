targetScope = 'resourceGroup'

param location string = resourceGroup().location
param containerAppName string = 'ai-inference-platform'
param managedEnvironmentName string
param managedEnvironmentResourceGroup string = resourceGroup().name
param registryName string
param identityName string
param keyVaultName string
param image string
param appVersion string

@allowed([
  'mock'
  'openai'
])
param llmProvider string = 'mock'

param openAIModel string = 'gpt-4.1-mini'
param apiAuthEnabled bool = true
param rateLimitEnabled bool = false
param rateLimitRequests int = 60
param rateLimitWindowSeconds int = 60
param minReplicas int = 1
param maxReplicas int = 3

param tags object = {
  application: 'ai-inference-platform'
  managedBy: 'bicep'
}

resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' existing = {
  name: managedEnvironmentName
  scope: resourceGroup(managedEnvironmentResourceGroup)
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: registryName
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: identityName
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

var openAISecrets = llmProvider == 'openai' ? [
  {
    name: 'openai-api-key'
    keyVaultUrl: '${keyVault.properties.vaultUri}secrets/openai-api-key'
    identity: identity.id
  }
] : []

var authenticationSecrets = apiAuthEnabled ? [
  {
    name: 'inference-api-key'
    keyVaultUrl: '${keyVault.properties.vaultUri}secrets/inference-api-key'
    identity: identity.id
  }
] : []

var redisSecrets = rateLimitEnabled ? [
  {
    name: 'redis-url'
    keyVaultUrl: '${keyVault.properties.vaultUri}secrets/redis-url'
    identity: identity.id
  }
] : []

var secrets = concat(openAISecrets, authenticationSecrets, redisSecrets)

var baseEnvironment = [
  {
    name: 'APP_ENV'
    value: 'production'
  }
  {
    name: 'APP_VERSION'
    value: appVersion
  }
  {
    name: 'LOG_LEVEL'
    value: 'INFO'
  }
  {
    name: 'LLM_PROVIDER'
    value: llmProvider
  }
  {
    name: 'OPENAI_MODEL'
    value: openAIModel
  }
  {
    name: 'API_AUTH_ENABLED'
    value: string(apiAuthEnabled)
  }
  {
    name: 'RATE_LIMIT_ENABLED'
    value: string(rateLimitEnabled)
  }
  {
    name: 'RATE_LIMIT_REQUESTS'
    value: string(rateLimitRequests)
  }
  {
    name: 'RATE_LIMIT_WINDOW_SECONDS'
    value: string(rateLimitWindowSeconds)
  }
  {
    name: 'RATE_LIMIT_FAIL_OPEN'
    value: 'false'
  }
]

var openAIEnvironment = llmProvider == 'openai' ? [
  {
    name: 'OPENAI_API_KEY'
    secretRef: 'openai-api-key'
  }
] : []

var authenticationEnvironment = apiAuthEnabled ? [
  {
    name: 'INFERENCE_API_KEY'
    secretRef: 'inference-api-key'
  }
] : []

var redisEnvironment = rateLimitEnabled ? [
  {
    name: 'REDIS_URL'
    secretRef: 'redis-url'
  }
] : []

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: managedEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        allowInsecure: false
        targetPort: 8000
        transport: 'auto'
      }
      registries: [
        {
          server: registry.properties.loginServer
          identity: identity.id
        }
      ]
      secrets: secrets
    }
    template: {
      containers: [
        {
          name: 'api'
          image: image
          env: concat(
            baseEnvironment,
            openAIEnvironment,
            authenticationEnvironment,
            redisEnvironment
          )
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 10
              periodSeconds: 30
              timeoutSeconds: 3
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/ready'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 5
              periodSeconds: 10
              timeoutSeconds: 3
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-concurrency'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

output containerAppName string = containerApp.name
output fqdn string = containerApp.properties.configuration.ingress.fqdn
output url string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
