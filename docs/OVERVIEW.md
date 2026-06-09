# RentMaster - Panorama Geral do Projeto 🏗️

> **Visão geral da arquitetura, stack tecnológico e referências cruzadas de documentação**.

---

## 📚 LEIA PRIMEIRO

**Novo Desenvolvedor?** Siga este plano:

1. **CONTEXT.md** (5 min) — Regras de codificação obrigatórias
2. **docs/STRUCTURE.md** (15 min) — Entender a estrutura do projeto
3. **docs/SETUP.md** (10 min) — Como rodar e testar (local + cloud)

Depois escolha seu caminho:
- Backend? Leia `backend/models.py` + `docs/guides/BACKEND.md`
- Scraper? Leia `scrapper/scrapper.py` + `docs/guides/SCRAPER.md`
- Frontend? Leia `frontend/index.html` + `docs/guides/FRONTEND.md`
- Cloud/DevOps? Leia `infrastructure/bicep/main.bicep` + `docs/SETUP.md`

---

## 🏗️ Arquitetura Medallion (Bronze → Silver → Gold)

```
┌─────────────────────────────────────────────────────────────────┐
│                   RENTMASTER - DATA PIPELINE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📥 BRONZE (Ingestão)                                           │
│  └─ Scraper (DFimoveis) → Azure Container Apps Job             │
│     Saída: JSON bruto em ADLS bronze/raw/                       │
│                                                                   │
│                            ↓                                      │
│                                                                   │
│  🔄 SILVER (Transformação) [SPRINT 3]                          │
│  └─ Azure Function ETL + Event Grid                             │
│     Processa: normaliza, deduplica, calcula features            │
│     Saída: Parquet em ADLS silver/date=YYYY-MM-DD/              │
│                                                                   │
│                            ↓                                      │
│                                                                   │
│  🏆 GOLD (Curação) [SPRINT 3+]                                 │
│  └─ Feature Engineering + Star Schema                           │
│     Processa: modela, enriquece, upsert em Azure SQL            │
│     Saída: Parquet em ADLS gold/ + Azure SQL tabelas            │
│                                                                   │
│                            ↓                                      │
│                                                                   │
│  🎨 CONSUMO                                                      │
│  └─ FastAPI Backend + Frontend + ML Models                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Guia Rápido de Arquivos

| Arquivo | Propósito | Leia se... |
|---------|-----------|-----------|
| **CONTEXT.md** | Regras de código | Você vai programar |
| **docs/STRUCTURE.md** | Estrutura do projeto | Novo no projeto |
| **docs/SETUP.md** | Setup + testes | Quer rodar/testar |
| **backend/models.py** | Schema DB | Vai trabalhar com BD |
| **scrapper/scrapper.py** | Extração de dados | Vai estender scraper |
| **infrastructure/bicep/main.bicep** | Azure resources | Vai fazer deploy |
| **backend/main.py** | API FastAPI | Vai criar endpoints |
| **docs/guides/SCRAPER.md** | Guia scraper | Precisa entender scraper |

---

## ✅ Implementado (Sprint 2)

- ✅ Web Scraper (DFimoveis.com.br)
- ✅ Azure Container Apps Job (cron 3h)
- ✅ Azure Container Registry (ACR)
- ✅ ADLS Gen2 (bronze/, silver/, gold/ containers)
- ✅ FastAPI Backend + SQLite
- ✅ Frontend HTML5
- ✅ Docker Compose local

---

## 🔄 Em Desenvolvimento (Sprint 3)

- 🔄 Azure Function Bronze→Silver ETL
- 🔄 Event Grid (blob trigger)
- 🔄 Silver Parquet schema + partitioning
- 🔄 Gold star-schema + SQL upsert

**Veja detalhes em**: `docs/SETUP.md` seção "O Que Falta"

---

## ⏳ Futuro (Sprint 4+)

- ⏳ Machine Learning (XGBoost)
- ⏳ Chatbot (LangChain + Text-to-SQL)
- ⏳ Dashboard BI (Power BI)

---

## 📚 Documentação Disponível

```
docs/
├── STRUCTURE.md              ⭐ Como entender o projeto
├── SETUP.md                  ⭐ Como rodar + testar
├── guides/
│   ├── SCRAPER.md
│   ├── BACKEND.md
│   └── DATABASE.md
├── medallion/
│   └── E2E_EXECUTION_GUIDE.md
├── testing/
│   └── CLOUD_TESTING.md
└── ceub/
    ├── backlog_sprint.csv
    └── er_diagram.mmd
```

---

## 🔗 Links Rápidos

| Recurso | Link |
|---------|------|
| Código | GitHub (Azure Repos) |
| Backend | `http://localhost:8000` (local) |
| Frontend | `http://localhost:5173` (local) |
| Azure RG | `rg_rent_master_dev` |
| ADLS | `rentmasterstorageaccount` |
| SQL Server | `rentmastersqlserver` |

---

## 📞 Comandos Úteis Rápidos

```bash
# Backend local
cd backend && uvicorn main:app --reload

# Frontend local  
cd frontend && python -m http.server 5173

# Docker
docker compose up

# Cloud: executar scraper
az containerapp job start -g rg_rent_master_dev -n rentmaster-dev-scraper-job

# Cloud: listar blobs
az storage blob list --account-name rentmasterstorageaccount --container-name bronze --prefix raw/
```

---

**Próximas leituras**: [STRUCTURE.md](STRUCTURE.md) | [SETUP.md](SETUP.md) | [../CONTEXT.md](../CONTEXT.md)

