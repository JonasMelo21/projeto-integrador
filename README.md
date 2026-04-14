# RentMaster - Moneyball de Aluguel 🏠📊

Uma plataforma inteligente e orientada a dados que extrai imóveis para aluguel em tempo real, aplica Machine Learning para avaliar preços (Caro/Justo/Barato), e fornece um assistente virtual para análises com linguagem natural.

**Status:** 

- Sprint 1 - Concluído ✅
- Sprint 2 - Scraper Funcional + Docker + ADLS Gen2 (✅ Feature 2.1 Validada)
- Sprint 3+ - Pendente ⏳

---

## 📚 Documentação Principal

Este projeto segue **regras rigorosas de codificação e arquitetura**. Antes de codificar ou fazer alterações, SEMPRE consulte:

### 1. **[CONTEXT.md](CONTEXT.md)** - LEITURA OBRIGATÓRIA PARA AGENTES IA
   - 📋 **Regras de Codificação:** Idioma, Clean Code, SOLID, Type Hints
   - 🛠️ **Stack Tecnológico:** Azure, FastAPI, Databricks, PostgreSQL, React
   - 🚀 **Status do Projeto:** O que foi feito (Sprint 1), o que vem (Sprint 2 e 3)
   - 🔄 **Fluxo de Dados:** Arquitetura end-to-end
   - 📦 **Gerenciamento com `uv`:** Grupos de dependências

### 2. **[docs/SCRAPER_GUIDE.md](SCRAPER_GUIDE.md)** - INSTRUÇÕES DO MÓDULO DE SCRAPING
   - 🔷 Como usar o scraper (CLI, opções, exemplos)
   - 📊 Estrutura dos dados coletados
   - 💡 Exemplos práticos de uso
   - 🔧 Troubleshooting

### 3. **Este README.md** - Visão Geral Rápida
   - Resumo do projeto
   - Como começar
   - Estrutura de pastas
   - Próximos passos

---

## 🎯 O Que é RentMaster?

RentMaster (Moneyball de Aluguel) é uma **plataforma inteligente** que:

1. **Extrai Dados em Tempo Real** (Sprint 2)
   - Web scraping de portais de imóveis (DFimoveis, etc.)
   - Identificação única de cada imóvel (ID SHA-256)
   - Suporte a paginação sem duplicatas

2. **Processa em Pipeline Medalhão** (Sprint 2)
   - 🥉 **Bronze:** Dados brutos no ADLS Gen2
   - 🥈 **Silver:** Dados limpos e validados (Databricks/PySpark)
   - 🥇 **Gold:** Dados curados para BI e consumo

3. **Prediz e Classifica Preços** (Sprint 3)
   - ML Model (XGBoost/Scikit-Learn) → "Caro", "Justo" ou "Barato"
   - Deployed em Azure Machine Learning
   - Real-time inference via FastAPI

4. **Fornece Assistente Virtual** (Sprint 3)
   - Chatbot Text-to-SQL (Vanna.ai/LangChain)
   - Consultas em linguagem natural
   - Integrado com PostgreSQL

5. **Dashboard Interativo** (Sprint 3)
   - Frontend React + Tailwind CSS
   - Hospedado no Azure Static Web Apps
   - Filtros, mapas, análises em tempo real

---

## 🚀 Como Começar

### Pré-requisitos
- Python 3.13+
- `uv` (gerenciador de pacotes) - [Instale aqui](https://astral.sh/uv/)
- Git

### Instalação Rápida

```bash
# Clone o repositório
git clone https://RentMaster@dev.azure.com/RentMaster/Projeto%20Integrador%20III%202.0/_git/Projeto%20Integrador%20III%202.0

cd "Projeto Integrador III 2.0"

# Sincronize dependências
uv sync

# (Opcional) Sincronize apenas grupos específicos
uv sync --group scraping        # Apenas web scraping
uv sync --group notebook        # Apenas Jupyter + análise
uv sync --group api             # Apenas FastAPI
```

### Executar o Scraper (Sprint 2 🔄)

> **Atenção:** Scraper está em desenvolvimento para Sprint 2. A seguir, exemplos de uso planejado:

```bash
# 1 página (padrão)
uv run scrapper/scrapper.py

# 3 páginas com apenas JSON
uv run scrapper/scrapper.py --num-pages 3 --format json

# Com timeout maior e URL customizada
uv run scrapper/scrapper.py "https://dfimoveis.com.br/aluguel/df/lago-sul/imoveis" --num-pages 2 --timeout-ms 60000
```

**Saída (esperada):** Dados em `data/imoveis.csv` e `data/imoveis.json`

→ Detalhes: [docs/SCRAPER_GUIDE.md](docs/SCRAPER_GUIDE.md)

### Explorar Dados com Jupyter (Sprint 2 🔄)

> **Atenção:** Jupyter com dados será disponível em Sprint 2 após implementação do scraper.

```bash
# Inicia servidor Jupyter
uv run jupyter notebook

# Abre notebooks/eda.ipynb
# Kernel: "Projeto Integrador III 2.0" (já registrado)
```

---

## 📁 Estrutura do Projeto

```
Projeto Integrador III 2.0/
│
├─ 📖 CONTEXT.md                      ← GUIA DE CODIFICAÇÃO (LEIA PRIMEIRO!)
├─ 📖 README.md                       ← Este arquivo
├─ 📦 pyproject.toml                  ← Config `uv` com grupos de deps
│
├─ � docs/  (Sprint 1 ✅)
│  ├─ CONTEXT.md                      │  Guia técnico e arquitetura
│  ├─ README.md                       │  Visão geral
│  ├─ SCRAPER_GUIDE.md               │  Manual do scraper
│  ├─ er_diagram.mmd                 │  Modelo de Dados
│  ├─ eap_diagram.mmd                │  Estrutura Analítica
│  ├─ backlog_sprint.csv
│  └─ [PDFs de requisitos, aulas]
│
├─ 🔷 scrapper/  (Sprint 2 🔄)
│  └─ scrapper.py                     │  Web scraper com paginação & dedup
│
├─ 📊 notebooks/  (Sprint 2 🔄)
│  └─ eda.ipynb                       │  Exploração de dados
│
├─ 🚀 backend/  (Sprint 2 🔄)
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ routers/
│  │  ├─ services/
│  │  ├─ models/
│  │  └─ schemas/
│  └─ tests/
│
├─ 🎨 frontend/  (Sprint 2 🔄)
│  ├─ src/
│  │  ├─ components/
│  │  ├─ pages/
│  │  └─ styles/
│  └─ package.json
│
└─ 🤖 ml/  (Sprint 3+ ⏳)
    ├─ models/
    ├─ preprocessing/
    └─ evaluation/
```

---

## 📊 Status do Projeto

### ✅ Sprint 1: Fundações e Concepção (CONCLUÍDO)

**Epic 1 - Concepção Visual e Técnica:**
- ✅ Modelo de Dados (ER Diagram)
- ✅ Estrutura Analítica (EAP)
- ✅ Protótipos em Figma (Listagem, Detalhe, Favoritos, Chat)
- ✅ Histórias de Usuário com Critérios de Aceitação
- ✅ Taskboard estruturado (Azure Boards)
- ✅ Documentação técnica (CONTEXT.md, README.md, SCRAPER_GUIDE.md)

### ✅ Sprint 2: Descoberta e Exploração de Imóveis (FEATURE 2.1 CONCLUÍDA)

**Epic 2.1 - Scraper + Docker + ADLS Gen2 Pipeline (CONCLUÍDO ✅)**

- ✅ **Scraper Funcional**
  - ✅ Extrai 30+ imóveis por página
  - ✅ Paginação com deduplicação automática
  - ✅ **Área correta**: procura por "m²" em múltiplos elementos
  - ✅ **Múltiplas imagens**: array de URLs (filtra base64)
  - ✅ ID hexadecimal único (SHA-256, 12 chars)
  - ✅ Exporta em CSV + JSON
  - ✅ Docker containerizado com SDKs Azure

- ✅ **Upload para ADLS Gen2**
  - ✅ Parâmetro `--upload-to-adls` funcional
  - ✅ Autenticação via `DefaultAzureCredential()` com Managed Identity
  - ✅ JSON persistido em `bronze/raw/` com timestamp
  - ✅ Validação de blob após upload (sem arquivos vazios)

- ✅ **Pipeline End-to-End no Azure Data Factory**
  - ✅ Web Activity dispara container ACI via REST API
  - ✅ Container executa com exitCode 0
  - ✅ Arquivo novo em `bronze/raw/` a cada execução
  - ✅ Pipeline marca "Succeeded" automaticamente
  - ✅ **Validado em: 2026-04-14 22:38 UTC**

- ✅ **Dados Coletados**
  - 30+ imóveis únicos por execução
  - Estrutura JSON completa com 13 campos
  - Deduplicação funcional em múltiplas páginas

**Próximas Features (Sprint 2):**
- [ ] Jupyter Notebook + EDA
- [ ] FastAPI backend (rotas iniciais)
- [ ] Frontend React (cards e integração)
- [ ] Feature 2.2 - Busca e Filtros Dinâmicos

**Commit de Referência:** `2ad201e` (Merged PR 3 - Feature 2.1 Completa)

### 🎨 Sprint 3+: Inteligência e Jornada

**Epic 3 - Diagnóstico de Preço (O 'Moneyball'):**
- [ ] Feature 3.1 - Termômetro de Oportunidade
  - Dataset preparado e feature engineering
  - Modelo XGBoost (Caro/Justo/Barato)
  - Deploy em Azure Machine Learning
  - Tags visuais no frontend

**Epic 4 - Assistente Virtual Especialista (Chat):**
- [ ] Feature 4.1 - Motor de IA
  - Treinamento Vanna.ai (Text-to-SQL)
  - Rota `/api/chat` no backend
  - Chat UI (modal flutuante)

**Epic 5 - Jornada Personalizada e Confiabilidade:**
- [ ] Feature 5.1 - Gestão de Favoritos
  - Persistência de curtidas (BD)
  - Página "Meus Favoritos"
  
- [ ] Feature 5.2 - Disponibilidade Pública
  - Deploy em Azure (ADLS, PostgreSQL, App Service, Static Web Apps)
  - CI/CD com Azure Pipelines

---

## 🏗️ Arquitetura Visual

![Diagrama de Arquitetura RentMaster](docs/diagrama_arq_rent_master.png)

**Componentes principais:**
- 🔷 **Ingestão & Orquestração:** Azure Data Factory + Scraper Python
- 💾 **Data Lake:** ADLS Gen2 com padrão Medalhão (Bronze/Silver/Gold)
- 🔄 **Transformação:** Databricks Workspace com PySpark
- 🗄️ **Database:** Azure Database for PostgreSQL
- 🚀 **Backend:** Azure App Service (FastAPI)
- 🎨 **Frontend:** Azure Static Web Apps (React)
- 🤖 **IA:** Vanna.ai + LangChain para chatbot Text-to-SQL

---

## 🛠️ Stack Tecnológico (Azure-First)

| Camada | Tecnologias | Status |
|--------|-------------|--------|
| **Arquitetura & Design** | ER Diagram, EAP, Protótipos Figma, Histórias | ✅ Sprint 1 |
| **Scraping** | Python, Playwright, BeautifulSoup | 🔄 Sprint 2 |
| **Análise** | Jupyter, Pandas, Matplotlib, Seaborn | 🔄 Sprint 2 |
| **Backend** | FastAPI, Uvicorn, Pydantic | 🔄 Sprint 2 |
| **Frontend** | React, Tailwind CSS | 🔄 Sprint 2 |
| **Data Lake** | ADLS Gen2 (Bronze/Silver/Gold) | 🔄 Sprint 2 |
| **ETL** | Azure Databricks, PySpark | 🔄 Sprint 2 |
| **Database** | PostgreSQL (Azure Database) | 🔄 Sprint 2 |
| **ML** | Scikit-Learn, XGBoost, MLflow | ⏳ Sprint 3 |
| **IA** | Vanna.ai, LangChain | ⏳ Sprint 3 |
| **DevOps** | Azure Repos, Pipelines, ACR, Static Apps | ⏳ Sprint 3 |

---

## 📦 Gerenciamento de Dependências com uv

Os grupos estão organizados por funcionalidade:

```bash
# Instalar ALL
uv sync

# Instalar grupos específicos
uv sync --group scraping        # Playwright, BeautifulSoup
uv sync --group notebook        # Jupyter, Pandas, Matplotlib
uv sync --group api             # FastAPI, Uvicorn
uv sync --group data            # PySpark, Pandas
uv sync --group ml              # Scikit-Learn, XGBoost, MLflow
uv sync --group test            # Pytest
uv sync --group dev             # Ruff, Black, Mypy

# Rodar comandos com uv
uv run python script.py
uv run pytest
uv run jupyter notebook
```

Detalhes: Veja `pyproject.toml` ou [CONTEXT.md](CONTEXT.md#-gerenciamento-de-dependências-com-uv)

---

## ✍️ Padrões de Codificação

Este projeto segue regras rígidas. **NUNCA desvie delas:**

✅ **Sempre:**
- Código em **Inglês** (variáveis, funções, classes)
- Documentação em **Português** (docstrings, comments)
- Type hints em todas as funções
- Docstrings no formato Google
- Git commits semânticos (`feat:`, `fix:`, `docs:`)

❌ **Nunca:**
- Variáveis com nomes genéricos (`x`, `temp`, `data`)
- Funções maiores que 20 linhas
- Sem type hints
- Commits sem semântica ("WIP", "updated")

📖 **Leia:** [CONTEXT.md - Regras de Codificação](CONTEXT.md#-regras-de-codificação-crítico---sempre-seguir)

---

## 🤝 Como Contribuir

1. Crie uma branch: `git checkout -b feature/minha-feature`
2. Siga as regras em [CONTEXT.md](CONTEXT.md)
3. Commit semântico: `git commit -m "feat: adiciona nova funcionalidade"`
4. Push e crie Pull Request

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError: No module named 'playwright'` | Execute `uv sync --group scraping` |
| Scraper não encontra imóveis | Aumentar timeout: `--timeout-ms 90000` |
| Jupyter kernel não aparece | Reexecute: `uv run python -m ipykernel install --user --name "projeto-integrador"` |
| Dependências conflitando | Delete `.venv/` e execute `uv sync` novamente |

---

## 📞 Referências Rápidas

- **Regras & Arquitetura:** [CONTEXT.md](CONTEXT.md)
- **Como usar Scraper:** [docs/SCRAPER_GUIDE.md](docs/SCRAPER_GUIDE.md)
- **Dados coletados:** `data/imoveis.csv` ou `data/imoveis.json`
- **Análise exploratória:** `notebooks/eda.ipynb`

---

## 📄 Licença

Este projeto é fornecido para fins educacionais na disciplina "Projeto Integrador III" (2026/1).

---

**Última atualização:** 2026-04-07  
**Versão:** 1.1.0 (Sprint 1 ✅ + Sprint 2 🔄)

---

💡 **Dica para Agentes IA:** Se foi direcionado para este arquivo, leia primeiro [CONTEXT.md](CONTEXT.md)!