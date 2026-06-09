# RentMaster - Moneyball de Aluguel 🏠📊

Plataforma inteligente que extrai imóveis para aluguel em tempo real, analisa preços com ML e fornece assistente virtual.

**240 imóveis** | **21 imobiliárias** | **39 localidades** | **Azure Medallion Architecture**

---

## 📚 Documentação Principal

**Comece aqui** (leia nesta ordem):

1. **[docs/STRUCTURE.md](docs/STRUCTURE.md)** ⭐ - Entender arquitetura e estrutura
2. **[docs/SETUP.md](docs/SETUP.md)** ⭐ - Como rodar (local + cloud)
3. **[CONTEXT.md](CONTEXT.md)** - Regras de código obrigatórias

**Guias Específicos** (quando trabalhar com esses módulos):

- **[docs/guides/BACKEND.md](docs/guides/BACKEND.md)** - FastAPI, endpoints, rotas
- **[docs/guides/DATABASE.md](docs/guides/DATABASE.md)** - Schema, queries, SQL
- **[docs/guides/SCRAPER.md](docs/guides/SCRAPER.md)** - Web scraper, deduplicação
- **[docs/OVERVIEW.md](docs/OVERVIEW.md)** - Panorama geral da arquitetura

---

## 🎯 O Projeto

Arquitetura **Medalhão (Bronze → Silver → Gold)** em Azure:

```
📥 BRONZE (Scraper)        →  🔄 SILVER (Transform) [Sprint 3]  →  🏆 GOLD (Curate) [Sprint 3+]  →  🎨 API/Frontend
   JSON bruto                   Parquet normalizado              Star schema + SQL              FastAPI + React
```

| Componente | Status | Descrição |
|-----------|--------|-----------|
| Web Scraper | ✅ Sprint 2 | Extrai imóveis de DFimoveis |
| Bronze/Raw | ✅ Sprint 2 | JSON em ADLS Gen2 |
| FastAPI Backend | ✅ Sprint 2 | 240 imóveis em SQLite |
| Frontend HTML | ✅ Sprint 2 | Busca, filtros, detalhes |
| Silver/Transform | 🔄 Sprint 3 | Azure Function + Event Grid |
| Gold/Analytics | 🔄 Sprint 3+ | Feature engineering + SQL |

---

## 🚀 Quick Start

### Local (sem Docker)
```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (outro terminal)
cd frontend && python -m http.server 5173
```

**Acesse**: http://localhost:5173

### Com Docker
```bash
docker compose up --build
```

**Acesse**: http://localhost:5173

Leia: **[docs/SETUP.md](docs/SETUP.md)** para detalhes completos.

---

## 📊 API Endpoints

```bash
# Listar imóveis
curl "http://localhost:8000/api/imoveis?limit=10"

# Detalhes de um imóvel
curl http://localhost:8000/api/imoveis/1

# Estatísticas
curl http://localhost:8000/api/imoveis/stats

# Imobiliárias
curl http://localhost:8000/api/dimensoes/imobiliarias

# Localidades
curl http://localhost:8000/api/dimensoes/locais
```

**Documentação interativa**: http://localhost:8000/docs

---

## 🏗️ Tech Stack

| Camada | Tecnologia |
|--------|-----------|
| **Ingestão** | Python 3.13, BeautifulSoup, Playwright, Docker |
| **Cloud** | Azure Container Apps, Container Registry, ADLS Gen2, SQL Serverless |
| **Backend** | FastAPI, Uvicorn, SQLAlchemy, SQLite/Azure SQL |
| **Frontend** | HTML5, CSS3, JavaScript (sem build tools) |
| **Container** | Docker, Docker Compose |
| **Databricks** | PySpark (futuro: Silver layer) |

---

## 📁 Estrutura de Pastas

```
Projeto Integrador III 2.0/
├── README.md                    # Este arquivo
├── CONTEXT.md                   # Regras de código ⭐ LEIA PRIMEIRO
├── docker-compose.yml           # Local development
│
├── docs/
│   ├── STRUCTURE.md             # ⭐ Arquitetura e estrutura
│   ├── SETUP.md                 # ⭐ Setup e testes
│   ├── OVERVIEW.md              # Panorama geral
│   ├── guides/
│   │   ├── BACKEND.md           # FastAPI + endpoints
│   │   ├── DATABASE.md          # Schema + queries SQL
│   │   └── SCRAPER.md           # Web scraper
│   ├── medallion/               # Medalhão architecture docs
│   └── testing/                 # Cloud testing guides
│
├── backend/                     # FastAPI + SQLite
│   ├── main.py                  # Entry point
│   ├── models.py                # ORM models
│   ├── routes/                  # API endpoints
│   └── scripts/load_from_adls.py
│
├── frontend/                    # HTML5 puro
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── scrapper/                    # Web scraper
│   └── scrapper.py
│
├── infrastructure/              # Azure IaC
│   └── bicep/main.bicep
│
├── data/                        # Sample data
│   └── dados_imoveis.json
│
└── scripts/                     # Utilities
    └── run_e2e_pipeline.sh
```

---

## 🔧 Azure Resources

Todos em `rg_rent_master_dev`, `brazilsouth`:

```
✅ Container Apps Job (scraper)      - rentmaster-dev-scraper-job
✅ Container Registry                - rentmasteracr
✅ ADLS Gen2                         - rentmasterstorageaccount
✅ Azure SQL Serverless             - rentmastersqlserver
✅ Key Vault                        - rentmaster-kv-dev
✅ Application Insights             - rentmaster-dev-insights
🔄 Azure Function (future)          - rentmaster-dev-etl-func
```

Ver status: **[docs/SETUP.md](docs/SETUP.md#-testes-na-cloud-azure)**

---

## 🎓 Aprendizado

**Novo no projeto?**

1. Leia [CONTEXT.md](CONTEXT.md) (5 min) - Regras
2. Leia [docs/STRUCTURE.md](docs/STRUCTURE.md) (15 min) - Arquitetura
3. Leia [docs/SETUP.md](docs/SETUP.md) (10 min) - Como rodar
4. Escolha seu caminho:
   - Backend? → [docs/guides/BACKEND.md](docs/guides/BACKEND.md)
   - Database? → [docs/guides/DATABASE.md](docs/guides/DATABASE.md)
   - Scraper? → [docs/guides/SCRAPER.md](docs/guides/SCRAPER.md)
   - DevOps? → [docs/OVERVIEW.md](docs/OVERVIEW.md)

---

## 📝 Comandos Rápidos

```bash
# Setup
cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Rodar local
uvicorn main:app --reload  # Backend
python -m http.server 5173  # Frontend

# Docker
docker compose up --build

# Testar API
curl http://localhost:8000/api/imoveis?limit=5
curl http://localhost:8000/api/imoveis/stats
curl http://localhost:8000/docs

# Cloud: executar scraper
az containerapp job start -g rg_rent_master_dev -n rentmaster-dev-scraper-job

# Cloud: verificar dados
az storage blob list --account-name rentmasterstorageaccount --container-name bronze --prefix raw/
```

---

## 🤝 Contribuindo

1. Crie branch: `git checkout -b feature/sua-feature`
2. Siga [CONTEXT.md](CONTEXT.md) (type hints, docstrings, português em docs)
3. Faça commit: `git commit -m "Adiciona feature X"`
4. Push: `git push origin feature/sua-feature`
5. Abra PR

---

## 📞 Próximas Etapas

**Sprint 3 Tasks**:
- [ ] Azure Function (Bronze → Silver ETL)
- [ ] Event Grid trigger
- [ ] Parquet schema normalizado
- [ ] SQL upsert pipeline

Veja: **[docs/SETUP.md](docs/SETUP.md#-próximos-passos-sprint-3)**

---

## 📄 Licença

CC0 1.0 Universal (Domínio Público)

---

**📚 Leia primeiro**: [docs/STRUCTURE.md](docs/STRUCTURE.md)  
**🚀 Depois execute**: [docs/SETUP.md](docs/SETUP.md)  
**🤖 Regras de código**: [CONTEXT.md](CONTEXT.md)
```

---

## 🔧 Variáveis de Ambiente

### backend/scripts/.env.adls
```
AZURE_STORAGE_ACCOUNT=rentmasterstorageaccount
AZURE_STORAGE_KEY=<sua_chave>
ADLS_CONTAINER=bronze
ADLS_PATH=raw/
```

---

## 📁 Estrutura

```
backend/           → FastAPI app
frontend/          → Interface HTML
scrapper/          → Web scraper
docs/              → Documentação
docker-compose.yml → Orquestração
```

---

## 🚀 Próximos Passos

1. **Leia**: [docs/SETUP.md](docs/SETUP.md) para começar
2. **Code**: Veja [CONTEXT.md](CONTEXT.md) para regras
3. **Test**: Use os comandos em [docs/SETUP.md](docs/SETUP.md)

---

**Desenvolvido por**: Projeto Integrador III - CEUB
