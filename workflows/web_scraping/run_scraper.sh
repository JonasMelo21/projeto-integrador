#!/bin/bash
# Rodar Scraper com variáveis de ambiente carregadas

set -e

cd "$(dirname "$0")"

echo "📦 Carregando variáveis de ambiente..."
# Carregar .env raiz e do scraper (ignorando comentários e linhas vazias)
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
export $(cat ./scrapper/.env | grep -v '^#' | grep -v '^$' | xargs)

echo "✓ Variáveis carregadas:"
echo "  AZURE_TENANT_ID: ${AZURE_TENANT_ID:0:10}..."
echo "  AZURE_CLIENT_ID: ${AZURE_CLIENT_ID:0:10}..."
echo "  STORAGE_ACCOUNT_NAME: $STORAGE_ACCOUNT_NAME"

echo ""
echo "🚀 Iniciando container do scraper..."
docker-compose --profile scraper up --build scraper
