"""Phase 3: Optimizing Simple Models (Soft AutoML)

Busca sistemática de hiperparâmetros para o Random Forest usando RandomizedSearchCV.
O objetivo é melhorar a Precision da classe 2 (Caros) e estabilizar o modelo,
afastando-se do ajuste manual (Graduate Student Descent).
"""

from pathlib import Path
import pandas as pd
import joblib
import json
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import classification_report

from ml_pipeline.data import FEATURE_COLUMNS, TARGET_COLUMN, load_gold_splits

# Caminhos
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "ml_pipeline" / "models"

def load_train_data() -> tuple[pd.DataFrame, pd.Series]:
    """Para tuning com validação cruzada (CV), juntamos Treino e Validação."""
    train_df, valid_df, _ = load_gold_splits()
    full_train = pd.concat([train_df, valid_df], ignore_index=True)
    full_train = full_train.loc[~full_train["flag_suspeito"].fillna(False)].copy()

    X = full_train[FEATURE_COLUMNS]
    y = full_train[TARGET_COLUMN]
    
    return X, y

def get_tuning_pipeline() -> Pipeline:
    cat_features = ["bairro_area_cross", "tipo_imovel"]
    num_features = [column for column in FEATURE_COLUMNS if column not in cat_features]
    
    preprocessor = ColumnTransformer(transformers=[
        (
            "cat",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ]),
            cat_features,
        ),
        ("num", SimpleImputer(strategy="median"), num_features),
    ])

    return Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(random_state=42))
    ])

def main():
    print("=" * 60)
    print("  Soft AutoML: Tuning de Hiperparâmetros (Random Forest)")
    print("=" * 60)

    X, y = load_train_data()
    pipeline = get_tuning_pipeline()

    # O Espaço de Busca (Search Space)
    param_distributions = {
        "classifier__n_estimators": [50, 100, 200, 300],
        "classifier__max_depth": [5, 10, 15, 20, None],
        "classifier__min_samples_split": [2, 5, 10],
        "classifier__min_samples_leaf": [1, 2, 4],
        "classifier__class_weight": ["balanced", "balanced_subsample", None]
    }

    # Configuração do Experimento
    print(f"Iniciando busca em {len(X)} amostras com Cross-Validation (cv=3)...")
    search = RandomizedSearchCV(
        pipeline,
        param_distributions=param_distributions,
        n_iter=20,          # Testa 20 combinações aleatórias diferentes
        cv=3,               # K-Fold igual a 3
        scoring='f1_macro', # Otimiza o F1-Score Macro para equilibrar as 3 classes
        n_jobs=-1,          # Usa todos os núcleos da CPU
        random_state=42,
        verbose=1
    )

    # Executa a busca
    search.fit(X, y)

    # Resultados do Experimento
    print("\n✅ Busca Concluída!")
    print(f"Melhor F1-Score (CV): {search.best_score_:.4f}")
    print("Melhores Hiperparâmetros:")
    for param, value in search.best_params_.items():
        print(f"   - {param.replace('classifier__', '')}: {value}")

    # Salva o melhor modelo
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    best_model_path = MODELS_DIR / "random_forest_optimized.joblib"
    joblib.dump(search.best_estimator_, best_model_path)
    
    # Salva os metadados do experimento (Tracking básico)
    tracker_file = MODELS_DIR / "experiment_log.json"
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "model": "RandomForestClassifier",
        "best_cv_f1_macro": search.best_score_,
        "params": search.best_params_
    }
    
    with open(tracker_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"\nModelo otimizado salvo em: {best_model_path}")
    print(f"Log do experimento salvo em: {tracker_file}")

if __name__ == "__main__":
    main()