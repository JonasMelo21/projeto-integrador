# ML Pipeline - RentMaster

Módulo responsável pelo **treinamento**, **avaliação** e **inferência** do modelo de classificação de preços. O pipeline executa a transformação de dados brutos em um modelo preditivo capaz de classificar imóveis como "Barato", "Preço Justo" ou "Caro".

---

## 🏗️ Arquitetura do ML Pipeline

```
Data Pipeline (Gold)
       ↓
   ML Pipeline
       ├── 1. Carregar dados Gold
       ├── 2. Split temporal (train/valid/test)
       ├── 3. Feature engineering
       ├── 4. Treinar Random Forest
       ├── 5. Avaliar em valid/test
       ├── 6. Salvar modelo
       └── 7. Gerar relatório
       ↓
   Model Artifact (joblib)
       ↓
   Backend (carrega + faz inferência)
```

---

## 📁 Estrutura de Arquivos

```
ml_pipeline/
├── __init__.py               # Exports principais
├── config.py                 # Configurações globais (caminhos, hiperparâmetros)
├── data.py                   # Carregamento e processamento de dados
├── train_simple.py           # Treinamento do Random Forest
├── evaluate.py               # Avaliação de modelos
├── optimize.py               # Otimização de hiperparâmetros
├── baselines.py              # Modelos baseline para comparação
├── tracker.py                # Rastreamento de experimentos
├── models/
│   ├── random_forest_optimized.joblib    # Modelo em produção
│   ├── random_forest_v1.joblib           # Versão anterior
│   └── experiment_log.json               # Histórico de treinos
└── README.md                 # Este arquivo
```

---

## 🔑 Arquivos Principais

### `config.py`
Define variáveis globais do pipeline:
- Caminhos de entrada (Gold) e saída (modelos)
- Configurações de split (train/val/test)
- Hiperparâmetros do Random Forest
- Seeds para reprodutibilidade

```python
FEATURE_COLUMNS = [
    "bairro_area_cross",    # Feature cross
    "imobiliaria_hash",     # Imobiliária com hash
    "quartos", "suites", "vagas"  # Features númericas
]

TARGET_COLUMN = "target_preco"  # 0: Barato, 1: Justo, 2: Caro
```

### `data.py`
Orquestra o carregamento e processamento de dados:

**Funções principais:**
- `load_gold_fact()` - Lê parquet da camada Gold (`data/gold/fact_imoveis_gold.parquet`)
- `split_time_based()` - Realiza split temporal (não aleatório!)
  - 70% treino (dados históricos)
  - 15% validação (período intermediário)
  - 15% teste (dados mais recentes)

**Por que split temporal?**
Imóveis têm tendências sazonais. Um split aleatório causaria leakage temporal (treinar em dados recentes e testar em históricos).

### `train_simple.py`
Implementa o treinamento end-to-end:

**Pipeline de pré-processamento:**
1. **Categorical encoder**: OneHotEncoder para `bairro_area_cross`
2. **Numerical imputation**: MedianImputer para features numéricas
3. **Estimator**: RandomForestClassifier

**Workflow:**
```python
1. Carrega dados Gold
2. Split temporal (train/val/test)
3. Cria pipeline sklearn (preprocessor + modelo)
4. Treina no split de treino
5. Avalia em validação
6. Salva modelo em joblib
7. Gera relatório de acurácia/F1
```

**Saída:**
- `ml_pipeline/models/random_forest_optimized.joblib` (modelo treinado)
- Relatório de acurácia em stdout

### `evaluate.py`
Avalia performance do modelo:

**Métricas calculadas:**
- Acurácia (global)
- F1-score (por classe)
- Classification report (precision/recall/f1)
- Confusion matrix

**Teste em dados não vistos (test set):**
```bash
uv run python ml_pipeline/evaluate.py
# Resultado: F1-score no test set
```

### `baselines.py`
Implementa modelos baseline para comparação:
- **Zero Rule**: Prediz sempre a classe majoritária (baseline mínimo)
- Serve como benchmark para validar que o Random Forest aprende algo

### `tracker.py`
Rastreamento de experimentos:
- Salva histórico de cada treino
- Registra hiperparâmetros, acurácia, timestamp
- Permite comparação entre versões
- Arquivo de saída: `ml_pipeline/models/experiment_log.json`

### `optimize.py`
Otimização de hiperparâmetros (GridSearch/RandomSearch):
- Testa combinações de `n_estimators`, `max_depth`, `min_samples_split`
- Retorna melhores hiperparâmetros
- Salva relatório de performance

---

## 📊 Fluxo Completo de Dados

### 1️⃣ Entrada: Dados Gold

A Gold fornece dados já com feature engineering:

| Coluna | Descrição | Tipo |
|--------|-----------|------|
| `bairro_area_cross` | Bairro + categoria de área | categorical |
| `imobiliaria_hash` | Imobiliária hasheada (0-1023) | numerical |
| `quartos` | # de quartos | integer |
| `suites` | # de suites | integer |
| `vagas` | # de vagas | integer |
| `target_preco` | **Alvo**: 0/1/2 | integer |

### 2️⃣ Split Temporal

```
Timeline de dados
├─ 70% TRAIN (histórico)
├─ 15% VAL (intermediário)
└─ 15% TEST (recente) ← Mais rigoroso
```

Razão: Dados mais recentes são mais representativos do mercado atual.

### 3️⃣ Pré-processamento

```
Input Features
├─ bairro_area_cross
│  └─ OneHotEncoder → 50+ dimensões binárias
├─ imobiliaria_hash
│  └─ MedianImputer (já numérico)
├─ quartos/suites/vagas
│  └─ MedianImputer (preenchimento de NaN)
└─ Output: Features matrix pronta
```

### 4️⃣ Treinamento

```
Random Forest (100 árvores by default)
├─ max_depth: 20
├─ min_samples_split: 5
├─ criterion: gini
└─ Treinado em 70% dos dados
```

### 5️⃣ Avaliação

```
Validation Set (15%)
├─ Acurácia: ~65%
├─ F1-score: 0.62
└─ Confusion matrix
```

### 6️⃣ Saída: Modelo Serializado

```
ml_pipeline/models/random_forest_optimized.joblib
↓
Backend carrega em startup
↓
Usa para predição em tempo real
```

---

## 🚀 Como Rodar

### Treinar Modelo Novo

```bash
# Instalar dependências de ML
uv sync --group ml_pipeline

# Treinar (lê Gold, produz modelo)
uv run python ml_pipeline/train_simple.py

# Output esperado:
# 🤖 Modelo de ML carregado com sucesso
# Acurácia no validation set: 0.65
# F1-score: 0.62
# ✅ Modelo salvo em ml_pipeline/models/random_forest_optimized.joblib
```

### Avaliar Modelo Atual

```bash
uv run python ml_pipeline/evaluate.py

# Avalia em test set (dados não vistos)
```

### Otimizar Hiperparâmetros

```bash
uv run python ml_pipeline/optimize.py

# Testa diferentes combinações
# Salva melhores em experiment_log.json
```

### Comparar com Baseline

```bash
uv run python ml_pipeline/baselines.py

# Resultado:
# Zero Rule (always predict 1): 45%
# Random Forest: 65%
# Delta: +20% acurácia
```

---

## 🔧 Configurar Hiperparâmetros

Edite `ml_pipeline/config.py`:

```python
# Número de árvores
N_ESTIMATORS = 200  # default: 100

# Profundidade máxima
MAX_DEPTH = 25  # default: 20

# Mínimo de amostras por split
MIN_SAMPLES_SPLIT = 3  # default: 5

# Seed para reprodutibilidade
RANDOM_STATE = 42
```

---

## 📊 Interpretabilidade

### Feature Importance

O Random Forest permite identificar quais features importam:

```python
# No arquivo train_simple.py
importances = model.feature_importances_
for feature, importance in sorted(zip(features, importances)):
    print(f"{feature}: {importance:.4f}")
```

**Exemplo esperado:**
```
bairro_area_cross: 0.35  (maior influência)
imobiliaria_hash: 0.28
quartos: 0.20
vagas: 0.12
suites: 0.05
```

### Explicação de Predição Individual

Quando o backend prediz para um imóvel:

```
Imóvel: Apartamento 2 quartos, 75m², Plano Piloto
Features:
- bairro_area_cross: "Plano Piloto_Padrao"
- imobiliaria_hash: 512
- quartos: 2
- suites: 1
- vagas: 1

Random Forest → Predição: 1 (Preço Justo) ✅
```

---

## 📋 Dependências

Veja o grupo `ml_pipeline` em `pyproject.toml`:

```toml
ml_pipeline = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.9.0",
    "joblib>=1.5.3",
]
```

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| Erro "fact_imoveis_gold.parquet não encontrado" | Execute `data_pipeline/medallion/silver_to_gold.py` primeiro |
| Modelo muito lento (overfitting) | Aumentar `min_samples_split`, reduzir `max_depth` |
| Modelo muito simples (underfitting) | Aumentar `n_estimators`, reduzir `min_samples_split` |
| Acurácia ruim | Verificar feature engineering na Gold (não enviesado?) |
| Seed não reproduz | Adicionar `np.random.seed()` em `config.py` |

---

## 🔄 Workflow Completo do Projeto

```
1. WebScraper (data_pipeline/scraper/)
   ↓ JSON com imóveis brutos
2. Bronze Layer (data/bronze/)
   ↓ Dados crus
3. Bronze → Silver (bronze_to_silver.py)
   ↓ Limpos + padronizados
4. Silver Layer (data/silver/)
   ↓ Parquet normalizado
5. Silver → Gold (silver_to_gold.py)
   ↓ Features engineered
6. Gold Layer (data/gold/)
   ↓ Pronto para ML
7. ⭐ ML Pipeline (treina modelo)
   ↓ Random Forest
8. Model Artifact (joblib)
   ↓ Carregado pelo backend
9. Backend (inferência em tempo real)
   ↓ Classifica imóveis
10. Mobile (lista com preços justos/caros)
```

---

## 📚 Referências

- [Scikit-Learn RandomForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- [Joblib para serialização](https://joblib.readthedocs.io/)
- [Time-based train/test split](https://en.wikipedia.org/wiki/Training%2C_validation%2C_and_test_sets#Time_series)

---

## 🎯 Próximos Passos (Roadmap)

- [ ] Implementar GridSearchCV automático
- [ ] Adicionar XGBoost como alternativa
- [ ] Implementar MLOps (model registry, versioning)
- [ ] Criar UI para visualizar feature importance
- [ ] Adicionar explicabilidade (SHAP values)
- [ ] Implementar A/B testing de modelos

---

**Status**: ✅ Em produção com Random Forest

**Última Atualização**: Setembro 2026
