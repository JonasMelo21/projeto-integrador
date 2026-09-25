"""Avaliação Offline do Modelo (Offline Evaluation)

Mede o desempenho final do modelo otimizado no conjunto de Teste (dados mais recentes).
Este script consolida as métricas que decidem se o modelo está pronto para ser
acoplado à API do backend.
"""

from pathlib import Path
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

from ml_pipeline.data import FEATURE_COLUMNS, TARGET_COLUMN, load_gold_splits

# Caminhos
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = PROJECT_ROOT / "ml_pipeline" / "models" / "random_forest_optimized.joblib"

def main():
    print("=" * 60)
    print("  Avaliação Offline: Teste no Mundo Real (Unseen Data)")
    print("=" * 60)

    # 1. Carregar os dados que o modelo nunca viu (Split de Teste)
    if not MODEL_PATH.exists():
        print("❌ Erro: Conjunto de teste ou modelo otimizado não encontrados.")
        return

    _, _, test_df = load_gold_splits()
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    # 2. Carregar o melhor artefato gerado pelo AutoML
    print(f"Carregando modelo: {MODEL_PATH.name}")
    model = joblib.load(MODEL_PATH)

    # 3. Fazer predições
    print(f"Avaliando {len(X_test)} imóveis recentes...")
    y_pred = model.predict(X_test)

    # 4. Calcular Métricas Finais
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")

    print("\n" + "-"*40)
    print(" 🏆 MÉTRICAS FINAIS DE PRODUÇÃO ")
    print("-" * 40)
    print(f"Acurácia Global: {acc:.4f} (Baseline Original: 0.5000)")
    print(f"F1-Score (Macro): {f1:.4f}")
    print("\nRelatório de Classificação Detalhado:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Bônus: Uma representação simples da Matriz de Confusão para análise de erros
    cm = confusion_matrix(y_test, y_pred)
    print("\nMatriz de Confusão (Linhas=Real, Colunas=Previsto):")
    print("          [Barato] [Justo] [Caro]")
    print(f"[Barato]  {cm[0][0]:<8} {cm[0][1]:<7} {cm[0][2]}")
    print(f"[Justo]   {cm[1][0]:<8} {cm[1][1]:<7} {cm[1][2]}")
    print(f"[Caro]    {cm[2][0]:<8} {cm[2][1]:<7} {cm[2][2]}")
    
    print("\n✅ Avaliação offline concluída. Se os números estiverem consistentes com o CV, o modelo está pronto para servir na API!")

if __name__ == "__main__":
    main()