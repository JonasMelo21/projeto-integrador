# 🚀 E2E Pipeline Medallion - Guia Prático Passo-a-Passo

> **Objetivo**: Mover todos os dados de `ADLS/bronze/raw/` através do Databricks até PostgreSQL

**Tempo estimado**: 30-45 minutos (incluindo execução dos notebooks)

---

## 📋 Pré-Requisitos

- ✅ Azure CLI autenticado (`az login`)
- ✅ 8 arquivos JSON em `rentmasterstorageaccount/bronze/raw/` (seu scraper já fez isso!)
- ✅ Credenciais PostgreSQL (_NOVA_: precisamos delas!)
- ✅ Acesso ao Databricks UI

**Verificar dados no ADLS:**
```bash
az storage blob list \
  --container-name bronze \
  --account-name rentmasterstorageaccount \
  --prefix raw/ \
  --auth-mode login \
  --output table
```

---

## 🎯 Fase 1: Deploy da Infraestrutura (Se ainda não tiver feito)

### Passo 1.1 - Validar Bicep
```bash
cd infrastructure

# Validar sintaxe
az bicep build bicep/main.bicep --outfile /tmp/main.json

# Esperado: "Build successful"
```

### Passo 1.2 - Deploy Databricks + PostgreSQL
```bash
# IMPORTANTE: Este comando criará recursos Azure 
# Tem um CUSTO mensal (~$565)

az deployment group create \
  --name medallion-deploy-$(date +%Y%m%d-%H%M%S) \
  --resource-group rg_rent_master_dev \
  --template-file bicep/main.bicep \
  --parameters parameters.dev.json \
  --query "properties.outputs"

# Salvar outputs (você precisará deles)
az deployment group show \
  --name medallion-deploy-... \
  --resource-group rg_rent_master_dev \
  --query "properties.outputs" > deployment_outputs.json
```

**Isso vai levar 15-30 minutos, crie um café ☕**

### Passo 1.3 - Inicializar PostgreSQL
```bash
# Obter host do arquivo de outputs
POSTGRES_HOST=$(cat deployment_outputs.json | jq -r '.postgresqlHostname.value')

# Carregar schema (tabelas, índices, views)
PGPASSWORD="sua_senha" psql \
  -h "$POSTGRES_HOST" \
  -U pgadmin \
  -d postgres \
  -c "CREATE DATABASE rentmaster_db;"

PGPASSWORD="sua_senha" psql \
  -h "$POSTGRES_HOST" \
  -U pgadmin \
  -d rentmaster_db < infrastructure/sql/schema.sql
```

---

## 💻 Fase 2: Configurar Databricks

### Passo 2.1 - Acessar Workspace
```bash
# Obter URL
DATABRICKS_URL=$(cat deployment_outputs.json | jq -r '.databricksWorkspaceUrl.value')

# Abrir no browser
echo "Acesse: $DATABRICKS_URL"
```

### Passo 2.2 - Fazer Login
- Clique em "Sign up" ou "Log in"
- Use conta Microsoft/Azure AD
- Aceite o workspace

### Passo 2.3 - Criar Cluster
1. No Databricks UI: **Compute** → **+ Create Compute**
2. Nome: `medallion-cluster`
3. Databricks Runtime: `13.3 LTS (Scala 2.12, Spark 3.4.1)`
4. Node Type: `Standard_D4s_v5` (4 cores, 16GB)
5. Workers: Min 1, Max 4
6. Advanced: Auto-terminate after 20 minutes ✅
7. Clique **Create Compute**

**Aguarde ~5 minutos para o cluster iniciar** ⏳

### Passo 2.4 - Upload dos Notebooks
1. No Databricks: **Workspace** → **Create** → **Folder**
   - Nome: `medallion`

2. Na pasta `medallion`, clique **Upload**:
   - Selecione `databricks/notebooks/01_bronze_layer.py`
   - Repita para `02_silver_layer.py` e `03_gold_layer.py`

3. Ou via REST API (avançado):
```bash
DATABRICKS_TOKEN="dapi..." # Gerar em User Settings → Developer → Access Tokens
DATABRICKS_URL="https://xxxxx.azuredatabricks.net"

curl -X POST "$DATABRICKS_URL/api/2.0/workspace/import" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/medallion/01_bronze_layer",
    "format": "SOURCE",
    "language": "PYTHON",
    "content": "'$(cat databricks/notebooks/01_bronze_layer.py | base64 | tr -d '\n')'"
  }'
```

---

## 🔄 Fase 3: Executar Pipeline Manualmente (Primeiro teste)

### Opção A: Via UI (Recomendado para primeira vez)

**Notebook 1 - Bronze Layer:**
1. Abrir: `/medallion/01_bronze_layer`
2. Conectar ao cluster: `medallion-cluster` (dropdown no topo)
3. Selecionar primeira célula
4. Clique **▶ Run** (ou Shift+Enter)
5. Aguarde **2-3 minutos**
6. Esperado: "✓ Loaded XX records to bronze.imoveis_raw"

**Notebook 2 - Silver Layer:**
1. Abrir: `/medallion/02_silver_layer`
2. Conectar ao cluster: `medallion-cluster`
3. Run all cells (ou **⌘A** → **Shift+Enter**)
4. Aguarde **4-5 minutos**
5. Esperado: "✓ Loaded XX qualified records to silver.imoveis_cleaned"

**Notebook 3 - Gold Layer:**
1. Abrir: `/medallion/03_gold_layer`
2. Conectar ao cluster: `medallion-cluster`
3. Run all cells
4. **Importante**: Adicione variáveis de PostgreSQL:
   ```python
   # No início do notebook, substituir:
   postgres_host = "seu_host.postgres.database.azure.com"
   postgres_user = "pgadmin"
   postgres_password = "sua_senha"  # NUNCA commitar isso!
   postgres_db = "rentmaster_db"
   ```
5. Aguarde **6-8 minutos**
6. Esperado: "✓ Upserted XX records to PostgreSQL"

---

### Opção B: Via API (Automático - Avançado)

```bash
# 1. Obter ID da notebook
NOTEBOOK_PATH="/medallion/01_bronze_layer"
CLUSTER_ID="seu_cluster_id"

# 2. Executar notebook
curl -X POST "$DATABRICKS_URL/api/2.1/jobs/runs/submit" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -d '{
    "run_name": "bronze_layer_run",
    "new_cluster": {
      "spark_version": "13.3.x-scala2.12",
      "node_type_id": "Standard_D4s_v5",
      "num_workers": 2
    },
    "notebook_task": {
      "notebook_path": "'$NOTEBOOK_PATH'",
      "base_parameters": {
        "environment": "prod"
      }
    }
  }' | jq '.run_id'

# 3. Monitorar status
RUN_ID="xxxxx"
curl -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  "$DATABRICKS_URL/api/2.1/jobs/runs/get?run_id=$RUN_ID" | jq '.state'
```

---

## ✅ Fase 4: Validar Dados em PostgreSQL

```bash
# Conectar ao PostgreSQL
PGPASSWORD="sua_senha" psql \
  -h "seu_host.postgres.database.azure.com" \
  -U pgadmin \
  -d rentmaster_db

# Dentro do psql:
\dt              -- Listar tabelas (deve ter 4)
\di              -- Listar índices (deve ter 10+)
\dv              -- Listar views (deve ter 5)

SELECT COUNT(*) FROM imoveis_gold;           -- Deve ter > 0
SELECT COUNT(*) FROM dim_imobiliarias;       -- Deve ter >= 1
SELECT COUNT(*) FROM dim_locations;          -- Deve ter >= 1
SELECT COUNT(*) FROM processing_metadata;    -- Deve ter >= 3 (um por notebook)

-- Amostra de dados
SELECT id_imovel_hex, titulo, preco, quartos, categoria 
FROM imoveis_gold 
LIMIT 5;

-- Verificar execuções
SELECT 
  layer, 
  status, 
  rows_processed, 
  rows_inserted,
  duration_minutes
FROM processing_metadata
ORDER BY start_time DESC;

\q              -- Sair
```

### Resultado Esperado:
```
 id_imovel_hex  |             titulo              | preco | quartos | categoria
────────────────┼─────────────────────────────────┼───────┼─────────┼──────────
 b106e792c4fe   | SQNW 108 Bloco D, BRASILIA      | 10900 |       3 | PREMIUM
 7c2bf7dac4f5   | SMPW Quadra 4, PARK WAY         | 26900 |       3 | LUXURY
 ...            | ...                             |   ... |     ... | ...
```

---

## 🎯 Fase 5: Criar Job Agendado (Opcional - Automática Diária)

### Via Databricks UI:
1. **Jobs** → **Create Job**
2. Nome: `medallion_daily_etl`
3. Tasks (adicione 3 em sequência):
   - Task 1: `bronze_layer` → Notebook `/medallion/01_bronze_layer` → Cluster `medallion-cluster`
   - Task 2: `silver_layer` → Notebook `/medallion/02_silver_layer` → Depends On: `bronze_layer`
   - Task 3: `gold_layer` → Notebook `/medallion/03_gold_layer` → Depends On: `silver_layer`
4. Schedule: **Trigger**
   - Frequency: Daily
   - Time: 3:30 AM (30 min após scraper rodar às 3:00 AM)
   - Timezone: `America/Sao_Paulo`
5. Notifications: Email on failure
6. Clique **Create**

---

## 🔗 Fase 6: Integrar com ADF (Opcional - Automática)

Se quiser que o pipeline Databricks rode **automaticamente após o scraper**:

1. No Azure Data Factory:
   - Abrir pipeline `RunScraperContainer`
   - Adicionar activity: **Databricks** → **Notebook**
   - Configurar para rodar após `RunScraperContainer` completa
   - Usar Managed Identity para autenticação

**Mas por agora, Fase 5 (job agendado no Databricks) é suficiente!**

---

## 📊 Verificação Final

Após completar, você deve ter:

Checkbox | Item | Status |
----------|------|--------|
- [ ] | 8 arquivos JSON em `bronze/raw/` | ✅ Scraper fez
- [ ] | Delta table `bronze.imoveis_raw` | ✅ Notebook 1
- [ ] | Delta table `silver.imoveis_cleaned` | ✅ Notebook 2
- [ ] | PostgreSQL com `imoveis_gold` + 7+ registros | ✅ Notebook 3
- [ ] | `dim_imobiliarias` com 1+ empresas | ✅ Notebook 3
- [ ] | `dim_locations` com 1+ bairros | ✅ Notebook 3
- [ ] | `processing_metadata` com 3 execuções | ✅ Notebooks fazem log
- [ ] | Job agendado no Databricks (opcional) | ✅ Fase 5

---

## 🔧 Troubleshooting

### Erro: "Notebook not found"
```
❌ ErrorDetail: notebooks/01_bronze_layer not found
```
**Solução:** Upload os notebooks primeiro (Passo 2.4)

### Erro: "Cluster not started"
```
❌ ClusterNotStarted: Cluster is in state PENDING
```
**Solução:** Aguarde 5-10 min para cluster iniciar

### Erro: "DataFrame not found in silver layer"
```
❌ AnalysisException: Table or view not found: silver.imoveis_cleaned
```
**Solução:** Execute Notebook 1 e 2 antes de rodar Notebook 3

### Erro: "Connection refused to PostgreSQL"
```
❌ psycopg2.OperationalError: FATAL: no pg_hba.conf entry for host "xxx"
```
**Solução:** Adicione IP em firewall PostgreSQL:
```bash
az postgres flexible-server firewall-rule create \
  --name AllowDatabricks \
  --resource-group rg_rent_master_dev \
  --server-name seu_server \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 255.255.255.255
```
*(Não é seguro, use cidr específico em produção)*

---

## 📞 Próximos Passos

1. ✅ **Executar E2E uma vez** (você está aqui)
2. ⏳ **Monitorar segunda execução** (job diário no Databricks)
3. ⏳ **Integrar com ADF** (dispara após scraper)
4. ⏳ **Criar dashboards** (SQL views no PostgreSQL)
5. ⏳ **Deploy do backend FastAPI** (consome PostgreSQL)

---

**Tempo total esperado: ~45 minutos** ⏱️

Qualquer dúvida, consulte `docs/medallion/MEDALLION_DEPLOYMENT_GUIDE.md`
