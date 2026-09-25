"""Baselines para Avaliação de Modelos de ML

Implementa estratégias simples (Zero Rule e Random) para estabelecer 
um piso de performance. Qualquer modelo de ML treinado futuramente 
DEVE superar as métricas geradas por este script.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report

from ml_pipeline.data import TARGET_COLUMN, load_gold_splits

# Caminhos
PROJECT_ROOT = Path(__file__).parent.parent
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carrega a fato Gold e retorna treino e teste temporais."""
    train_df, _, test_df = load_gold_splits()
    return train_df, test_df

def evaluate_predictions(y_true: pd.Series, y_pred: np.ndarray, model_name: str) -> None:
    """Calcula e imprime as métricas (Accuracy e F1) do baseline."""
    acc = accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average='macro')
    
    print(f"\n--- {model_name} ---")
    print(f"Acurácia: {acc:.4f}")
    print(f"F1-Score (Macro): {f1_macro:.4f}")
    print("Relatório de Classificação:")
    print(classification_report(y_true, y_pred, zero_division=0))

def zero_rule_baseline(y_train: pd.Series, y_test: pd.Series) -> None:
    """
    Zero Rule Baseline: Sempre prevê a classe majoritária do conjunto de treino.
    """
    # Encontra a classe mais frequente no treino
    majority_class = y_train.mode()[0]
    
    # Cria um array com essa mesma classe para todo o conjunto de teste
    y_pred = np.full(shape=y_test.shape, fill_value=majority_class)
    
    evaluate_predictions(y_test, y_pred, "Baseline: Zero Rule (Classe Majoritária)")

def random_uniform_baseline(y_test: pd.Series) -> None:
    """
    Random Baseline (Uniform): Prevê as classes aleatoriamente com a mesma probabilidade.
    """
    classes = [0, 1, 2] # 0: Barato, 1: Justo, 2: Caro
    # np.random.choice escolhe aleatoriamente com distribuição uniforme se 'p' não for passado
    y_pred = np.random.choice(classes, size=len(y_test))
    
    evaluate_predictions(y_test, y_pred, "Baseline: Random (Distribuição Uniforme)")

def random_stratified_baseline(y_train: pd.Series, y_test: pd.Series) -> None:
    """
    Random Baseline (Task's Label Distribution): Prevê as classes aleatoriamente, 
    mas respeitando a proporção/frequência delas no conjunto de treino.
    """
    # Calcula a probabilidade de cada classe no treino
    class_counts = y_train.value_counts(normalize=True).sort_index()
    classes = class_counts.index.values
    probabilities = class_counts.values
    
    # Chuta com base nessa probabilidade
    y_pred = np.random.choice(classes, size=len(y_test), p=probabilities)
    
    evaluate_predictions(y_test, y_pred, "Baseline: Random (Distribuição do Treino)")

def main():
    print("=" * 60)
    print("  Estabelecendo Baselines do SmartRent AI")
    print("=" * 60)
    
    train_df, test_df = load_data()
    
    y_train = train_df[TARGET_COLUMN]
    y_test = test_df[TARGET_COLUMN]
    
    # Executa os três baselines propostos pela Chip Huyen
    zero_rule_baseline(y_train, y_test)
    random_uniform_baseline(y_test)
    random_stratified_baseline(y_train, y_test)
    
    print("\n✅ Baselines estabelecidos. O modelo ML precisará bater essas métricas no teste!")

if __name__ == "__main__":
    # Fixar a semente aleatória para reprodutibilidade dos baselines randomizados
    np.random.seed(42)
    main()