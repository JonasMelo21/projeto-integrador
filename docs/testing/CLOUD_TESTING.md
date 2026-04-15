# Teste E2E em Cloud - Pipeline Scraper

> **Documentação para testes do módulo Scraper integrado ao Azure Data Factory e Data Lake**

## 📋 Visão Geral do Teste E2E

O pipeline `RunScraperContainer` executa as seguintes etapas:

1. **Disparo** → Ativa um container no ACR
2. **Execução** → Container executa web scraping (DFimoveis)
3. **Escrita** → Dados brutos salvos em `bronze/raw/` do ADLS Gen2
4. **Validação** → Verificar se arquivos JSON foram criados

---

## 🔍 Recursos Azure Referenciais

Substitua pelos valores reais do seu projeto:

| Recurso | Valor | Descrição |
|---------|-------|-----------|
| `SUBSCRIPTION_ID` | `c8bb64c0-25e3-4b8e-a99e-262dcdeb7c0b` | ID da subscription Azure |
| `RESOURCE_GROUP` | `rg_rent_master_dev` | Resource group que contém os recursos |
| `ADF_NAME` | `rentmaster-dataFactory` | Nome do Azure Data Factory |
| `PIPELINE_NAME` | `RunScraperContainer` | Nome do pipeline |
| `ACR_NAME` | `rentmasteracr` | Nome do Azure Container Registry |
| `STORAGE_ACCOUNT` | `rentmasterstorageaccount` | Nome da Storage Account Gen2 |

---

## 🚀 Teste Rápido (5 min)

### Passo 1: Login na Azure
```bash
az login
az account set --subscription "c8bb64c0-25e3-4b8e-a99e-262dcdeb7c0b"
```

### Passo 2: Validar Recursos
```bash
# Ver ACR
az acr show -n rentmasteracr --resource-group rg_rent_master_dev

# Ver Storage Account
az storage account show -n rentmasterstorageaccount

# Ver Data Factory
az datafactory show -n rentmaster-dataFactory --resource-group rg_rent_master_dev
```

### Passo 3: Listar Pipelines
```bash
az datafactory pipeline list \
  --resource-group rg_rent_master_dev \
  --factory-name rentmaster-dataFactory \
  --output table
```

### Passo 4: Disparar Pipeline
```bash
RUN_ID=$(az datafactory pipeline create-run \
  --resource-group rg_rent_master_dev \
  --factory-name rentmaster-dataFactory \
  --name RunScraperContainer \
  --query runId -o tsv)

echo "Pipeline disparado com RUN_ID: $RUN_ID"
```

### Passo 5: Monitorar Status (atualização a cada 15s)
```bash
while true; do
  STATUS=$(az datafactory pipeline-run show \
    --resource-group rg_rent_master_dev \
    --factory-name rentmaster-dataFactory \
    --run-id "$RUN_ID" \
    --query status -o tsv)
  
  echo "[$(date +%H:%M:%S)] Status: $STATUS"
  
  if [[ "$STATUS" == "Succeeded" || "$STATUS" == "Failed" || "$STATUS" == "Cancelled" ]]; then
    break
  fi
  
  sleep 15
done
```

### Passo 6: Ver Resultado Final
```bash
az datafactory pipeline-run show \
  --resource-group rg_rent_master_dev \
  --factory-name rentmaster-dataFactory \
  --run-id "$RUN_ID" \
  --output table
```

### Passo 7: Validar Dados no ADLS
```bash
# Listar arquivos em bronze/raw/
az storage fs file list \
  --account-name rentmasterstorageaccount \
  --file-system bronze \
  --path raw \
  --auth-mode login \
  --output table
```

---

## 🔧 Teste Completo (Script Automático)

Salve e execute este script para rodar o teste E2E completo:

```bash
#!/bin/bash
set -e

# Configuração
SUBSCRIPTION_ID="c8bb64c0-25e3-4b8e-a99e-262dcdeb7c0b"
RESOURCE_GROUP="rg_rent_master_dev"
ADF_NAME="rentmaster-dataFactory"
PIPELINE_NAME="RunScraperContainer"
ACR_NAME="rentmasteracr"
STORAGE_ACCOUNT="rentmasterstorageaccount"

echo "================================"
echo "TESTE E2E - PIPELINE SCRAPER"
echo "================================"
echo ""

# 1. Configurar subscription
echo "1️⃣  Configurando subscription..."
az account set --subscription "$SUBSCRIPTION_ID"
echo ""

# 2. Validar recursos
echo "2️⃣  Validando Recursos..."
echo "   ACR:"
az acr show -n "$ACR_NAME" --resource-group "$RESOURCE_GROUP" --query '{name:name, loginServer:loginServer}' -o table

echo "   Storage Account:"
az storage account show -n "$STORAGE_ACCOUNT" --query '{name:name, kind:kind}' -o table

echo "   Data Factory:"
az datafactory show -n "$ADF_NAME" --resource-group "$RESOURCE_GROUP" --query '{name:name}' -o table
echo ""

# 3. Disparar Pipeline
echo "3️⃣  Disparando Pipeline..."
RUN_ID=$(az datafactory pipeline create-run \
  --resource-group "$RESOURCE_GROUP" \
  --factory-name "$ADF_NAME" \
  --name "$PIPELINE_NAME" \
  --query runId -o tsv)

echo "   ✓ RUN_ID: $RUN_ID"
echo ""

# 4. Monitorar (máx 10 minutos)
echo "4️⃣  Monitorando Pipeline..."
TIMEOUT=600
ELAPSED=0
INTERVAL=15

while [ $ELAPSED -lt $TIMEOUT ]; do
  STATUS=$(az datafactory pipeline-run show \
    --resource-group "$RESOURCE_GROUP" \
    --factory-name "$ADF_NAME" \
    --run-id "$RUN_ID" \
    --query status -o tsv)
  
  ELAPSED=$((ELAPSED + INTERVAL))
  echo "   [$ELAPSED s] Status: $STATUS"
  
  if [[ "$STATUS" == "Succeeded" || "$STATUS" == "Failed" ]]; then
    break
  fi
  sleep $INTERVAL
done

echo ""

# 5. Resultado
echo "5️⃣  Resultado Final:"
az datafactory pipeline-run show \
  --resource-group "$RESOURCE_GROUP" \
  --factory-name "$ADF_NAME" \
  --run-id "$RUN_ID" \
  --query '{status:status, runId:runId}' -o table

echo ""

# 6. Atividades da execução
echo "6️⃣  Atividades:"
AFTER=$(date -u -d "1 hour ago" +"%Y-%m-%dT%H:%M:%SZ")
BEFORE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

az datafactory activity-run query-by-pipeline-run \
  --resource-group "$RESOURCE_GROUP" \
  --factory-name "$ADF_NAME" \
  --run-id "$RUN_ID" \
  --last-updated-after "$AFTER" \
  --last-updated-before "$BEFORE" \
  --query '[].{name:output.activityName, status:output.status}' -o table

echo ""

# 7. Validar dados no ADLS
echo "7️⃣  Validando ADLS Gen2..."
echo "   Files em bronze/raw/:"
az storage fs file list \
  --account-name "$STORAGE_ACCOUNT" \
  --file-system bronze \
  --path raw \
  --auth-mode login --output table

echo ""
echo "✅ Teste E2E Concluído!"
```

---

## ✅ Checklist de Sucesso

- [ ] Subscription configurada corretamente
- [ ] ACR, Storage Account e ADF acessíveis
- [ ] Pipeline disparado com sucesso
- [ ] RUN_ID retornado
- [ ] Status final = "Succeeded"
- [ ] Atividades do container executadas sem erro
- [ ] Arquivos JSON encontrados em `bronze/raw/`
- [ ] Arquivo JSON tem conteúdo (tamanho > 0 bytes)

---

## 🚨 Troubleshooting

### Erro: "Pipeline not found"
```bash
# Verificar se o nome do pipeline está correto
az datafactory pipeline list --resource-group rg_rent_master_dev --factory-name rentmaster-dataFactory
```

### Erro: "Access denied" (Storage/ACR)
- Verificar permissões RBAC da identidade:
  - `ACR pull` para puxa imagem
  - `Storage Blob Data Contributor` para escrever em bronze/raw
```bash
# Ver permissões
az role assignment list \
  --resource-group rg_rent_master_dev \
  --output table
```

### Pipeline Falha (Status = "Failed")
```bash
# Ver logs detalhados das atividades
az datafactory activity-run query-by-pipeline-run \
  --resource-group rg_rent_master_dev \
  --factory-name rentmaster-dataFactory \
  --run-id "$RUN_ID" \
  --last-updated-after "$(date -u -d '2 hours ago' +%Y-%m-%dT%H:%M:%SZ)" \
  --last-updated-before "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --output json | jq '.[].output | select(.status != "Succeeded")'
```

### Nenhum arquivo em bronze/raw
- [ ] Container `bronze` existe?
```bash
az storage fs list --account-name rentmasterstorageaccount --auth-mode login
```

- [ ] Pasta `raw/` foi criada?
```bash
az storage fs directory exists \
  --account-name rentmasterstorageaccount \
  --file-system bronze \
  --path raw \
  --auth-mode login
```

---

## 📊 Validação de Dados

Após sucesso, validar qualidade dos dados:

```bash
# 1. Contar arquivos
FILE_COUNT=$(az storage fs file list \
  --account-name rentmasterstorageaccount \
  --file-system bronze \
  --path raw \
  --auth-mode login \
  --query 'length(@)' -o tsv)

echo "Total de arquivos: $FILE_COUNT"

# 2. Ver tamanho total
az storage fs file list \
  --account-name rentmasterstorageaccount \
  --file-system bronze \
  --path raw \
  --auth-mode login \
  --query '[].properties.contentLength' -o json | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Total: {sum(data)} bytes ({sum(data)/1024/1024:.2f} MB)')"

# 3. Verificar estrutura de um arquivo JSON
az storage blob download \
  --account-name rentmasterstorageaccount \
  --container-name bronze \
  --name "raw/imoveis_latest.json" \
  --file /tmp/sample.json \
  --auth-mode login

head -50 /tmp/sample.json
```

---

## 🔄 Pipeline Recorrente (Agendado)

Se o pipeline está agendado para rodar diariamente, você pode:

1. **Aguardar execução agendada** (verificar horário em ADF)
2. **Disparar manual** (como acima)
3. **Modificar trigger** (se precisar mudar horário/frequência)

```bash
# Ver triggers do pipeline
az datafactory trigger list \
  --resource-group rg_rent_master_dev \
  --factory-name rentmaster-dataFactory \
  --output table
```

---

## 📝 Próximos Passos

1. ✅ Validar dados em `bronze/raw/`
2. → Processar em `silver/` (Databricks/PySpark)
3. → Curar para `gold/` (Analytics-ready)
4. → Consumir em BI + API (FastAPI)
5. → Treinar ML Model (XGBoost)
6. → Deploy em produção

