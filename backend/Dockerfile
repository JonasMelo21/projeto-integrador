FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# Instala curl para o healthcheck (mantido do seu original)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copia o TOML e o LOCK da raiz
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# =====================================================================
# CONFIGURAÇÃO DO PLAYWRIGHT
# 1. Baixa os binários do Chromium usando o ambiente virtual do uv
RUN uv run playwright install chromium
# 2. Instala as dependências de SO (libglib, etc) exigidas pelo Chromium
RUN uv run playwright install-deps chromium
# =====================================================================

# Copia todo o resto do projeto
COPY . .

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=2 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Executa o servidor puxando a main do backend
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]