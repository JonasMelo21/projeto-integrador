#!/bin/bash

# Script para setup de Managed Identity + Key Vault + ACR para produção
# Execute este script após fazer: az login

set -e

echo "🔧 Setup: Managed Identity, Key Vault, ACR"
echo "==========================================="
echo ""

# Configurações
SUBSCRIPTION_ID="c8bb64c0-25e3-4b8e-a99e-262dcdeb7c0b"
LOCATION="eastus"
RESOURCE_GROUP="rentmaster-prod"
VAULT_NAME="rentmaster-vault-$(date +%s | tail -c 5)"  # Nome único
ACR_NAME="rentmasteracr"
TENANT_ID="dfb66dc4-3f3c-492c-991d-727dbd1c89d4"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 Configurações:${NC}"
echo "   Subscription: $SUBSCRIPTION_ID"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Location: $LOCATION"
echo "   Key Vault: $VAULT_NAME"
echo "   ACR: $ACR_NAME"
echo "   Tenant: $TENANT_ID"
echo ""

# Verificar login
CURRENT_USER=$(az account show --query "user.name" -o tsv 2>/dev/null || echo "")
if [ -z "$CURRENT_USER" ]; then
    echo -e "${RED}❌ Não autenticado. Execute: az login${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Autenticado como: $CURRENT_USER${NC}"
echo ""

# 1️⃣ Criar Resource Group
echo -e "${YELLOW}1️⃣ Criando Resource Group...${NC}"
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --subscription "$SUBSCRIPTION_ID" > /dev/null
echo -e "${GREEN}✅ Resource Group criado${NC}"
echo ""

# 2️⃣ Criar Key Vault
echo -e "${YELLOW}2️⃣ Criando Key Vault...${NC}"
az keyvault create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VAULT_NAME" \
    --location "$LOCATION" \
    --subscription "$SUBSCRIPTION_ID" \
    --enable-soft-delete false > /dev/null
echo -e "${GREEN}✅ Key Vault criado: $VAULT_NAME${NC}"
echo ""

# 3️⃣ Adicionar Secrets ao Key Vault
echo -e "${YELLOW}3️⃣ Adicionando Secrets ao Key Vault...${NC}"

# Ler secretos do arquivo .env
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
ENV_FILE="$PROJECT_ROOT/.env"
WEB_SCRAPING_ENV="$PROJECT_ROOT/workflows/web_scraping/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Arquivo $ENV_FILE não encontrado${NC}"
    exit 1
fi

if [ ! -f "$WEB_SCRAPING_ENV" ]; then
    echo -e "${RED}❌ Arquivo $WEB_SCRAPING_ENV não encontrado${NC}"
    exit 1
fi

# Carregar variáveis
source "$ENV_FILE"
source "$WEB_SCRAPING_ENV"

# Adicionar secrets
echo "   Adicionando AZURE_TENANT_ID..."
az keyvault secret set \
    --vault-name "$VAULT_NAME" \
    --name "AZURE-TENANT-ID" \
    --value "$AZURE_TENANT_ID" \
    --subscription "$SUBSCRIPTION_ID" > /dev/null

echo "   Adicionando AZURE_CLIENT_ID..."
az keyvault secret set \
    --vault-name "$VAULT_NAME" \
    --name "AZURE-CLIENT-ID" \
    --value "$AZURE_CLIENT_ID" \
    --subscription "$SUBSCRIPTION_ID" > /dev/null

echo "   Adicionando AZURE_CLIENT_SECRET..."
az keyvault secret set \
    --vault-name "$VAULT_NAME" \
    --name "AZURE-CLIENT-SECRET" \
    --value "$AZURE_CLIENT_SECRET" \
    --subscription "$SUBSCRIPTION_ID" > /dev/null

echo "   Adicionando STORAGE_ACCOUNT_NAME..."
az keyvault secret set \
    --vault-name "$VAULT_NAME" \
    --name "STORAGE-ACCOUNT-NAME" \
    --value "$STORAGE_ACCOUNT_NAME" \
    --subscription "$SUBSCRIPTION_ID" > /dev/null

echo -e "${GREEN}✅ Secrets adicionados ao Key Vault${NC}"
echo ""

# 4️⃣ Criar ACR
echo -e "${YELLOW}4️⃣ Criando Azure Container Registry...${NC}"
az acr create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$ACR_NAME" \
    --sku Basic \
    --location "$LOCATION" \
    --subscription "$SUBSCRIPTION_ID" \
    --admin-enabled true > /dev/null
echo -e "${GREEN}✅ ACR criado: $ACR_NAME.azurecr.io${NC}"
echo ""

# 5️⃣ Obter credenciais de login ACR
echo -e "${YELLOW}5️⃣ Obtendo credenciais ACR...${NC}"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"
ACR_USERNAME=$(az acr credential show --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" --query "username" -o tsv --subscription "$SUBSCRIPTION_ID")
ACR_PASSWORD=$(az acr credential show --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" --query "passwords[0].value" -o tsv --subscription "$SUBSCRIPTION_ID")

echo -e "${GREEN}✅ Credenciais obtidas${NC}"
echo ""

# 6️⃣ Login no ACR localmente
echo -e "${YELLOW}6️⃣ Fazendo login no ACR localmente...${NC}"
echo "$ACR_PASSWORD" | docker login -u "$ACR_USERNAME" --password-stdin "$ACR_LOGIN_SERVER" > /dev/null
echo -e "${GREEN}✅ Logado no ACR${NC}"
echo ""

# 7️⃣ Tag e push da imagem
echo -e "${YELLOW}7️⃣ Preparando push da imagem...${NC}"
IMAGE_TAG="${ACR_LOGIN_SERVER}/scraper:v1.0.0"
docker tag rentmaster-scraper:prod "$IMAGE_TAG"
echo "   Tag: $IMAGE_TAG"
echo ""

echo -e "${YELLOW}📤 Fazendo push da imagem (pode levar alguns minutos)...${NC}"
docker push "$IMAGE_TAG"
echo -e "${GREEN}✅ Imagem enviada para ACR${NC}"
echo ""

# Resumo
echo "=================================================="
echo -e "${GREEN}✅ SETUP CONCLUÍDO COM SUCESSO!${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}📝 Informações para usar em produção:${NC}"
echo ""
echo "🔑 Key Vault:"
echo "   Nome: $VAULT_NAME"
echo "   URL: https://${VAULT_NAME}.vault.azure.net/"
echo ""
echo "📦 ACR:"
echo "   Servidor: $ACR_LOGIN_SERVER"
echo "   Imagem: $IMAGE_TAG"
echo ""
echo "🐳 Executar container em ACI:"
echo "   az container create \\"
echo "     --resource-group $RESOURCE_GROUP \\"
echo "     --name scraper-job \\"
echo "     --image $IMAGE_TAG \\"
echo "     --registry-login-server $ACR_LOGIN_SERVER \\"
echo "     --registry-username $ACR_USERNAME \\"
echo "     --registry-password '$ACR_PASSWORD' \\"
echo "     --environment-variables KEY_VAULT_URL=https://${VAULT_NAME}.vault.azure.net/ \\"
echo "     --assign-identity"
echo ""
echo -e "${YELLOW}💾 Salve essas informações para usar no ADF pipeline!${NC}"
echo ""
