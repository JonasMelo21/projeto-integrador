# RentMaster - Arquitetura e Panorama Geral 🏗️

> **Documentação da arquitetura técnica, módulos do projeto e ferramentas usadas**.

## 📊 Estrutura do Projeto

RentMaster segue a **arquitetura Medalhão (Bronze → Silver → Gold)** no Azure:

```
┌─────────────────────────────────────────────────────────────┐
│                    RENTMASTER - PIPELINE                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1️⃣  INGESTÃO (Bronze)                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Web Scraper (DFimoveis) → Azure Container Registry   │   │
│  │ Disparado: Azure Data Factory (Pipeline)             │   │
│  │ Saída: JSON bruto em ADLS Gen2 (bronze/raw/)         │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                  │
│  2️⃣  PROCESSAMENTO (Silver)                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Databricks (PySpark)                                  │   │
│  │ - Limpeza e validação de dados                        │   │
│  │ - Deduplicação (ID SHA-256)                           │   │
│  │ - Transformação em formatos otimizados (Parquet)      │   │
│  │ - Saída: silver/cleaned/ (ADLS Gen2)                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                  │
│  3️⃣  CURAÇÃO (Gold)  &  CONSUMO                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ PostgreSQL + FastAPI                                 │   │
│  │ - Dados prontos para BI, ML e Analytics              │   │
│  │ - Saída: gold/ (DW - Data Warehouse)                 │   │
│  │ - API REST para frontend/chatbot                      │   │
│  │ - ML Model (XGBoost) integrado                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                     ↙     ↓      ↘                            │
│              React     Chatbot  BI/Power BI                   │
│            Dashboard    (Text-to-SQL)  Dashboard             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Módulos e Ferramentas

| Módulo | Responsabilidade | Ferramentas | Status |
|--------|------------------|-----------|--------|
| **Scraper** | Extração de dados em tempo real | Python, BeautifulSoup, Playwright, Docker | ✅ Sprint 2 |
| **Ingestão (ADF)** | Orquestração e agendamento | Azure Data Factory, ACR | ✅ Sprint 2 |
| **ADLS Gen2** | Armazenamento de dados brutos | Azure Data Lake Storage | ✅ Sprint 2 |
| **Databricks** | Transformação e limpeza | PySpark, SQL, Notebooks | 🔄 Sprint 3+ |
| **Backend API** | Servir dados e ML | FastAPI, Python | 🔄 Sprint 3 |
| **Banco de Dados** | DB transacional | PostgreSQL, SQL | 🔄 Sprint 3 |
| **Machine Learning** | Previsão de preços | XGBoost, Scikit-Learn, MLflow | 🔄 Sprint 3 |
| **Chatbot** | Interface de consultas NLP | Vanna.ai, LangChain, FastAPI | 🔄 Sprint 3+ |
| **Frontend** | Dashboard interativo | React, Tailwind CSS, JavaScript | ⏳ Sprint 4+ |
| **DevOps** | CI/CD e versionamento | Azure Repos, Azure Pipelines, Git | ✅ Contínuo |

---

## 📁 Estrutura de Pastas

```
Projeto Integrador III 2.0/
│
├── README.md                           # Visão geral rápida do projeto
├── CONTEXT.md                          # Regras de codificação + padrões (para Agentes IA)
│
├── docs/
│   ├── OVERVIEW.md                     # Este arquivo (arquitetura + módulos)
│   ├── ceub/                           # Documentação do cliente CEUB
│   │   ├── backlog_sprint.csv          # Backlog das sprints
│   │   └── er_diagram.mmd              # Diagrama ER (Mermaid)
│   │
│   ├── guides/                         # Guias por módulo
│   │   ├── SCRAPER.md                  # Como usar e estender o scraper
│   │   ├── API.md                      # API REST (FastAPI)
│   │   ├── DATABASE.md                 # Modelagem PostgreSQL
│   │   └── ML.md                       # ML Model + MLflow
│   │
│   └── testing/
│       └── CLOUD_TESTING.md            # Teste E2E com comandos `az`
│
├── scrapper/                           # Módulo Scraper
│   ├── scrapper.py                     # Script principal
│   ├── debug_scraper.py                # Versão com debug
│   ├── Dockerfile                      # Imagem Docker
│   └── debug_output/                   # Logs e outputs de debug
│
├── notebooks/                          # Jupyter Notebooks para análise
│   └── eda.ipynb                       # EDA (Exploratory Data Analysis)
│
├── examples.py                         # Exemplos de uso
├── main.py                             # Entry point (se houver)
├── pyproject.toml                      # Configuração de dependências (uv)
└── .env.example                        # Template de variáveis de ambiente
```

---

## 🔄 Fluxo de Dados - Sprint 2 (Atual)

### Etapas do Pipeline `RunScraperContainer`

```
1. Agendamento (ADF)
   └→ Dispara container no ACR em horário definido

2. Execução do Scraper
   └→ Container puxa imagens do DFimoveis
   └→ Extrai: titulo, preco, bairro, quartos, suites, vagas, etc.
   └→ Gera ID único (SHA-256, 12 chars)

3. Escrita em Bronze (Raw)
   └→ Cria arquivo JSON:
      {
        "data_extracao": "2026-04-15T10:30:00",
        "imoveis": [
          {
            "id_hex": "7c2bf7dac4f5",
            "titulo": "...",
            "preco": "R$ 26.900",
            ...
          }
        ]
      }
   └→ Salva em: ADLS Gen2 → bronze/raw/imoveis_YYYYMMDD_HHMMSS.json

4. Validação
   └→ Arquivo criado? ✅
   └→ Tamanho > 0? ✅
   └→ JSON válido? ✅
```

### Teste E2E da Sprint 2

Para validar o scraper de ponta a ponta:

```bash
# 1. Disparar pipeline
az datafactory pipeline create-run \
  --resource-group rg_rent_master_dev \
  --factory-name rentmaster-dataFactory \
  --name RunScraperContainer

# 2. Monitorar status
# (veja docs/testing/CLOUD_TESTING.md)

# 3. Validar dados em bronze/raw/
az storage fs file list \
  --account-name rentmasterstorageaccount \
  --file-system bronze \
  --path raw
```

---

## 🎯 Próximos Passos - Sprint 3+

### Silver (Databricks)
- [ ] Criar notebooks PySpark para limpeza
- [ ] Deduplicação eficiente usando ID único
- [ ] Validação de dados (schema, tipos)
- [ ] Detecção de anomalias

### Gold (Data Warehouse)
- [ ] Modelagem dimensional (Star Schema)
- [ ] Denormalização para queries rápidas
- [ ] Agregações pré-calculadas

### API (FastAPI)
- [ ] Rotas para consultar imóveis
- [ ] Autenticação (JWT)
- [ ] Rate limiting
- [ ] Integração com PostgreSQL

### Machine Learning
- [ ] Treinar modelo de classificação (Caro/Justo/Barato)
- [ ] Rastreamento de experimentos (MLflow)
- [ ] Deploy em Azure ML Endpoints

### Chatbot
- [ ] Conectar LLM com PostgreSQL
- [ ] Gerar SQL from natural language (Vanna.ai)
- [ ] Cache de queries comuns

### Frontend (React)
- [ ] Dashboard com filtros
- [ ] Maps (Leaflet/MapBox)
- [ ] Charts (Recharts/Chart.js)
- [ ] Integração com API

---

## 📚 Leitura Recomendada

1. **[CONTEXT.md](../CONTEXT.md)** - Regras de codificação e padrões obrigatórios
2. **[docs/testing/CLOUD_TESTING.md](testing/CLOUD_TESTING.md)** - Como testar pipeline na nuvem
3. **[docs/guides/SCRAPER.md](guides/SCRAPER.md)** - Guia detalhado do scraper
4. **[README.md](../README.md)** - Quick start e resumo

---

## 🔐 Recursos Azure Produção

| Recurso | Tipo | RG | Status |
|---------|------|----|---------
| rentmaster-dataFactory | Data Factory | rg_rent_master_dev | ✅ |
| rentmasteracr | Container Registry | rg_rent_master_dev | ✅ |
| rentmasterstorageaccount | Storage Account Gen2 | rg_rent_master_dev | ✅ |
| (em breve) | Databricks | rg_rent_master_dev | 🔄 |
| (em breve) | PostgreSQL | rg_rent_master_dev | ⏳ |
| (em breve) | App Service | rg_rent_master_dev | ⏳ |

---

## 🚀 Como Começar neste Projeto

1. **Leia** [CONTEXT.md](../CONTEXT.md) para entender as regras
2. **Veja** [README.md](../README.md) para setup local
3. **Teste** a Scraper localmente: `uv run scrapper/scrapper.py`
4. **Teste** em cloud: siga [docs/testing/CLOUD_TESTING.md](testing/CLOUD_TESTING.md)
5. **Implemente** features seguindo os padrões descritos em cada módulo

