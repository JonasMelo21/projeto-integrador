# CONTEXT.md - Guia de Codificação: RentMaster

> **Este arquivo é um guia essencial para agentes de IA e desenvolvedores.** Define as regras de codificação, padrões, stack tecnológico e estado do projeto.

---

## 📌 Sobre o RentMaster

**RentMaster** (Moneyball de Aluguel) é uma plataforma inteligente que:
- Extrai dados reais de imóveis via web scraping (Sprint 2)
- Aplica ML para avaliar se o preço está "Caro, Justo ou Barato" (Sprint 3)
- Fornece um assistente virtual (Chatbot Text-to-SQL) para análises complexas (Sprint 3)

**Status:** Sprint 1 Concluído (Fundações) ✅ | Sprint 2 Iniciado (Scraper/Backend) 🔄

---

## 🛠️ Stack Tecnológico

### Coleta de Dados (Web Scraping)
- **Python:** BeautifulSoup, Playwright, Selenium
- **Containerização:** Docker (Azure Container Instances via Azure Data Factory)
- **Ferramentas:** `uv` para gerenciamento de dependências

### Armazenamento e Engenharia de Dados
- **Data Lake:** Azure Data Lake Storage Gen2 (ADLS Gen2)
- **Arquitetura:** Medalhão (Bronze → Silver → Gold)
- **Processing:** Azure Databricks (PySpark)

### Backend & API
- **Framework:** FastAPI (hospedado em Azure App Service)
- **Linguagem:** Python
- **Padrão:** Separação clara (routers, services, models, schemas)

### Banco de Dados
- **Principal:** Azure Database for PostgreSQL
- **Função:** Consumo transacional, API queries, Chatbot

### Machine Learning
- **Modelagem:** Scikit-Learn, XGBoost
- **Rastreamento:** MLflow
- **Deploy:** Azure Machine Learning (Managed Online Endpoints)

### IA & Chatbot
- **Framework:** Vanna.ai / LangChain
- **Padrão:** Text-to-SQL connected to PostgreSQL
- **Delivery:** FastAPI

### Frontend
- **Framework:** React + JavaScript
- **Styling:** Tailwind CSS
- **Hospedagem:** Azure Static Web Apps

### DevOps & CI/CD
- **Versionamento:** Azure Repos
- **Gestão Ágil:** Azure Boards
- **Imagens Docker:** Azure Container Registry (ACR)
- **Automação:** Azure Pipelines

---

## 📋 Regras de Codificação (CRÍTICO - SEMPRE SEGUIR)

### 1. Idioma
- **Código:** Inglês (variáveis, funções, classes, modules)
- **Documentação:** Português do Brasil (docstrings, comments, README, guides)

**Exemplos:**
```python
# ❌ ERRADO
def extrair_dados_imovel():
    """Extrai os dados"""
    dados_locais = []

# ✅ CORRETO
def extract_property_data(article_html: str) -> dict:
    """Extrai dados de um imóvel a partir do HTML da article."""
    properties = []
```

### 2. Clean Code & SOLID
- **S**ingle Responsibility: Uma função faz UMA coisa
- **O**pen/Closed: Aberto pra extensão, fechado pra modificação
- **L**iskov Substitution: Subclasses substituem superclasses sem quebrar
- **I**nterface Segregation: Interfaces específicas, não genéricas
- **D**ependency Inversion: Depende de abstrações, não implementações

**Na prática:**
- Funções <= 20 linhas (preferencialmente)
- Nomes descritivos (não `x`, `temp`, `data`)
- Sem código duplicado (DRY)

### 3. Estrutura de Pastas (FastAPI Backend)
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── routers/             # Rotas por domínio (properties.py, users.py)
│   ├── services/            # Lógica de negócio
│   ├── models/              # Modelos de dados (Pydantic)
│   ├── schemas/             # DTOs (request/response)
│   ├── database/            # Conexão, migrations
│   └── config.py            # Variáveis de ambiente
├── tests/
└── requirements.txt / pyproject.toml
```

### 4. Type Hints (Obrigatório)
```python
# ❌ ERRADO
def scrape_properties(url):
    return []

# ✅ CORRETO
def scrape_properties(url: str, timeout_ms: int = 45_000) -> list[dict]:
    """Faz scraping de imóveis."""
    properties: list[dict] = []
    return properties
```

### 5. Tratamento de Erros
- **Scraper:** Resiliente a mudanças de layout, retries, logging
- **API:** HTTP status codes corretos (400, 404, 500, etc.)
- **Db:** Transações com rollback automático

```python
# Exemplo: Scraper resiliente
try:
    page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
except PlaywrightTimeoutError as e:
    print(f"✗ Timeout: {e}")
    raise
```

### 6. Versionamento com Git
- **Branches:** `feature/nome-da-tarefa`, `fix/nome-do-bug`, `chore/nome-da-task`
- **Commits Semânticos (em PORTUGUÊS):**
  - `feat:` Nova funcionalidade
  - `fix:` Correção de bug
  - `docs:` Apenas documentação
  - `refactor:` Refatoração sem mudança de comportamento
  - `chore:` Dependências, configs, setup

- **Mensagens de Commit (Máximo 2 linhas):**
  - Linha 1: Tipo + descrição (~72 caracteres)
  - Linha 2 (opcional): Contexto ou detalhes adicionais
  - Descrever *o quê* foi feito, não *como*

```bash
# ✅ CORRETO (Breve, português, semântico)
git commit -m "feat: adiciona geração de ID com SHA256"
git commit -m "fix: corrige lógica de dedup
Ajusta set de IDs duplicados após paginação"

# ❌ ERRADO
git commit -m "feature: added property ID generation with SHA256"
git commit -m "atualiza tudo"
git commit -m "WIP"
```

- **Pull Requests (Máximo 4 parágrafos):**
  - Parágrafo 1: O que foi feito e por quê
  - Parágrafo 2: Mudanças principais e impacto
  - Parágrafo 3: Testes e validações realizadas
  - Parágrafo 4 (opcional): Próximos passos ou contexto
  - Use templates de PR quando disponível
  - Incluir checklist, links e evidências quando necessário

### 7. Nomes de Variáveis e Funções
```python
# ❌ ERRADO
p = get_data()
props = [x for x in p if x['price'] > 1000]

# ✅ CORRETO
properties = get_properties_from_api()
expensive_properties = [prop for prop in properties if prop['price'] > 1000]
```

### 8. Docstrings (Google Style)
```python
def generate_property_id(url: str) -> str:
    """Gera ID hexadecimal único a partir da URL do imóvel.
    
    Usa SHA-256 da URL e retorna os primeiros 12 caracteres hex.
    Garante identificação consistente e única para cada imóvel.
    
    Args:
        url: String com a URL do imóvel (ex: https://dfimoveis.com.br/imovel/...)
    
    Returns:
        String com 12 caracteres hexadecimais (ex: "7c2bf7dac4f5")
    
    Raises:
        ValueError: Se url for vazia ou None
    
    Example:
        >>> generate_property_id("https://example.com/imovel/1")
        '7c2bf7dac4f5'
    """
```

### 9. Testes
- **Framework:** pytest
- **Cobertura:** >= 80%
- **Estrutura:** `test_module_name.py` next to source

```bash
uv run pytest tests/ -v --cov=app
```

### 10. Ambiente com `uv`
**Grupos de Dependências (no `pyproject.toml`):**
```toml
[dependency-groups]
scraping = ["beautifulsoup4", "playwright"]
api = ["fastapi", "uvicorn"]
data = ["pyspark", "pandas"]
ml = ["scikit-learn", "xgboost", "mlflow"]
notebook = ["jupyter", "jupyterlab", "pandas", "matplotlib"]
test = ["pytest", "pytest-cov"]
dev = ["ruff", "black", "mypy"]
```

**Comandos:**
```bash
uv sync                              # Sync all dependencies
uv sync --group scraping             # Sync scraping group only
uv add --group data pandas           # Add to specific group
uv run python script.py              # Run script with uv Python
uv run pytest                        # Run tests
```

---

## ✅ Status Sprint 1: Fundações e Concepção do Produto (CONCLUÍDO)

### 📊 Epic 1: Fundações e Concepção do Produto

**Tarefas Completas:**
- ✅ **Modelo de Dados (ER Diagram)** - `docs/er_diagram.mmd`
  - Entidades: Property, User, Favorites, ML_Predictions
  - Relacionamentos: User-Favorites, Property-Predictions
  - Normalização: 3NF

- ✅ **Estrutura Analítica (EAP)** - `docs/eap_diagram.mmd`
  - 5 Epics mapeados (Fundações, Descoberta, Diagnóstico, Assistente, Jornada)
  - Features e Tasks por Sprint
  - Rastreabilidade completa

- ✅ **Protótipos de Telas em Figma**
  - Wireframes: Listagem, Detalhe, Favoritos, Chat
  - Componentes visuais: Cards, Filtros, Chat UI
  - Design System: Cores, Tipografia, Espaçamento

- ✅ **Histórias de Usuário & Critérios de Aceitação**
  - 5 User Stories (uma por Epic)
  - Critérios de Aceitação para cada Feature
  - Rastreadas no Azure Boards

- ✅ **Taskboard & Planejamento Sprint 1**
  - Backlog estruturado com 6 tarefas
  - Representantes de cada funcionalidade
  - Timeline e estimativas

**Entregáveis Gerados:**
- Documentação de arquitetura (CONTEXT.md, README.md)
- Guia técnico (docs/SCRAPER_GUIDE.md)
- Diagramas Mermaid (ER, EAP)
- Backlog em CSV (docs/backlog_sprint.csv)

### Estrutura de Dados Coletada
Campos por imóvel:
```json
{
  "id_hex": "7c2bf7dac4f5",           // ID único (SHA-256, 12 chars)
  "titulo": "SMPW Quadra 4, PARK WAY",
  "url": "https://dfimoveis.com.br/imovel/...",
  "preco": "26.900",
  "descricao": "Texto resumido...",
  "quartos": "3 Quartos",
  "suites": "3 Suítes",
  "vagas": "4 Vagas",
  "area": "N/A",
  "imagem": "https://img.dfimoveis.com.br/...",
  "imobiliaria": "Neves Teixeira Imóveis",
  "data_extracao": "2026-04-07T06:05:27.120767"
}
```

---

## 🚀 Sprint 2: Descoberta e Exploração de Imóveis (PRÓXIMO)

### 🔷 Epic 2: Descoberta e Exploração de Imóveis

**Feature 2.1: Vitrine e Scraping Base**
- [ ] **Scraper Funcional** (`scrapper/scrapper.py`)
  - Extração de imóveis por página
  - Suporte a paginação
  - Deduplicação automática de IDs
  - ID Hexadecimal único (SHA-256)
  - Saída em CSV e JSON
  - Documentação completa

- [ ] **Jupyter Notebook** (`notebooks/eda.ipynb`)
  - Carregamento e exploração de dados
  - Análise exploratória (EDA)
  - Visualizações iniciais

- [ ] **Pipelines de Ingestão** (Estrutura)
  - Padrão Medalhão: Bronze → Silver → Gold
  - Documentação de fluxo

- [ ] **API FastAPI (Rotas Iniciais)**
  - Estrutura: routers, services, models, schemas
  - Rota: `GET /api/properties` - Listagem básica

- [ ] **Frontend React (Componentes Base)**
  - Scaffolding com Create React App + Tailwind
  - Componentes: Cards de imóveis
  - Integração com API

**Feature 2.2: Busca e Filtros Dinâmicos**
- [ ] **Expandir Scraper**
  - Dados geográficos (bairro, localização)
  - Links originais para imóveis

- [ ] **Rotas Parametrizadas (Backend)**
  - `GET /api/properties?preco_min=X&preco_max=Y`
  - `GET /api/properties?bairro=Y`
  - `GET /api/properties/{id}` - Detalhe

- [ ] **Queries SQL Otimizadas**
  - Filtros complexos
  - Índices em PostgreSQL

- [ ] **Barra de Filtros (Frontend)**
  - Componente SearchBar
  - Filtros laterais interativos
  - Conectar com parâmetros de busca

- [ ] **Performance**
  - Homologação com base populada
  - Otimização de queries

---

## 🎨 Sprint 3+: Inteligência e Jornada (FUTURO)

### 💰 Epic 3: Diagnóstico de Preço (O 'Moneyball')

**Feature 3.1: Termômetro de Oportunidade**
- [ ] **Preparação de Dataset**
  - Limpeza de dados
  - Feature engineering (localização, tamanho, amenidades)

- [ ] **Treinamento - XGBoost**
  - Modelo classificador: Caro / Justo / Barato
  - Rastreamento com MLflow

- [ ] **Deploy - Azure ML**
  - Registrar modelo
  - Managed Online Endpoint
  - Real-time inference

- [ ] **Frontend - Tags Visuais**
  - Design das classificações
  - Integração com API de previsão

### 💬 Epic 4: Assistente Virtual Especialista (Chat)

**Feature 4.1: Motor de IA e Interface**
- [ ] **Treinamento Vanna.ai**
  - Schema PostgreSQL
  - Exemplos de queries

- [ ] **Text-to-SQL Backend**
  - Rota: `POST /api/chat`
  - Execução segura de SQL
  - Logging e auditoria

- [ ] **Chat UI (Frontend)**
  - Modal flutuante
  - Histórico de conversas
  - Sugestões

### ⭐ Epic 5: Jornada Personalizada e Confiabilidade

**Feature 5.1: Gestão de Favoritos**
- [ ] **Backend - Persistência**
  - Rotas: `POST /api/favorites`, `DELETE /api/favorites/{id}`
  - Ligação com usuários

- [ ] **Frontend - Página Meus Favoritos**
  - Botão Like/Unlike interativo
  - Página dedicada
  - Integração com histórico

**Feature 5.2: Disponibilidade Pública (Go Live)**
- [ ] **Infraestrutura em Nuvem**
  - ADLS Gen2
  - PostgreSQL
  - Azure App Service / Static Web Apps

- [ ] **Deployment Completo**
  - CI/CD com Azure Pipelines
  - Deploy Backend + Frontend
  - CORS e variáveis de produção

- [ ] **Documentação & Reports**
  - Documentação técnica
  - Relatórios finais
  - SLAs e monitoring

---

## 🔄 Fluxo de Dados (Visão Geral)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. WEB SCRAPING (Playwright + BeautifulSoup)               │
│    └─> DFimoveis.com.br → JSON/CSV files                  │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. EXTRACT → ADLS Gen2 Bronze (/bronze/raw/)               │
│    └─> Azure Data Factory Trigger                          │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. TRANSFORM → Databricks (PySpark)                        │
│    Bronze (/bronze/) → Silver (/silver/cleaned/)           │
│    Clean, validate, deduplicate, enrich                    │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. LOAD → PostgreSQL (from Silver + Gold)                  │
│    Silver data → PostgreSQL `properties` table             │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. API & ML (FastAPI)                                      │
│    ├─ GET /properties → From PostgreSQL                    │
│    ├─ POST /chat → Text-to-SQL (Vanna.ai)                 │
│    └─ POST /predict_price → ML Endpoint                   │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. FRONTEND (React + Tailwind)                             │
│    ├─ Azure Static Web Apps                                │
│    ├─ Calls backend API                                    │
│    └─ Real-time dashboards                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Estrutura Atual do Projeto

```
Projeto Integrador III 2.0/
├── CONTEXT.md                          # ← VOCÊ ESTÁ AQUI (Guia de Codificação)
├── README.md                           # ← Visão geral do projeto
├── pyproject.toml                      # Config `uv` com grupos de deps
├── main.py                             # Entry point (TODO)
│
├── scrapper/                           # 🔷 WEB SCRAPING (Sprint 1 ✅)
│   └── scrapper.py                     # Scraper com paginação & dedup
│
├── notebooks/                          # 📊 ANÁLISE DE DADOS (Sprint 1 ✅)
│   └── eda.ipynb                       # Exploração dos dados coletados
│
├── docs/
│   ├── SCRAPER_GUIDE.md               # 📖 Como usar o scraper
│   ├── er_diagram.mmd                 # 🏗️ Modelo de Dados (Sprint 1 ✅)
│   ├── eap_diagram.mmd                # 📊 Estrutura Analítica (Sprint 1 ✅)
│   ├── backlog_sprint.csv             # Backlog com histórias
│   └── [PDFs de requisitos]
│
├── backend/                            # 🚀 API BACKEND (Sprint 2 🔄)
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/                   # Rotas por domínio
│   │   ├── services/
│   │   ├── models/
│   │   └── schemas/
│   └── tests/
│
├── frontend/                           # 🎨 FRONTEND (Sprint 2 🔄)
│   ├── src/
│   │   ├── components/                # React components
│   │   ├── pages/
│   │   └── styles/
│   └── package.json
│
└── ml/                                 # 🤖 MACHINE LEARNING (Sprint 3 ⏳)
    ├── models/
    ├── preprocessing/
    └── evaluation/
```

---

## 🎓 Referências Rápidas para Agentes IA

Quando receber instruções, procure por:
1. **Regras de código** → Seção "Regras de Codificação" deste arquivo
2. **Como usar o scraper** → [docs/SCRAPER_GUIDE.md](docs/SCRAPER_GUIDE.md)
3. **Visão do projeto** → [README.md](README.md)
4. **Stack Azure** → Seção "Stack Tecnológico" deste arquivo
5. **Estado de progresso** → Seções "Status Sprint X" deste arquivo

---

## 📞 Suporte & Próximos Passos

Dúvidas? Consulte:
- Este CONTEXT.md (regras e arquitetura)
- README.md (overview do projeto)
- docs/SCRAPER_GUIDE.md (instruções do scraper)
- Código-fonte comentado (docstrings em português)

---

**Última atualização:** 2026-04-07  
**Versão:** 1.1.0 (Sprint 1 ✅ + Sprint 2 🔄)  
**Ciclo de Desenvolvimento:** Epic1 → Epic2 → Epics3-5 → Deploy