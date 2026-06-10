#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE="rentmasteracr.azurecr.io/rentmaster/scraper:latest"

echo "🔐 RentMaster Scraper - Executar Localmente"
echo ""

# 1. Verificar e fazer login no Azure
if [ ! -f "$HOME/.azure/accessTokens.json" ]; then
    echo "❌ Azure CLI não autenticado"
    echo "📝 Executando: az login"
    az login
else
    echo "✅ Credenciais Azure encontradas"
fi
echo ""

# 2. Rebuild imagem
echo "🏗️  Rebuilding Docker image..."
docker build -t "$IMAGE" "$SCRIPT_DIR"
echo ""

# 3. Executar container com credenciais
echo "🚀 Iniciando container com Managed Identity..."
docker run -it \
    --rm \
    -e NUM_PAGES=1 \
    -e FORMAT=json \
    -e TIMEOUT_MS=45000 \
    -e STORAGE_ACCOUNT_NAME=rentmasterstorageaccount \
    -v "$HOME/.azure:/root/.azure:ro" \
    "$IMAGE"
