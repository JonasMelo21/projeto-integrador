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
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import accuracy_score, f1_score, classification_report

# Configuração de Caminhos
PROJECT_ROOT = Path(__file__).parent.parent
GOLD_DIR = PROJECT_ROOT / "data" / "gold"
MODELS_DIR = PROJECT_ROOT / "ml_pipeline" / "models"

def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carrega as bases de Treino, Validação e Teste da camada Gold."""
    train_df = pd.read_parquet(GOLD_DIR / "train.parquet")
    valid_df = pd.read_parquet(GOLD_DIR / "valid.parquet")
    test_df = pd.read_parquet(GOLD_DIR / "test.parquet")
    return train_df, valid_df, test_df

def build_pipeline() -> Pipeline:
    """
    Constrói a arquitetura do modelo unindo pré-processamento e o algoritmo.
    Isso blinda a esteira contra Data Leakage.
    """
    # Features Categóricas e Numéricas
    cat_features = ["bairro_area_cross"]
    # imobiliaria_hash já é um inteiro, tratamos como numérica contínua/discreta
    num_features = ["imobiliaria_hash", "quartos", "suites", "vagas"]

    # Pré-processamento: OHE para categorias, passa direto os numéricos
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features)
        ],
        remainder="passthrough"
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
    train_df, valid_df, _ = load_data() # O teste fica guardado para o final da pipeline

    # Separar Features (X) e Target (y)
    features_cols = ["bairro_area_cross", "imobiliaria_hash", "quartos", "suites", "vagas"]
    X_train, y_train = train_df[features_cols], train_df["target_preco"]
    X_valid, y_valid = valid_df[features_cols], valid_df["target_preco"]

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