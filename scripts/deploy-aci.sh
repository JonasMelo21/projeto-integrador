#!/bin/bash

# Script para rodar container em Azure Container Instances com Key Vault
# Execute após ter executado setup-azure-prod.sh

set -e

RESOURCE_GROUP="rentmaster-prod"
CONTAINER_NAME="scraper-job-$(date +%s)"
ACR_NAME="rentmasteracr"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"
VAULT_NAME="rentmaster-vault"  # ⚠️ AJUSTAR PARA O NOME REAL DO SEU VAULT
LOCATION="eastus"

echo "🚀 Desplorando container em Azure Container Instances"
echo "======================================================"
echo ""
echo "📋 Configuração:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Container: $CONTAINER_NAME"
echo "   Imagem: $ACR_LOGIN_SERVER/scraper:v1.0.0"
echo "   Key Vault: $VAULT_NAME"
echo ""

# ⚠️ AVISO: Para produção, crie Managed Identity + configure RBAC
echo -e "⚠️  NOTA: Este script usa AdminUser do ACR."
echo "   Para produção, crie Managed Identity no ACI"
echo ""

# Obter credenciais ACR
echo "Obtendo credenciais ACR..."
ACR_USERNAME=$(az acr credential show --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" --query "passwords[0].value" -o tsv)

# Obter URL do Key Vault
VAULT_URL="https://${VAULT_NAME}.vault.azure.net/"

echo ""
echo "📤 Criando container no ACI..."
az container create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$CONTAINER_NAME" \
    --image "$ACR_LOGIN_SERVER/scraper:v1.0.0" \
    --registry-login-server "$ACR_LOGIN_SERVER" \
    --registry-username "$ACR_USERNAME" \
    --registry-password "$ACR_PASSWORD" \
    --cpu 2 \
    --memory 4 \
    --restart-policy OnFailure \
    --command-line "python scrapper.py --upload-to-adls" \
    --environment-variables \
        "KEY_VAULT_URL=$VAULT_URL" \
        "ENVIRONMENT=production" \
        "LOG_LEVEL=INFO" \
    --assign-identity \
    --location "$LOCATION"

echo ""
echo -e "✅ Container criado: $CONTAINER_NAME"
echo ""
echo "📊 Para ver logs:"
echo "   az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
echo ""
echo "🔍 Para ver status:"
echo "   az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query instanceView.state"
echo ""
