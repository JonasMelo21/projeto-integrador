FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -q --upgrade pip setuptools && pip install -q -r requirements.txt

COPY . .

RUN mkdir -p /app/data && chmod 777 /app/data

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=2 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
