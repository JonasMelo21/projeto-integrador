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
- **Python:** BeautifulSoup, Playwright
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
time-tracking = ["requests", "python-dotenv"]
```

**Comandos:**
```bash
uv sync                              # Sync all dependencies
uv sync --group scraping             # Sync scraping group only
uv add --group data pandas           # Add to specific group
uv run python script.py              # Run script with uv Python
uv run pytest                        # Run tests
```

### 11. Time Tracking Automático (NOVA REGRA - IMPORTANTE!)

**Objetivo:** Rastrear automaticamente horas dedicadas a cada funcionalidade/módulo do projeto.

**Como funciona:**
1. **Setup WakaTime** (gratuito):
   - Instalar extensão VS Code: "WakaTime"
   - Criar conta: https://wakatime.com
   - Copiar API Key e adicionar em `.env`: `WAKATIME_API_KEY=xxx`

2. **Configuração Automática:**
   - Git hook `.git/hooks/post-commit` exporta dados ao fazer commit
   - Dados salvos em `.time-tracking/archive/` (não vai pro repositório)
   - Arquivo ignorado em `.gitignore`

3. **Exportar Dados:**
   ```bash
   uv sync --group time-tracking        # Instalar dependências
   python .time-tracking/export_wakatime.py
   ```

4. **Resultado:**
   ```json
   // .time-tracking/archive/wakatime-20260408.json
   {
     "2026-04-08": {
       "total_hours": 31.25,
       "projects": {
         "scraper": { "hours": 28.5, "percent": 91.2 },
         "backend": { "hours": 2.75, "percent": 8.8 }
       }
     }
   }
   ```

5. **Para Preenchimento Manual no Azure DevOps:**
   - Abra o arquivo JSON gerado
   - Leia as horas totais du projeto
   - Preencha manualmente no card da task (ou use MCP después)

**Regras Importantes:**
- ✅ WakaTime é gratuito (com limite de 7 dias de histórico)
- ✅ Dados locais são preservados em `.time-tracking/archive/`
- ✅ Git hook roda automaticamente após commits em branches de feature/fix
- ✅ Arquivo `.time-tracking/` é ignorado pelo git (dados locais apenas)
- ❌ Não versionamos dados de time tracking no repositório
- ❌ Arquivo `.env` com API key também é ignorado (segurança)

**Iniciar nova funcionalidade:**
```bash
# 1. Criar branch
git checkout -b feature/nova-funcionalidade

# 2. Trabalhar normalmente (WakaTime rastreia)

# 3. Fazer commits semânticos
git commit -m "feat: implementa algo novo"
# ← Git hook executa export_wakatime.py automaticamente

# 4. Ao terminar, exportar manualmente se quiser
python .time-tracking/export_wakatime.py

# 5. Verificar horas e preencher em Azure DevOps
cat .time-tracking/archive/wakatime-*.json
```

---

### 12. Tratamento de Erros de Integração com APIs (REGRA CRÍTICA!)

**Objetivo:** Estabelecer protocolo padrão para falhas em integrações com APIs externas (WakaTime, Azure DevOps, etc).

**Regra de Ouro:**
Quando uma integração com API externa retorna erro de autenticação/autorização (401, 403) ou credencial inválida:
1. ⛔ **PARAR IMEDIATAMENTE** a execução do script/task
2. 📢 **REPORTAR** o erro detalhadamente ao usuário
3. ⏸️ **AGUARDAR** instruções/credenciais corretas do usuário
4. ❌ **NÃO CONTINUAR** com fallbacks automáticos ou valores padrão

**Exemplos de Erros que Acionam Esta Regra:**
```
- 401 Unauthorized (API key inválida, expirada ou revogada)
- 403 Forbidden (Permissões insuficientes)
- "Invalid credentials" (Texto de erro da API)
- "Authentication failed" (Falha na autenticação)
- "API key not found" (Chave não configurada corretamente)
```

**Implementação em Código:**
```python
# ✅ CORRETO - Parar e reportar
try:
    response = requests.get(
        "https://api.exemplo.com/data",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code in [401, 403]:
        print(f"\n❌ ERRO CRÍTICO DE AUTENTICAÇÃO:")
        print(f"   Status: {e.response.status_code}")
        print(f"   Mensagem: {e.response.text}")
        print(f"   Ação: Verifique a API key em .env e tente novamente\n")
        sys.exit(1)  # ← Parar aqui
    else:
        # Outros erros podem ter retry logic
        pass

# ❌ INCORRETO - Silenciar erros
try:
    response.raise_for_status()
except:
    pass  # Continuar como se nada tivesse acontecido
```

**Regras Específicas por Serviço:**

| Serviço | Erro | Ação |
|---------|------|------|
| **WakaTime** | 401 / API Key inválida | Parar. Validar em https://wakatime.com/settings/account |
| **Azure DevOps** | 401 / PAT expirado | Parar. Regenerar PAT em Azure DevOps |
| **OpenAI** | 401 / Chave inválida | Parar. Verificar quota e validade da chave |
| **PostgreSQL** | Connection refused | Parar. Verificar string de conexão e credenciais |

**Comunicação ao Usuário:**
```
❌ API INVÁLIDA - ERRO CRÍTICO
─────────────────────────────────────────
Serviço: WakaTime
Erro: 401 Unauthorized
Mensagem: API key inválida ou expirada

O que fazer:
1. Verifique a chave em .env
2. Regenere se necessário em https://wakatime.com/settings/account
3. Execute novamente

Aguardando seu feedback...
```

**Nunca Faça:**
- ❌ Usar valores default/mock quando API falha
- ❌ Continuar execução com dados parciais
- ❌ Esconder mensagens de erro
- ❌ Tentar múltiplas retentativas sem informar o usuário
- ❌ Assumir que o erro se resolve sozinho

---

### 13. WakaTime - Status Bloqueado (INVESTIGAÇÃO NECESSÁRIA)

**Status:** ❌ **NÃO FUNCIONAL** - Setup completo mas API retorna 401 Unauthorized persistente

**O que foi implementado:**
- ✅ Scripts criados: `test_wakatime.py`, `export_wakatime.py`, Git hook
- ✅ Dependências instaladas: `requests`, `python-dotenv`
- ✅ Configuração: `.env` com WAKATIME_API_KEY
- ✅ `.wakatime.cfg` atualizado com API key
- ✅ Múltiplas API keys testadas (3 diferentes)

**problema Relatado:**
```
❌ Erro de Autenticação: 401 Unauthorized
   URL: https://wakatime.com/api/v1/users/current
   Mensagem: API Key inválida ou expirada
```

**Investigações Realizadas:**
1. ✅ API keys testadas no arquivo `.env`
2. ✅ API keys testadas no `~/.wakatime.cfg`
3. ✅ Email da conta WakaTime confirmado
4. ✅ Sintaxe da API key validada (formato: `waka_xxxx`)
5. ✅ Diferentes API keys regeneradas

**Possíveis Causas:**
- API keys regeneradas podem estar expiradas ou revogadas
- Conta WakaTime pode estar em estado suspenso
- Possível problema de permissões da API
- Rate limiting ou bloqueio de IP

**Como Reativar (quando resolvido):**
1. Acessar https://wakatime.com/settings/account
2. Verificar status da conta
3. Regenerar API key completamente
4. Copiar nova chave para `.env` e `.wakatime.cfg`
5. Executar `uv run python .time-tracking/test_wakatime.py`
6. Se sucesso, remover este aviso e atualizar esta seção

**Alternativa (Implementada):**
- Seção 11 (Time Tracking Automático) ainda documenta o sistema para **quando WakaTime voltar a funcionar**
- Scripts já estão prontos e testados (exceto autenticação)
- Git hook está instalado e pronto

**GitHub Issue Criado:**
- Issue #X: "WakaTime API retorna 401 Unauthorized mesmo com credenciais corretas"
- Labels: `bug`, `blocked`, `devops`, `investigation`
- Status: INVESTIGAÇÃO NECESSÁRIA

---



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

## 🚀 Sprint 2: Descoberta e Exploração de Imóveis (INICIADO) 🔄

### 🔷 Epic 2: Descoberta e Exploração de Imóveis

**Feature 2.1: Vitrine e Scraping Base**
- [x] **Scraper Funcional** (`scrapper/scrapper.py`) ✅
  - ✅ Extração de imóveis por página (30+ por página)
  - ✅ Suporte a paginação com deduplicação automática de IDs
  - ✅ ID Hexadecimal único (SHA-256, 12 chars)
  - ✅ Extração de ÁREA corrigida (procura por "m²")
  - ✅ Extração de MÚLTIPLAS IMAGENS (array de URLs, filtrando base64)
  - ✅ Saída em CSV e JSON
  - ✅ Documentação completa no [docs/SCRAPER_GUIDE.md](docs/SCRAPER_GUIDE.md)

- [x] **Docker Containerizado** ✅
  - ✅ Dockerfile pronto com SDKs Azure
  - ✅ Build bem-sucedido
  - ✅ Testado localmente (2 páginas = 30 imóveis extraídos)
  - ✅ Suporte a env vars (NUM_PAGES, TIMEOUT_MS, FORMAT, UPLOAD_TO_ADLS)

- [x] **Upload para ADLS Gen2** ✅
  - ✅ Novo parâmetro `--upload-to-adls` no scraper
  - ✅ Autenticação via `DefaultAzureCredential()` (Managed Identity ready)
  - ✅ Upload testado: Arquivo JSON enviado com sucesso
  - ✅ 📍 Destino confirmado: `rentmasterstorageaccount/bronze/raw/imoveis_*.json`

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

---

## 🏗️ Arquitetura do Sistema (Visão Completa)

### Diagrama Visual - Fluxo End-to-End

Consulte o diagrama visual completo em:

📊 **[docs/diagrama_arq_rent_master.png](../docs/diagrama_arq_rent_master.png)**

Este diagrama ilustra toda a arquitetura Azure do RentMaster com os fluxos de dados entre componentes:

### Componentes Principais

#### 1. **Camada de Ingestão e Orquestração**
- **Azure Data Factory:** Orquestra pipelines de ingestão
- **web-scraper Python:** Executa em container (Docker) via ACI ou agendado
- **Fontes externas:** Portais imobiliários (DFimoveis, etc.)

#### 2. **Camada de Armazenamento - Data Lake (ADLS Gen2)**
- **Container Bronze:** Dados brutos extraídos (`/bronze/raw/`)
- **Container Silver:** Dados limpos e validados (`/silver/cleaned/`)
- **Container Gold:** Dados curados prontos para consumo (`/gold/curated/`)
- **Padrão Medalhão:** Qualidade progressiva de Bronze → Silver → Gold

#### 3. **Camada de Transformação**
- **Databricks Workspace:** Orquestra processamento PySpark
- **Notebooks PySpark:** Executam ETL (Limpeza, dedup, enriquecimento)
- **MLlib/Scikit:** Feature engineering para modelos de preço

#### 4. **Camada de Integração**
- **Banco de Dados:** Azure Database for PostgreSQL
- **Tabelas principais:**
  - `properties` (imóveis extraídos do Gold)
  - `user_favorites` (favoritos do usuário)
  - `price_predictions` (scores ML)
  - `chat_history` (histórico de conversas)

#### 5. **Camada de Aplicação (Backend)**
- **FastAPI** hospedado em **Azure App Service**
- **Rotas principais:**
  - `GET /api/properties` → Lista imóveis (queries PostgreSQL)
  - `POST /api/chat` → Chatbot (Vanna.ai Text-to-SQL)
  - `POST /api/predict-price` → ML Inference (Azure Machine Learning)
  - `GET /api/favorites` → Favoritos do usuário
- **Autenticação:** Azure Entra ID (Microsoft Entra)

#### 6. **Camada de Aplicação (Frontend)**
- **React + Tailwind CSS** hospedado em **Azure Static Web Apps**
- **Componentes principais:**
  - Listagem de imóveis com filtros dinâmicos
  - Cards com preço, localização, imagens
  - Barra de filtros (área, preço, localidade)
  - Chatbot flutuante integrado
  - Página de favoritos

#### 7. **Camada de IA e ML**
- **Vanna.ai + LangChain:** Traduz linguagem natural para SQL
- **Azure Machine Learning:** Hosting do modelo de preços
- **Modelo XGBoost:** Classifica preço (Caro/Justo/Barato)

### Fluxo Completo

```
1. Web Scraper (local/Docker) → extrai dados
                                  ↓
2. Azure Data Factory → dispara ingestão para ADLS Bronze
                        ↓
3. Databricks → processa Bronze → Silver
                (limpeza, dedup, enriquecimento)
                        ↓
4. Databricks + ML → enriquece e feature-engineering → Gold
                        ↓
5. PostgreSQL ← carregado do Gold
                        ↓
6. FastAPI Backend ← consome PostgreSQL
    ├─ GET /properties
    ├─ POST /chat (Text-to-SQL via Vanna)
    └─ POST /predict-price (ML Endpoint)
                        ↓
7. React Frontend + Static Web Apps
    ├─ Listagem com filtros
    ├─ Cards de imóveis
    ├─ Chatbot (conversas)
    └─ Favoritos
                        ↓
8. Usuário Final → visualiza e interage com dados
```

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