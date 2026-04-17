#!/bin/bash

###############################################################################
# E2E Medallion Pipeline Orchestrator
# Fluxo completo: Scraper (JSON) → ADLS Bronze → Databricks → PostgreSQL
###############################################################################

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "🚀 RentMaster Medallion E2E Pipeline Executor"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="rg_rent_master_dev"
SUBSCRIPTION="c8bb64c0-25e3-4b8e-a99e-262dcdeb7c0b"
STORAGE_ACCOUNT="rentmasterstorageaccount"
POSTGRES_HOST="${POSTGRES_HOST:-rentmaster-postgres-xxxxx.postgres.database.azure.com}"
POSTGRES_USER="pgadmin"
POSTGRES_DB="rentmaster_db"

# Step 0: Verificar Azure CLI
echo -e "${YELLOW}[0/6]${NC} Validando Azure CLI..."
az account show --query name -o tsv > /dev/null || {
  echo -e "${RED}✗ Erro: Não autenticado no Azure. Execute: az login${NC}"
  exit 1
}
echo -e "${GREEN}✓ Azure CLI OK${NC}"

# Step 1: Verificar dados no ADLS Bronze
echo ""
echo -e "${YELLOW}[1/6]${NC} Verificando dados em ADLS/bronze/raw/..."
FILES=$(az storage blob list \
  --container-name bronze \
  --account-name "$STORAGE_ACCOUNT" \
  --prefix raw/ \
  --auth-mode login \
  --query "[].name" -o tsv 2>/dev/null || echo "")

if [ -z "$FILES" ]; then
  echo -e "${RED}✗ Nenhum arquivo JSON encontrado em bronze/raw/${NC}"
  echo "  Solução: Executar o scraper primeiro"
  exit 1
fi

FILE_COUNT=$(echo "$FILES" | wc -l)
echo -e "${GREEN}✓ $FILE_COUNT arquivos encontrados em bronze/raw/${NC}"
echo "  Exemplos:"
echo "$FILES" | head -3 | sed 's/^/    - /'

# Step 2: Verificar PostgreSQL
echo ""
echo -e "${YELLOW}[2/6]${NC} Testando conexão PostgreSQL..."

if [ -z "$POSTGRES_PASSWORD" ]; then
  echo -e "${RED}✗ Erro: POSTGRES_PASSWORD não definido${NC}"
  echo "  Execute: export POSTGRES_PASSWORD=\"sua_senha_aqui\""
  exit 1
fi

PGPASSWORD="$POSTGRES_PASSWORD" psql \
  -h "$POSTGRES_HOST" \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  -c "SELECT version();" > /dev/null 2>&1 || {
  echo -e "${RED}✗ Não conseguiu conectar ao PostgreSQL${NC}"
  echo "  Host: $POSTGRES_HOST"
  echo "  Solução: Verifique credenciais e firewall"
  exit 1
}
echo -e "${GREEN}✓ PostgreSQL conectado${NC}"

# Step 3: Verificar Databricks
echo ""
echo -e "${YELLOW}[3/6]${NC} Verificando Databricks Workspace..."

if [ -z "$DATABRICKS_URL" ] || [ -z "$DATABRICKS_TOKEN" ]; then
  echo -e "${RED}✗ Erro: DATABRICKS_URL ou DATABRICKS_TOKEN não definidos${NC}"
  echo "Execute:"
  echo "  export DATABRICKS_URL=\"https://xxxxx.azuredatabricks.net\""
  echo "  export DATABRICKS_TOKEN=\"dapi...xxxxx\""
  exit 1
fi

curl -s -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  "$DATABRICKS_URL/api/2.1/jobs/list" > /dev/null || {
  echo -e "${RED}✗ Não conseguiu conectar ao Databricks${NC}"
  echo "  Verifique DATABRICKS_TOKEN"
  exit 1
}
echo -e "${GREEN}✓ Databricks conectado${NC}"

# Step 4: Executar pipeline Databricks
echo ""
echo -e "${YELLOW}[4/6]${NC} Executando Databricks Job (Bronze → Silver → Gold)..."
echo "  ⏳ Isso pode levar 15-20 minutos..."

JOB_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": '$(cat databricks/config/job_id.txt 2>/dev/null || echo "0")',
    "notebook_params": {
      "environment": "prod",
      "batch_id": "'$(date +%s)'"
    }
  }' \
  "$DATABRICKS_URL/api/2.1/jobs/run-now")

RUN_ID=$(echo "$JOB_RESPONSE" | grep -o '"run_id":[0-9]*' | cut -d':' -f2 || echo "")

if [ -z "$RUN_ID" ]; then
  echo -e "${RED}✗ Erro ao iniciar Databricks job${NC}"
  echo "  Response: $JOB_RESPONSE"
  exit 1
fi

echo -e "${GREEN}✓ Job iniciado (Run ID: $RUN_ID)${NC}"
echo "  Monitorar em: $DATABRICKS_URL/#job/$RUN_ID"

# Step 5: Aguardar conclusão
echo ""
echo -e "${YELLOW}[5/6]${NC} Aguardando conclusão do job..."

TIMEOUT=1200  # 20 minutos
ELAPSED=0
POLL_INTERVAL=10

while [ $ELAPSED -lt $TIMEOUT ]; do
  JOB_STATUS=$(curl -s -H "Authorization: Bearer $DATABRICKS_TOKEN" \
    "$DATABRICKS_URL/api/2.1/jobs/runs/get?run_id=$RUN_ID" \
    | grep -o '"state":"[^"]*"' | cut -d'"' -f4)
  
  case "$JOB_STATUS" in
    RUNNING)
      echo -n "."
      ;;
    SUCCESS)
      echo ""
      echo -e "${GREEN}✓ Job completado com sucesso!${NC}"
      break
      ;;
    FAILED)
      echo ""
      echo -e "${RED}✗ Job falhou${NC}"
      exit 1
      ;;
    *)
      echo -n "?"
      ;;
  esac
  
  sleep $POLL_INTERVAL
  ELAPSED=$((ELAPSED + POLL_INTERVAL))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
  echo -e "${RED}✗ Timeout esperando job (20 min)${NC}"
  exit 1
fi

# Step 6: Validar dados no PostgreSQL
echo ""
echo -e "${YELLOW}[6/6]${NC} Validando dados em PostgreSQL..."

GOLD_COUNT=$(PGPASSWORD="$POSTGRES_PASSWORD" psql \
  -h "$POSTGRES_HOST" \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  -t -c "SELECT COUNT(*) FROM imoveis_gold;")

IMOB_COUNT=$(PGPASSWORD="$POSTGRES_PASSWORD" psql \
  -h "$POSTGRES_HOST" \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  -t -c "SELECT COUNT(*) FROM dim_imobiliarias;")

LOCATION_COUNT=$(PGPASSWORD="$POSTGRES_PASSWORD" psql \
  -h "$POSTGRES_HOST" \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  -t -c "SELECT COUNT(*) FROM dim_locations;")

echo -e "${GREEN}✓ Dados carregados${NC}"
echo "  imoveis_gold: $GOLD_COUNT registros"
echo "  dim_imobiliarias: $IMOB_COUNT empresas"
echo "  dim_locations: $LOCATION_COUNT localizações"

# Amostra de dados
echo ""
echo "Amostra de dados (top 3 imóveis):"
PGPASSWORD="$POSTGRES_PASSWORD" psql \
  -h "$POSTGRES_HOST" \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  -c "SELECT id_imovel_hex, titulo, preco, quartos, categoria FROM imoveis_gold LIMIT 3;"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ E2E PIPELINE COMPLETO!${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Próximos passos:"
echo "1. Verifique dados em PostgreSQL:"
echo "   psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB"
echo ""
echo "2. Configure scheduled job (opcional):"
echo "   Databricks → Jobs → medallion_job → Trigger"
echo ""
echo "3. Integre com ADF (opcional):"
echo "   Azure Data Factory → Pipelines → Add Databricks Activity"
echo ""
