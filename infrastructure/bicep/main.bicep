param location string = 'eastus'
param environment string = 'dev'

// Variables
var postgresqlServerName = 'rentmaster-postgres-${uniqueString(resourceGroup().id)}'
var postgresqlDatabaseName = 'rentmaster_db'

// PostgreSQL Flexible Server
resource postgresqlServer 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {
  name: postgresqlServerName
  location: location
  sku: {
    name: 'Standard_B2s'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: 'pgadmin'
    administratorLoginPassword: 'Rentmaster@2026!'
    version: '15'
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    storage: {
      storageSizeGB: 32
    }
  }
}

// PostgreSQL Database
resource postgresqlDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2022-12-01' = {
  parent: postgresqlServer
  name: postgresqlDatabaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// Firewall rule - Allow Azure services
resource postgresqlFirewallRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2022-12-01' = {
  parent: postgresqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '255.255.255.255'
  }
}

output postgresqlHostname string = postgresqlServer.properties.fullyQualifiedDomainName
output postgresqlDatabaseName string = postgresqlDatabase.name
output postgresqlAdminUser string = 'pgadmin'
