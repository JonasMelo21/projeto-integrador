# ML Pipeline — RentMaster

Treinamento e avaliação do modelo Random Forest para classificar preços de aluguel em 3 categorias: **Barato** / **Justo** / **Caro**.

## 🎯 Objetivo

Dado um imóvel (bairro, área, quartos, etc), o modelo prediz se o preço é justo, barato ou caro comparado ao mercado local.

## 📁 Estrutura

- **`config.py`** — Configurações globais
  - Features, hiperparâmetros, caminhos, seed

- **`data.py`** — Carregamento de dados
  - `load_gold_splits()` — Lê parquets temporais da Gold
  - Remove suspeitos APENAS do treino, mantém validação/teste realista

- **`train_simple.py`** — Treinamento
  - Pipeline: OneHotEncoder (categóricas) + Median Imputer (numéricas) + Random Forest
  - Salva modelo em `models/random_forest_optimized.joblib`

- **`evaluate.py`** — Avaliação
  - Calcula acurácia, F1-score, confusion matrix no test set

- **`optimize.py`** — Otimização
  - GridSearch de hiperparâmetros
  - Salva melhores em `models/experiment_log.json`

- **`baselines.py`** — Modelos naive
  - Zero Rule (sempre prediz classe majoritária) — benchmark mínimo

- **`tracker.py`** — Histórico de experimentos
  - Log de cada treino (hiperparâmetros, acurácia, timestamp)

## 🚀 Executar

```bash
# Setup
uv sync --group ml_pipeline

# Treinar novo modelo
uv run python ml_pipeline/train_simple.py
# Output: models/random_forest_optimized.joblib

# Avaliar em test set
uv run python ml_pipeline/evaluate.py

# Otimizar hiperparâmetros
uv run python ml_pipeline/optimize.py

# Comparar com baseline
uv run python ml_pipeline/baselines.py
```

## 🔑 Features Importantes

| Feature | Tipo | Descrição |
|---------|------|-----------|
| `bairro_area_cross` | categorical | Bairro + categoria de tamanho |
| `tipo_imovel` | categorical | Apt/Casa/Loja (extraído de URL/título) |
| `imobiliaria_hash` | numerical | Imobiliária hasheada (0-1023) |
| `area_m2` | numerical | Área normalizada |
| `quartos` | integer | # quartos |
| `suites` | integer | # suites |
| `vagas` | integer | # vagas |

## 📊 Fluxo Completo

```
Data Pipeline (Gold)
    ↓
Load splits (train/valid/test)
    ↓
Remove suspeitos do treino
    ↓
Pré-processamento (OneHot + Median Imputer)
    ↓
Treinar Random Forest
    ↓
Avaliar em valid/test
    ↓
Salvar modelo (.joblib)
    ↓
Backend carrega e faz inferência
```

## 🔧 O que Contribuir

| Tarefa | Arquivo |
|--------|---------|
| Ajustar hiperparâmetros | `config.py` |
| Testar novo algoritmo | `train_simple.py` |
| Implementar métrica customizada | `evaluate.py` |
| Adicionar feature | `data.py` |
| Automação de experimentos | `tracker.py` |

## ⚠️ Pontos Importantes

- 🛡️ **Sem leakage**: Split temporal, estatísticas do treino não vazam para validação/teste
- 🎲 **Seed fixo**: `random_state=42` para reprodutibilidade
- ⚖️ **Class weight balanceado**: Modelo presta atenção em "Barato" e "Caro" também
- 📈 **Métrica principal**: F1-score (melhor que acurácia pura em dados desbalanceados)

## 🚨 Se o modelo não treinar

| Erro | Solução |
|------|---------|
| "ml_train.parquet não existe" | Execute `data_pipeline/medallion/silver_to_gold.py` |
| Overfitting | Aumentar `min_samples_split`, reduzir `max_depth` |
| Underfitting | Aumentar `n_estimators`, reduzir `min_samples_split` |
