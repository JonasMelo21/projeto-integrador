"""Dados e contrato compartilhado do treinamento de modelos."""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
GOLD_PATH = PROJECT_ROOT / "data" / "gold" / "fact_imoveis_gold.parquet"
TARGET_COLUMN = "target_preco"
FEATURE_COLUMNS = [
    "bairro_area_cross",
    "imobiliaria_hash",
    "area_m2",
    "quartos",
    "suites",
    "banheiros",
    "vagas",
]


def load_gold_fact() -> pd.DataFrame:
    """Carrega a tabela fato Gold produzida pela arquitetura atual."""
    if not GOLD_PATH.exists():
        raise FileNotFoundError(
            f"Tabela fato Gold não encontrada: {GOLD_PATH}. "
            "Execute Bronze → Silver → Gold antes do treinamento."
        )

    df = pd.read_parquet(GOLD_PATH)
    required_columns = set(FEATURE_COLUMNS + [TARGET_COLUMN, "data_extracao"])
    missing_columns = sorted(required_columns.difference(df.columns))
    if missing_columns:
        raise ValueError(f"Colunas obrigatórias ausentes na Gold: {missing_columns}")

    df = df.dropna(subset=[TARGET_COLUMN, "data_extracao"]).copy()
    if df.empty:
        raise ValueError("A tabela fato Gold não possui registros treináveis.")

    return df


def split_time_based(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Divide a fato em treino, validação e teste respeitando a ordem temporal."""
    df_sorted = df.sort_values("data_extracao").reset_index(drop=True)
    train_end = int(len(df_sorted) * 0.70)
    valid_end = int(len(df_sorted) * 0.85)

    train_df = df_sorted.iloc[:train_end].copy()
    valid_df = df_sorted.iloc[train_end:valid_end].copy()
    test_df = df_sorted.iloc[valid_end:].copy()

    if min(len(train_df), len(valid_df), len(test_df)) == 0:
        raise ValueError("A tabela fato precisa de registros suficientes para os três splits.")

    return train_df, valid_df, test_df