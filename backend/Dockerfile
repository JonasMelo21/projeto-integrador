FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instalar o curl no Linux (necessário para o healthcheck funcionar)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -q --upgrade pip setuptools && pip install -q -r requirements.txt

# Copiando os arquivos de forma limpa
COPY . .

RUN mkdir -p /app/data && chmod 777 /app/data

# Healthcheck usando o curl recém-instalado
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=2 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]