# Dockerfile - RentMaster Scraper Module
# ⚠️  ESTE É O ÚNICO DOCKERFILE ENVIADO PARA ACR
# Backend e Frontend rodam com docker compose localmente

FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy
# Microsoft-maintained Playwright image com todas as dependências do SO pré-instaladas

# Metadados
LABEL maintainer="RentMaster Dev Team"
LABEL description="RentMaster Scraper - Extrai imóveis da DFimoveis.com.br"
LABEL version="1.0.0"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TIMEOUT_MS=45000 \
    NUM_PAGES=2 \
    FORMAT=json

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools

# Diretório de trabalho
WORKDIR /app

# Instalar Azure CLI (para DefaultAzureCredential funcionar localmente)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg lsb-release ca-certificates \
    && curl -sL https://aka.ms/InstallAzureCLIDeb | bash \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências de scraping
RUN pip install --no-cache-dir beautifulsoup4 playwright azure-storage-blob azure-identity

# Install Playwright browsers (essencial!)
RUN playwright install chromium

# Copiar código do scraper
COPY scrapper.py .

# Criar diretório de output
RUN mkdir -p /app/data && chmod 777 /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=2 \
    CMD python -c "print('OK')" || exit 1

# Criar script entry point com suporte a Managed Identity + Azure CLI
RUN cat > /app/entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 RentMaster Scraper - Iniciando..."
echo ""
echo "📋 Configuração:"
echo "   NUM_PAGES=${NUM_PAGES:-2}"
echo "   FORMAT=${FORMAT:-json}"
echo "   TIMEOUT_MS=${TIMEOUT_MS:-45000}"
echo "   STORAGE_ACCOUNT=${STORAGE_ACCOUNT_NAME:-rentmasterstorageaccount}"
echo "   TENANT_ID=${AZURE_TENANT_ID:0:12}..." || echo "   TENANT_ID: (não configurado)"
echo ""

# Verificar se credenciais estão configuradas
echo "🔐 Verificando credenciais Azure..."
if [ -n "$AZURE_TENANT_ID" ] && [ -n "$AZURE_CLIENT_ID" ] && [ -n "$AZURE_CLIENT_SECRET" ]; then
    echo "   ✓ Service Principal via variáveis de ambiente"
    echo ""
    
    # Validar credenciais (modo test)
    echo "📝 Validando credenciais..."
    python scrapper.py --validate-credentials --storage-account "${STORAGE_ACCOUNT_NAME:-rentmasterstorageaccount}" || {
        echo ""
        echo "⚠️  Erro na validação de credenciais"
        echo "   Continuando com modo permissivo (--skip-on-error)..."
    }
else
    echo "   ⚠️  Credenciais não completamente configuradas"
    echo "   Esperando: AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET"
    echo ""
fi

echo ""

# Executar scraper com modo permissivo (continua mesmo se falhar upload)
python scrapper.py \
    --num-pages "${NUM_PAGES:-2}" \
    --format "${FORMAT:-json}" \
    --timeout-ms "${TIMEOUT_MS:-45000}" \
    --upload-to-adls \
    --storage-account "${STORAGE_ACCOUNT_NAME:-rentmasterstorageaccount}" \
    --skip-on-error

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Scraper finalizado com sucesso!"
else
    echo "⚠️  Scraper finalizado com avisos (código: $EXIT_CODE)"
fi

exit $EXIT_CODE
EOF
RUN chmod +x /app/entrypoint.sh

# Executar scraper via script de entrada
ENTRYPOINT ["/app/entrypoint.sh"]