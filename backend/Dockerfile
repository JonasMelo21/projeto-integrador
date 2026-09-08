FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# Instala curl para o healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copia o TOML e o LOCK da raiz (deps serão cache-friendly)
COPY pyproject.toml uv.lock ./

# Instala apenas dependências do backend (sem dev, sem ml_pipeline, sem data_pipeline)
RUN uv sync --frozen --no-install-project --group backend

# Copia apenas o necessário (backend + ml_pipeline/models)
COPY backend ./backend
COPY ml_pipeline/models ./ml_pipeline/models

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=2 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Executa o servidor
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]