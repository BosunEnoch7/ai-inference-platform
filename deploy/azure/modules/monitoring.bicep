param location string
param logAnalyticsWorkspaceName string
param logAnalyticsWorkspaceResourceGroup string
param namePrefix string
param alertEmail string = ''
param enabled bool = false
param tags object

var notificationsEnabled = enabled && !empty(alertEmail)

resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = if (notificationsEnabled) {
  name: '${namePrefix}-operations'
  location: 'global'
  tags: tags
  properties: {
    groupShortName: take(replace(namePrefix, '-', ''), 12)
    enabled: true
    emailReceivers: [
      {
        name: 'platform-operations'
        emailAddress: alertEmail
        useCommonAlertSchema: true
      }
    ]
  }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: logAnalyticsWorkspaceName
  scope: resourceGroup(logAnalyticsWorkspaceResourceGroup)
}

resource applicationErrors 'Microsoft.Insights/scheduledQueryRules@2023-12-01' = if (notificationsEnabled) {
  name: '${namePrefix}-application-errors'
  location: location
  tags: tags
  properties: {
    displayName: 'AI inference platform application errors'
    description: 'Application error log entries were detected in Azure Container Apps.'
    severity: 2
    enabled: true
    evaluationFrequency: 'PT5M'
    windowSize: 'PT5M'
    scopes: [
      logAnalytics.id
    ]
    targetResourceTypes: [
      'Microsoft.OperationalInsights/workspaces'
    ]
    criteria: {
      allOf: [
        {
          query: 'ContainerAppConsoleLogs_CL | where Log_s has_any ("ERROR", "CRITICAL")'
          timeAggregation: 'Count'
          operator: 'GreaterThan'
          threshold: 0
          failingPeriods: {
            numberOfEvaluationPeriods: 1
            minFailingPeriodsToAlert: 1
          }
        }
      ]
    }
    autoMitigate: true
    actions: {
      actionGroups: [
        actionGroup.id
      ]
    }
  }
}

resource systemErrors 'Microsoft.Insights/scheduledQueryRules@2023-12-01' = if (notificationsEnabled) {
  name: '${namePrefix}-system-errors'
  location: location
  tags: tags
  properties: {
    displayName: 'AI inference platform container system errors'
    description: 'Container App system warnings or errors were detected.'
    severity: 2
    enabled: true
    evaluationFrequency: 'PT5M'
    windowSize: 'PT5M'
    scopes: [
      logAnalytics.id
    ]
    targetResourceTypes: [
      'Microsoft.OperationalInsights/workspaces'
    ]
    criteria: {
      allOf: [
        {
          query: 'ContainerAppSystemLogs_CL | where Type_s in ("Warning", "Error")'
          timeAggregation: 'Count'
          operator: 'GreaterThan'
          threshold: 0
          failingPeriods: {
            numberOfEvaluationPeriods: 1
            minFailingPeriodsToAlert: 1
          }
        }
      ]
    }
    autoMitigate: true
    actions: {
      actionGroups: [
        actionGroup.id
      ]
    }
  }
}

output notificationsEnabled bool = notificationsEnabled
