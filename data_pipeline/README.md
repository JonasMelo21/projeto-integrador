# Data Pipeline — RentMaster

ETL de imóveis: coleta → limpeza → ML-ready. Segue a arquitetura Medallion (Bronze → Silver → Gold).

## 📊 Fluxo de Dados

```
Scraper (site) → Bronze (bruto)
              ↓
         Silver (limpo)
              ↓
            Gold (ML-ready)
```

## 📁 Estrutura

- **`scraper/`** — Web scraping de imóveis (Playwright + BeautifulSoup)
  - `scraper_to_bronze.py` — Coleta dados brutos e salva em JSON
  - `debug_scraper.py` — Testes do scraper

- **`medallion/`** — Transformações de dados
  - `bronze_to_silver.py` — Limpeza, deduplicação, normalização, feature básicas
  - `silver_to_gold.py` — Feature engineering, splits temporais (70/15/15), estatísticas por bairro
  - `load_gold_to_supabase.py` — Carrega dados Gold no Supabase (prod)

- **`llm_audit/`** — Auditoria inteligente de qualidade
  - `chain.py` — Orchestração do LLM (validação de outliers/suspeitos)
  - `cli.py` — CLI para rodar auditoria
  - `data.py` — Carregamento de dados para auditoria
  - `schemas.py` — Tipos estruturados (Pydantic)
  - `prompts.py` — Prompts do LLM

## 🎯 Outputs Principais

| Camada | Arquivo | Descrição |
|--------|---------|-----------|
| **Bronze** | `data/bronze/*.json` | Dados brutos do scraper |
| **Silver** | `data/silver/imoveis_limpos.parquet` | Dados limpos e normalizados |
| **Silver** | `data/silver/dim_*.parquet` | Dimensões (bairros, imobiliárias) |
| **Gold** | `data/gold/ml_train.parquet` | 70% dos dados (treino) |
| **Gold** | `data/gold/ml_valid.parquet` | 15% dos dados (validação) |
| **Gold** | `data/gold/ml_test.parquet` | 15% dos dados (teste) |

## 🚀 Executar

```bash
# Sincronizar dependências
uv sync --group data_pipeline

# Rodar scraper
uv run python data_pipeline/scraper/scraper_to_bronze.py

# Bronze → Silver
uv run python data_pipeline/medallion/bronze_to_silver.py

# Silver → Gold (com splits e features)
uv run python data_pipeline/medallion/silver_to_gold.py

# Auditoria com LLM (opcional)
uv run python data_pipeline/llm_audit/cli.py
```

## 🔧 O que Contribuir

| Tarefa | Arquivo |
|--------|---------|
| Melhorar detecção de bairros | `scraper/scraper_to_bronze.py` |
| Adicionar features | `medallion/silver_to_gold.py` |
| Regras de suspeita | `medallion/bronze_to_silver.py` |
| Auditoria LLM | `llm_audit/prompts.py` |

## 📌 Pontos Importantes

- ⚠️ **Split temporal**: Treino (histórico) → Validação → Teste (recente) — evita leakage
- 🚨 **Suspeitos**: Marcados mas não removidos — auditados pelo LLM
- 🔑 **Features**: `bairro_area_cross`, `tipo_imovel`, `imobiliaria_hash`, `area_m2`, `quartos`, `suites`, `vagas`
- 📊 **Estatísticas**: Calculadas APENAS no treino, aplicadas aos outros splits
