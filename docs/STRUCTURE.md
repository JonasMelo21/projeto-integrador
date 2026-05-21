# RentMaster - Guia de Estrutura e Arquitetura para Desenvolvedores 🏗️

> **Este documento ajuda novos desenvolvedores a entender a estrutura do projeto, componentes e como começar a codar**.

---

## 🎯 Visão Geral da Arquitetura

RentMaster segue o **padrão Medalhão (Bronze → Silver → Gold)** na Azure para processamento de dados em camadas:

```
┌─────────────────────────────────────────────────────────────────┐
│                   RENTMASTER - DATA PIPELINE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📥 BRONZE (Ingestão - JSON Bruto)                              │
│  └─ Azure Container Apps Job + Scraper                          │
│     └─ Roda cron: 3h da madrugada todos os dias                 │
│     └─ Gera: JSON array com imóveis brutos                      │
│     └─ Salva em: ADLS Gen2 → bronze/raw/imoveis_*.json          │
│                                                                   │
│                            ↓                                      │
│                                                                   │
│  🔄 SILVER (Transformação - Parquet Normalizado) [SPRINT 3]     │
│  └─ Azure Function + Event Grid                                 │
│     └─ Trigger: Blob criado em bronze/raw/                      │
│     └─ Processamento:                                           │
│        • Lê JSON de bronze/raw/                                 │
│        • Normaliza campos (preco, area, quartos → tipos num)    │
│        • Calcula derived fields (preco_por_m2, img_count)       │
│        • Deduplicação por id_hex                                │
│     └─ Salva em: ADLS Gen2 → silver/date=YYYY-MM-DD/*.parquet  │
│                                                                   │
│                            ↓                                      │
│                                                                   │
│  🏆 GOLD (Curação - Delta/Parquet Modelado) [SPRINT 3+]         │
│  └─ Azure Functions + Feature Engineering                       │
│     └─ Lê: silver/*.parquet (dados limpos)                      │
│     └─ Enriquece: features para ML, star-schema                 │
│     └─ Salva em: ADLS Gen2 → gold/date=YYYY-MM-DD/*.parquet    │
│     └─ Upsert: Azure SQL Serverless (fact_imoveis, dim_*)       │
│                                                                   │
│                            ↓                                      │
│                                                                   │
│  🎨 CONSUMO (API + Frontend + ML)                                │
│  ├─ FastAPI Backend: consulta Azure SQL + expõe REST API        │
│  ├─ Frontend React: dashboard interativo                        │
│  └─ ML Models: previsão de preços (XGBoost via MLflow)          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Componentes do Sistema

### ✅ IMPLEMENTADO (Sprint 2)

| Componente | Localização | Tecnologia | Descrição |
|-----------|-----------|-----------|----------|
| **Scraper** | `scrapper/scrapper.py` | Python, BeautifulSoup, Playwright | Extrai dados de DFimoveis.com.br via web scraping |
| **Containerização Scraper** | `scrapper/Dockerfile` + ACR | Docker, Azure Container Registry | Imagem em `rentmasteracr.azurecr.io/scraper:latest` |
| **Container Apps Job** | Azure Cloud | Azure Container Apps | Job que executa scraper em cron (3h madrugada) |
| **ADLS Gen2** | Azure Cloud | Azure Data Lake Storage | Armazenamento: containers `bronze/`, `silver/`, `gold/` |
| **Backend API** | `backend/main.py` | FastAPI, SQLAlchemy, Uvicorn | API REST para consultar imóveis |
| **Database Local** | `backend/` | SQLite | BD de dev/teste (production usa Azure SQL) |
| **Frontend** | `frontend/` | HTML5, CSS, JavaScript | Interface de busca e listagem de imóveis |
| **Docker Compose** | `docker-compose.yml` | Docker | Orquestração local de backend + frontend |

### 🔄 EM DESENVOLVIMENTO (Sprint 3)

| Componente | Localização | Status | O que Falta |
|-----------|-----------|--------|----------|
| **Azure Function (Bronze→Silver)** | `function_app/` (NOT CREATED YET) | ❌ Falta criar | Python function para ETL, Event Grid subscription |
| **Silver Layer (Parquet)** | ADLS `silver/` | ⚠️ Container existe, schema não | Schema normalizado, particionamento, transformações |
| **Gold Layer (Curação)** | ADLS `gold/` | ⚠️ Container existe, pipeline não | Features para ML, star-schema modeling, upsert SQL |

### ⏳ FUTURO (Sprint 4+)

| Componente | Tecnologia | Descrição |
|-----------|-----------|----------|
| **Machine Learning** | XGBoost, Scikit-Learn, MLflow | Modelo de classificação (Caro/Justo/Barato) |
| **Chatbot** | LangChain, Vanna.ai | Interface Text-to-SQL |
| **Dashboard BI** | Power BI ou Metabase | Análises gerenciais |

---

## 📁 Estrutura de Pastas Detalhada

```
Projeto Integrador III 2.0/
│
├── 📄 README.md                        # Visão geral rápida do projeto
├── 📄 CONTEXT.md                       # ⭐ Regras OBRIGATÓRIAS de codificação (LEIA PRIMEIRO)
├── 📄 pyproject.toml                   # Dependências Python (gerenciadas com `uv`)
├── 📄 docker-compose.yml               # Orquestração local (backend + frontend)
│
├── 📁 docs/                            # 📚 DOCUMENTAÇÃO
│   ├── 📄 STRUCTURE.md                 # Este arquivo (estrutura + arquitetura)
│   ├── 📄 SETUP.md                     # Como testar (local + cloud Azure)
│   ├── 📁 guides/                      # Guias por módulo
│   │   ├── 📄 SCRAPER.md               # Como estender o scraper
│   │   ├── 📄 BACKEND.md               # FastAPI + rotas
│   │   └── 📄 DATABASE.md              # SQLAlchemy models
│   │
│   ├── 📁 medallion/                   # Arquitetura Medallion
│   │   └── 📄 E2E_EXECUTION_GUIDE.md   # Fluxo de dados ponta a ponta
│   │
│   ├── 📁 testing/                     # Testes
│   │   └── 📄 CLOUD_TESTING.md         # Testes E2E com Azure CLI
│   │
│   └── 📁 ceub/                        # Cliente CEUB
│       ├── 📄 backlog_sprint.csv       # Backlog das sprints
│       └── 📄 er_diagram.mmd           # Diagrama ER (Mermaid)
│
├── 📁 scrapper/                        # 🕷️ MÓDULO SCRAPER
│   ├── 📄 scrapper.py                  # ⭐ Script principal (extrai dados)
│   ├── 📄 debug_scraper.py             # Versão com debug detalhado
│   ├── 📄 Dockerfile                   # Container para ACR
│   └── 📁 debug_output/                # Logs de debug (git-ignored)
│
├── 📁 backend/                         # 🔧 API FASTAPI + DATABASE
│   ├── 📄 main.py                      # ⭐ Aplicação FastAPI (entry point)
│   ├── 📄 database.py                  # Setup ORM + conexões
│   ├── 📄 models.py                    # SQLAlchemy models (fact_imoveis, dim_*)
│   ├── 📄 schemas.py                   # Pydantic schemas (validação)
│   ├── 📄 requirements.txt              # Dependências Python
│   ├── 📄 Dockerfile                   # Container FastAPI
│   ├── 📁 routes/                      # Rotas da API
│   │   ├── 📄 imoveis.py               # GET /api/imoveis
│   │   └── 📄 dimensoes.py             # GET /api/dimensoes
│   │
│   ├── 📁 scripts/                     # Scripts de configuração
│   │   ├── 📄 load_from_adls.py        # Carrega JSON de ADLS para BD
│   │   └── 📄 .env.adls                # ⚠️ Credenciais Azure (git-ignored)
│   │
│   └── 📁 data/                        # Dados locais (desenvolvimento)
│
├── 📁 frontend/                        # 🎨 INTERFACE WEB
│   ├── 📄 index.html                   # ⭐ Interface principal
│   ├── 📄 script.js                    # Lógica JavaScript
│   ├── 📄 style.css                    # Estilos CSS
│   ├── 📄 nginx.conf                   # Config Nginx (em container)
│   ├── 📄 Dockerfile                   # Container Nginx
│   └── 📁 codigo_figma/                # Código Figma (design)
│
├── 📁 infrastructure/                  # ☁️ AZURE INFRASTRUCTURE AS CODE
│   └── 📁 bicep/                       # Bicep templates
│       └── 📄 main.bicep               # ⭐ Define recursos Azure (job, function, sql, etc)
│
├── 📁 notebooks/                       # 📊 ANÁLISE E TESTES
│   └── 📄 eda.ipynb                    # Exploratory Data Analysis
│
├── 📁 tests/                           # 🧪 TESTES
│   └── 📁 e2e/                         # Testes end-to-end
│       └── 📄 test_medallion_pipeline.py
│
└── 📁 scripts/                         # 🔨 SCRIPTS DE EXECUÇÃO
    ├── 📄 run_e2e_pipeline.sh          # Roda pipeline completo
    └── 📄 setup_medallion.py           # Setup inicial medallion
```

### 🔑 Arquivos Críticos para Novo Desenvolvedor

| Arquivo | Ler Primeiro | Motivo |
|---------|-------------|--------|
| **CONTEXT.md** | ✅ SIM (5 min) | Define regras de código obrigatórias (inglês/português, type hints, commits) |
| **docs/STRUCTURE.md** | ✅ SIM (15 min) | Entender arquitetura e componentes |
| **docs/SETUP.md** | ✅ SIM (10 min) | Como rodar local + testar cloud |
| **backend/models.py** | ✅ SIM (5 min) | Schema SQL (dim_imoveis, fact_imoveis) |
| **scrapper/scrapper.py** | ✅ SIM (10 min) | Entender fluxo de extração |
| **docker-compose.yml** | ✅ SIM (3 min) | Como rodar tudo local |
| **infrastructure/bicep/main.bicep** | ⚠️ DEPOIS (30 min) | Azure resource definitions |
| **backend/main.py** | ⚠️ DEPOIS (20 min) | Implementação FastAPI |
| **frontend/index.html** | ⚠️ DEPOIS (15 min) | Interface (comece pelo backend) |

---

## 💡 Como Começar a Codar Neste Projeto

### 🚀 Passo 1: Entender a Base (30 min)

1. **Leia `CONTEXT.md`** (5 min)
   - Entenda as regras: inglês/português, type hints, commits semânticos
   
2. **Leia este arquivo** (15 min)
   - Entenda a arquitetura: Bronze → Silver → Gold
   
3. **Explore a estrutura** (10 min)
   ```bash
   tree -L 2 -I '__pycache__|*.pyc|.git|node_modules'
   ```

### 💻 Passo 2: Explore o Backend (20 min)

```bash
# 1. Navegue até backend
cd backend

# 2. Veja os models (schema do banco)
cat models.py
# Você vai ver:
#  - class DimImobiliaria (empresa, nome)
#  - class DimLocal (bairro, cidade, UF)
#  - class FactImovel (imóvel, preço, área, quartos)

# 3. Veja as rotas (API endpoints)
cat routes/imoveis.py
cat routes/dimensoes.py
# Você vai ver: GET /api/imoveis, GET /api/dimensoes, etc

# 4. Entenda o main.py
cat main.py
# Você vai ver: FastAPI app initialization + startup
```

### 🕷️ Passo 3: Explore o Scraper (15 min)

```bash
# 1. Navegue até scraper
cd scrapper

# 2. Leia o código
cat scrapper.py
# Você vai ver:
#  - generate_property_id() → gera id_hex (SHA-256)
#  - extract_property_data() → parseia HTML
#  - upload_to_adls() → salva JSON em ADLS

# 3. Leia o guia
cat ../docs/guides/SCRAPER.md
```

### 🔧 Passo 4: Rode Localmente (30 min)

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 2. Frontend (outro terminal)
cd frontend
python -m http.server 5173

# 3. Acesse http://localhost:5173
```

### ☁️ Passo 5: Teste na Cloud (20 min)

```bash
# 1. Leia o guia
cat docs/SETUP.md   # Seção "Cloud Testing"

# 2. Verifique recursos Azure
az resource list -g rg_rent_master_dev

# 3. Execute o scraper no ACA
az containerapp job start -g rg_rent_master_dev -n rentmaster-dev-scraper-job

# 4. Verifique dados em bronze/raw
az storage blob list --account-name rentmasterstorageaccount --container-name bronze --prefix raw/
```

---

## 🎯 Stack Tecnológico por Camada

### Bronze (Ingestão)
- **Linguagem**: Python 3.11+
- **Scraping**: BeautifulSoup, Playwright
- **Containerização**: Docker, Azure Container Apps
- **Armazenamento**: ADLS Gen2 (blob storage)
- **Orquestração**: Azure Container Apps Job (cron)

### Silver (Transformação) [EM DESENVOLVIMENTO]
- **Linguagem**: Python 3.11+
- **Bibliotecas**: pandas, pyarrow (Parquet), azure-functions, azure-storage-blob
- **Trigger**: Azure Event Grid (BlobCreated)
- **Runtime**: Azure Functions Python 3.11
- **Saída**: Parquet particionado por data

### Gold (Curação) [PRÓXIMO]
- **Linguagem**: Python, SQL
- **DB**: Azure SQL Serverless
- **Saída**: Delta Lake ou Parquet
- **Features**: Modelagem star-schema

### Consumo
- **API**: FastAPI, Python
- **Frontend**: HTML5, CSS, JavaScript (sem framework build)
- **DB Local**: SQLite (dev), PostgreSQL (prod)
- **Container**: Docker (local), Azure App Service (prod)

---

## 📊 Responsabilidades por Arquivo

### Ao adicionar um novo endpoint de API
1. Crie função em `backend/routes/novo_modulo.py`
2. Adicione schema em `backend/schemas.py`
3. Importe em `backend/main.py`
4. Teste localmente: `curl http://localhost:8000/api/novo`
5. Commit semântico: `feat: novo endpoint /api/novo`

### Ao estender o scraper
1. Modifique `scrapper/scrapper.py`
2. Teste localmente: `python scrapper/debug_scraper.py`
3. Build da imagem: `docker build -t rentmasteracr.azurecr.io/scraper:latest .`
4. Push ao ACR: `az acr build -r rentmasteracr -t scraper:latest .`
5. Commit: `feat: adicionar extração de campo X`

### Ao criar Azure Function (Bronze→Silver)
1. Crie pasta `function_app/`
2. Crie `function_app/function_app.py` (entry point)
3. Crie `function_app/requirements.txt`
4. Teste localmente com Azure Functions Core Tools
5. Deploy via Bicep ou Azure CLI

---

## ⚠️ Regras Importantes

1. **SEMPRE ler `CONTEXT.md` antes de codar**
   - Type hints obrigatórios
   - Docstrings em português (Google Style)
   - Commits semânticos (`feat:`, `fix:`, `docs:`, `refactor:`)

2. **Variáveis de ambiente em `.env.adls` (git-ignored)**
   - NUNCA commitar credenciais
   - Use Key Vault em produção

3. **Testes obrigatórios**
   - Mínimo 80% de cobertura
   - Rode `pytest` antes de push

4. **Separação inglês/português**
   - Código: inglês
   - Docs: português
   - Comentários: português

5. **Versionamento Git**
   - Branch: `feature/nome`, `fix/nome`, `chore/nome`
   - Commit: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`

---

## 📚 Documentação Relacionada

- **[CONTEXT.md](../CONTEXT.md)** - Regras de codificação (OBRIGATÓRIO)
- **[docs/SETUP.md](SETUP.md)** - Setup local + testes cloud
- **[docs/guides/SCRAPER.md](guides/SCRAPER.md)** - Guia do scraper
- **[docs/medallion/E2E_EXECUTION_GUIDE.md](medallion/E2E_EXECUTION_GUIDE.md)** - Fluxo completo
