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

# Executar scraper com args padrão
# Use: docker run -e NUM_PAGES=5 ...
ENTRYPOINT ["sh", "-c", "python scrapper.py --num-pages $NUM_PAGES --format $FORMAT --upload-to-adls"]