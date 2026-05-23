# Multi-stage build for RentMaster Bronze Pipeline
# Used for Azure Container Apps deployment

# ============================================================================
# STAGE 1: Builder
# ============================================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# ============================================================================
# STAGE 2: Runtime
# ============================================================================
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Install ODBC driver for SQL Server (required for pyodbc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY main.py .
COPY requirements.txt .

# Set environment
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Default environment variables (override in Container Apps)
ENV STORAGE_ACCOUNT_NAME=rentmasterstorageaccount \
    CONTAINER_NAME=bronze \
    BLOB_PREFIX=raw/ \
    DB_CONNECTION_STRING=mssql+pyodbc://user:password@server.database.windows.net:1433/rentmaster_db?driver=ODBC+Driver+17+for+SQL+Server \
    EMAIL_FROM=python_pipeline@gmail.com \
    SMTP_SERVER=smtp.gmail.com \
    SMTP_PORT=587 \
    LOG_LEVEL=INFO

# Switch to non-root user
USER appuser

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD echo "OK" || exit 1

# Entry point
ENTRYPOINT ["python", "/app/main.py"]
