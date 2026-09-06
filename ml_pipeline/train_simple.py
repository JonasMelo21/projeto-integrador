"""Phase 2: Simplest Machine Learning Models

Treinamento do modelo inicial (Random Forest) para o SmartRent AI.
O objetivo é estabelecer um fluxo completo de treinamento e superar 
a barreira dos 50% de acurácia do baseline Zero Rule.
"""

from pathlib import Path
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import accuracy_score, f1_score, classification_report

from ml_pipeline.data import FEATURE_COLUMNS, TARGET_COLUMN, load_gold_fact, split_time_based

PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "ml_pipeline" / "models"

def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carrega a fato Gold e cria os splits temporais para o treinamento."""
    return split_time_based(load_gold_fact())

def build_pipeline() -> Pipeline:
    """
    Constrói a arquitetura do modelo unindo pré-processamento e o algoritmo.
    Isso blinda a esteira contra Data Leakage.
    """
    cat_features = ["bairro_area_cross"]
    num_features = [column for column in FEATURE_COLUMNS if column not in cat_features]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore")),
                ]),
                cat_features,
            ),
            ("num", SimpleImputer(strategy="median"), num_features),
        ],
        remainder="drop",
    )

    # Algoritmo Base (Simples e interpretável)
    # n_estimators=100 (número de árvores), max_depth limita o overfitting
    rf_model = RandomForestClassifier(
        n_estimators=100, 
        max_depth=10, 
        class_weight="balanced", # Ajuda o modelo a prestar atenção nos Baratos e Caros
        random_state=42
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", rf_model)
    ])

def main():
    print("=" * 60)
    print("  Treinamento: Modelo Base (Random Forest)")
    print("=" * 60)

    # 1. Carregar Dados
    train_df, valid_df, _ = load_data()

    # Separar Features (X) e Target (y)
    X_train, y_train = train_df[FEATURE_COLUMNS], train_df[TARGET_COLUMN]
    X_valid, y_valid = valid_df[FEATURE_COLUMNS], valid_df[TARGET_COLUMN]

    # 2. Construir e Treinar o Pipeline
    print(f"Treinando em {len(X_train)} amostras...")
    model_pipeline = build_pipeline()
    model_pipeline.fit(X_train, y_train)

    # 3. Avaliar no conjunto de Validação
    y_pred_valid = model_pipeline.predict(X_valid)
    
    acc = accuracy_score(y_valid, y_pred_valid)
    f1 = f1_score(y_valid, y_pred_valid, average="macro")

    print(f"\n--- Resultados na Validação ---")
    print(f"Acurácia: {acc:.4f} (Baseline a bater: 0.5000)")
    print(f"F1-Score (Macro): {f1:.4f}")
    print("\nRelatório de Classificação:")
    print(classification_report(y_valid, y_pred_valid, zero_division=0))

    # 4. Salvar o Artefato do Modelo (Model Registry básico)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / "random_forest_v1.joblib"
    joblib.dump(model_pipeline, model_path)
    print(f"✅ Modelo salvo com sucesso em: {model_path}")

if __name__ == "__main__":
    main()