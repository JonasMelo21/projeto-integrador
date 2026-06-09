# 🚀 Setup Local & Cloud Testing Guide

> **Como rodar o projeto localmente (sem Docker e com Docker) e testar tudo na nuvem (Azure Cloud)**.

---

## ⚡ Quick Start Local (Sem Docker)

### Pré-requisitos
```bash
python3 -m venv backend/.venv_clean
source backend/.venv_clean/bin/activate
pip install -q -r backend/requirements.txt
```

### Terminal 1: Backend
```bash
cd backend
source .venv_clean/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Esperado:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Frontend
```bash
cd frontend
python -m http.server 5173
```

Esperado:
```
Serving HTTP on 0.0.0.0 port 5173
```

### Abrir no navegador
```
http://localhost:5173
```

---

## 🐳 Com Docker

### Build e Iniciar
```bash
docker compose build
docker compose up
```

Esperado:
```
backend    | INFO:     Application startup complete.
frontend   | [1] signal 17 (sigchld)
```

### Acessar
```
Frontend: http://localhost:5173
Backend:  http://localhost:8000/docs
```

### Ver Logs
```bash
docker compose logs -f backend      # Logs do backend
docker compose logs -f frontend     # Logs do frontend
docker compose logs                 # Todos os logs
```

### Parar Containers
```bash
docker compose down                 # Para e remove containers
docker compose down -v              # Remove também volumes
```

---

## ✅ Testes Locais

### Backend Health
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### API de Imóveis
```bash
curl http://localhost:8000/api/imoveis?limit=2 | jq
```

Esperado:
```json
[
  {
    "id_imovel": 1,
    "titulo": "SQNW 108 Bloco D",
    "endereco": "NOROESTE, BRASILIA",
    "preco": 10900.0,
    "area": 150.0,
    ...
  }
]
```

### API de Estatísticas
```bash
curl http://localhost:8000/api/imoveis/stats | jq
```

### Frontend
```bash
# Abrir em navegador
http://localhost:5173

# Grid com 240 imóveis deve aparecer
# Busca deve funcionar em tempo real
# Clique em um imóvel para ver detalhes
```

---

## 🔄 Dados do ADLS

### Carregar 240 imóveis
```bash
cd backend
python scripts/load_from_adls.py
```

Esperado:
```
✅ Carregando configurações...
✅ Banco inicializado
✅ Total carregado: 240 imóveis
```

### Verificar dados no SQLite
```bash
sqlite3 backend/rental.db "SELECT COUNT(*) FROM fact_imoveis;"
# 240
```

---

## ☁️ Testes na Cloud (Azure)

### Pré-requisito: Azure CLI instalado
```bash
az --version  # Deve mostrar versão

# Fazer login
az login
```

### 1️⃣ Verificar Recursos do RG

#### Listar todos os recursos
```bash
az resource list -g rg_rent_master_dev --query "[].{name:name, type:type}" -o table
```

Esperado:
```
Name                              Type
────────────────────────────────────────────────────────────
rentmaster-dev-scraper-job        Microsoft.App/jobs
rentmasteracr                     Microsoft.ContainerRegistry/registries
rentmasterstorageaccount          Microsoft.Storage/storageAccounts
rentmaster-dev-etl-func           Microsoft.Web/sites
rentmastersqlserver               Microsoft.Sql/servers
rentmaster-kv-dev                 Microsoft.KeyVault/vaults
rentmaster-dev-insights           Microsoft.Insights/components
```

#### Verificar Container Apps Job
```bash
az containerapp job show \
  -g rg_rent_master_dev \
  -n rentmaster-dev-scraper-job \
  --query "{name:name, image:properties.template.containers[0].image, status:properties.provisioningState}" \
  -o json
```

---

### 2️⃣ Teste do Scraper no ACA

#### Executar o Scraper Manualmente
```bash
# Iniciar job
az containerapp job start \
  -g rg_rent_master_dev \
  -n rentmaster-dev-scraper-job
```

#### Monitorar Execução
```bash
# Aguarde 10 segundos
sleep 10

az containerapp job execution list \
  -g rg_rent_master_dev \
  -n rentmaster-dev-scraper-job \
  --query "[0].{name:name, status:properties.status, startTime:properties.startTime, endTime:properties.endTime}" \
  -o json
```

Esperado:
```json
{
  "name": "rentmaster-dev-scraper-job-u9dygue",
  "status": "Succeeded",
  "startTime": "2026-05-13T20:13:13+00:00",
  "endTime": "2026-05-13T20:14:11+00:00"
}
```

---

### 3️⃣ Teste do ADLS (Bronze Layer)

#### Listar Blobs em bronze/raw/
```bash
RG=rg_rent_master_dev
STORAGE=rentmasterstorageaccount
KEY=$(az storage account keys list -g $RG -n $STORAGE --query "[0].value" -o tsv)

az storage blob list \
  --account-name $STORAGE \
  --account-key "$KEY" \
  --container-name bronze \
  --prefix raw/ \
  --query "[].{name:name, lastModified:properties.lastModified, size:properties.contentLength}" \
  -o json | jq 'sort_by(.lastModified) | reverse | .[0:3]'
```

Esperado (3 arquivos mais recentes):
```json
[
  {
    "lastModified": "2026-05-13T20:14:05+00:00",
    "name": "raw/imoveis_20260513_201402.json",
    "size": 24243
  },
  {
    "lastModified": "2026-05-13T03:01:12+00:00",
    "name": "raw/imoveis_20260513_030108.json",
    "size": 24268
  }
]
```

#### Contar Blobs em bronze
```bash
RG=rg_rent_master_dev
STORAGE=rentmasterstorageaccount
KEY=$(az storage account keys list -g $RG -n $STORAGE --query "[0].value" -o tsv)

az storage blob list \
  --account-name $STORAGE \
  --account-key "$KEY" \
  --container-name bronze \
  --prefix raw/ | jq 'length'
```

#### Verificar Silver e Gold (quando prontos)
```bash
# Silver layer
az storage blob list --account-name $STORAGE --account-key "$KEY" --container-name silver --prefix "date=" | jq length

# Gold layer
az storage blob list --account-name $STORAGE --account-key "$KEY" --container-name gold --prefix "date=" | jq length
```

---

### 4️⃣ Teste do Azure SQL (quando pronto)

#### Contar registros em fact_imoveis
```bash
# Obter credenciais
SQL_SERVER=$(az sql server show -g rg_rent_master_dev -n rentmastersqlserver --query fullyQualifiedDomainName -o tsv)
SQL_ADMIN=$(az sql server show -g rg_rent_master_dev -n rentmastersqlserver --query administratorLogin -o tsv)
SQL_PASSWORD=$(az keyvault secret show --vault-name rentmaster-kv-dev --name sql-admin-password --query value -o tsv)

echo "Connection: $SQL_SERVER"

# Query com sqlcmd (se instalado)
sqlcmd -S "$SQL_SERVER" -U "$SQL_ADMIN@${SQL_SERVER%.*}" -P "$SQL_PASSWORD" -d rentmasterdb -Q "SELECT COUNT(*) as total FROM dbo.fact_imoveis"
```

---

## 📊 Testes Completos (Ponta a Ponta)

### Checklist: Testar Toda a Pipeline

```bash
echo "=== LOCAL TESTING ==="
# 1. Backend
curl -s http://localhost:8000/health | jq && echo "✅ Backend OK" || echo "❌ Backend FAIL"

# 2. Frontend
curl -s http://localhost:5173 | head -c 50 && echo "✅ Frontend OK" || echo "❌ Frontend FAIL"

# 3. Dados no SQLite
SQLITE_COUNT=$(sqlite3 backend/rental.db "SELECT COUNT(*) FROM fact_imoveis;" 2>/dev/null)
echo "✅ SQLite tem $SQLITE_COUNT imóveis"

echo -e "\n=== CLOUD TESTING ==="

# 4. Container Apps Job
JOB_STATUS=$(az containerapp job show -g rg_rent_master_dev -n rentmaster-dev-scraper-job --query properties.provisioningState -o tsv)
echo "✅ Job status: $JOB_STATUS"

# 5. ACR tem imagem?
ACR_IMAGE=$(az acr repository show -n rentmasteracr --repository scraper --query name -o tsv 2>/dev/null)
echo "✅ ACR image: $ACR_IMAGE"

# 6. ADLS storage
BLOB_COUNT=$(RG=rg_rent_master_dev && STORAGE=rentmasterstorageaccount && KEY=$(az storage account keys list -g $RG -n $STORAGE --query "[0].value" -o tsv) && az storage blob list --account-name $STORAGE --account-key "$KEY" --container-name bronze --prefix raw/ 2>/dev/null | jq length)
echo "✅ ADLS tem $BLOB_COUNT blobs em bronze/raw/"

echo -e "\n✅ Todos os componentes estão prontos!"
```

---

## 🚧 O Que Falta - Próximos Passos (Sprint 3)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check |
| GET | `/api/imoveis` | Lista imóveis (paginado) |
| GET | `/api/imoveis/{id}` | Detalhes de um imóvel |
| GET | `/api/imoveis/stats` | Estatísticas gerais |
| GET | `/api/dimensoes/imobiliarias` | Lista de imobiliárias |
| GET | `/api/dimensoes/locais` | Lista de localidades |

---

## 🔧 Variáveis de Ambiente

### backend/scripts/.env.adls
```
AZURE_STORAGE_ACCOUNT=rentmasterstorageaccount
AZURE_STORAGE_KEY=<sua_chave_aqui>
ADLS_CONTAINER=bronze
ADLS_PATH=raw/
```

### Carregar do ADLS
Arquivos disponíveis em `bronze/raw/`:
```
imoveis_20260408_183715.json (30 imóveis)
imoveis_20260414_195102.json (31 imóveis)
imoveis_20260414_221801.json (29 imóveis)
imoveis_20260414_222407.json (29 imóveis)
imoveis_20260414_222843.json (29 imóveis)
imoveis_20260414_224008.json (29 imóveis)
imoveis_20260415_060240.json (29 imóveis)
imoveis_20260415_132527.json (30 imóveis) ← Mais recente
─────────────────────────────────────
Total: 240 imóveis
```

---

## 🐛 Troubleshooting

### Port em uso
```bash
lsof -i :8000 | awk 'NR!=1 {print $2}' | xargs kill -9
lsof -i :5173 | awk 'NR!=1 {print $2}' | xargs kill -9
```

### Backend não responde
```bash
docker compose logs backend
docker compose restart backend
```

### Sem dados no frontend
```bash
# Verifique se os dados foram carregados
sqlite3 backend/rental.db "SELECT COUNT(*) FROM fact_imoveis;"

# Se vazio, carregar:
python backend/scripts/load_from_adls.py
```

### ModuleNotFoundError
```bash
# Certifique-se que está na pasta backend/
cd backend
python scripts/load_from_adls.py  # ✅ Correto
```

### Docker não encontrado
Instale em: https://www.docker.com/products/docker-desktop

---

## 📁 Estrutura de Arquivos

```
backend/
├── Dockerfile                    # Container FastAPI
├── requirements.txt              # Dependências
├── main.py                       # Aplicação
├── database.py                   # Setup ORM
├── models.py                     # Modelos
├── routes/
│   ├── imoveis.py               # GET /api/imoveis
│   └── dimensoes.py             # GET /api/dimensoes
└── scripts/
    ├── load_from_adls.py        # Carrega dados do ADLS
    └── .env.adls                # Credenciais Azure

frontend/
├── Dockerfile                    # Container Nginx
├── nginx.conf                    # Config Nginx
├── index.html                    # UI
├── style.css                     # Estilos
└── script.js                     # Lógica

scrapper/
├── Dockerfile                    # Container scraper (→ ACR)
├── scrapper.py                   # Scraper principal
└── debug_scraper.py              # Debug tools

docker-compose.yml               # Orquestração
```

---

## 📝 Resumo de Comandos

| Tarefa | Comando |
|--------|---------|
| Setup local | `python3 -m venv backend/.venv_clean && source backend/.venv_clean/bin/activate && pip install -r backend/requirements.txt` |
| Carregar dados | `python backend/scripts/load_from_adls.py` |
| Backend local | `cd backend && uvicorn main:app --reload` |
| Frontend local | `cd frontend && python -m http.server 5173` |
| Docker build | `docker compose build` |
| Docker up | `docker compose up` |
| Docker logs | `docker compose logs -f backend` |
| Docker down | `docker compose down` |
| Testar API | `curl http://localhost:8000/api/imoveis?limit=2` |

---

## ✅ Checklist antes de começar

- [ ] Python 3.11+ instalado
- [ ] Docker Desktop instalado (se usar containers)
- [ ] Arquivo `backend/scripts/.env.adls` configurado
- [ ] Portas 8000 e 5173 livres
- [ ] ~500MB de espaço em disco (dados + containers)
- [ ] Leu [CONTEXT.md](../CONTEXT.md) (regras de código)
- [ ] Leu [docs/STRUCTURE.md](STRUCTURE.md) (estrutura do projeto)

---

## 📚 Próximas Leituras

| Documento | Quando ler |
|-----------|-----------|
| [CONTEXT.md](../CONTEXT.md) | Antes de programar |
| [docs/STRUCTURE.md](STRUCTURE.md) | Antes de começar (entender arquitetura) |
| [docs/OVERVIEW.md](OVERVIEW.md) | Para panorama geral |
| [docs/guides/SCRAPER.md](guides/SCRAPER.md) | Se vai trabalhar com scraper |
| [docs/guides/BACKEND.md](guides/BACKEND.md) | Se vai trabalhar com FastAPI |
| [docs/testing/CLOUD_TESTING.md](testing/CLOUD_TESTING.md) | Para testes avançados em cloud |
| [docs/medallion/E2E_EXECUTION_GUIDE.md](medallion/E2E_EXECUTION_GUIDE.md) | Para entender pipeline completo |

---

## 🎯 Próximos Passos (Sprint 3)

Após validar que tudo funciona localmente:

### 1. Azure Function (Bronze → Silver ETL)
- [ ] Criar Azure Function Python
- [ ] Implementar normalização de campos
- [ ] Conectar com Event Grid em ADLS

### 2. Silver Layer Schema
- [ ] Definir Parquet schema normalizado
- [ ] Implementar particionamento por data

### 3. Gold Layer & SQL Upsert
- [ ] Feature engineering
- [ ] Star schema em SQL
- [ ] Pipeline SQL Serverless

Leia: [docs/medallion/E2E_EXECUTION_GUIDE.md](medallion/E2E_EXECUTION_GUIDE.md) para mais detalhes.

---

**Última atualização**: Sprint 2, Maio 2026
**Autor**: RentMaster Team
**Status**: ✅ Local + Cloud Setup Completo, 🔄 Silver/Gold Em Desenvolvimento
