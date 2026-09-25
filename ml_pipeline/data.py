"""Dados e contrato compartilhado do treinamento de modelos."""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
GOLD_PATH = PROJECT_ROOT / "data" / "gold" / "fact_imoveis_gold.parquet"
TARGET_COLUMN = "target_preco"
FEATURE_COLUMNS = [
    "bairro_area_cross",
    "tipo_imovel",
    "imobiliaria_hash",
    "area_m2",
    "quartos",
    "suites",
    "vagas",
]
GOLD_SPLIT_PATHS = {
    "train": PROJECT_ROOT / "data" / "gold" / "ml_train.parquet",
    "valid": PROJECT_ROOT / "data" / "gold" / "ml_valid.parquet",
    "test": PROJECT_ROOT / "data" / "gold" / "ml_test.parquet",
}


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


def load_gold_splits() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carrega splits Gold enriquecidos com estatisticas ajustadas no treino."""
    missing = [str(path) for path in GOLD_SPLIT_PATHS.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Splits ML ausentes. Execute Silver -> Gold antes do treinamento: "
            + ", ".join(missing)
        )

    splits = {
        name: pd.read_parquet(path)
        for name, path in GOLD_SPLIT_PATHS.items()
    }
    required = set(FEATURE_COLUMNS + [TARGET_COLUMN, "data_extracao", "flag_suspeito"])
    for name, split_df in splits.items():
        missing_columns = sorted(required.difference(split_df.columns))
        if missing_columns:
            raise ValueError(f"Colunas ausentes no split {name}: {missing_columns}")

    train_df = splits["train"].loc[~splits["train"]["flag_suspeito"].fillna(False)].copy()
    train_df = train_df.dropna(subset=[TARGET_COLUMN, "data_extracao"])
    valid_df = splits["valid"].dropna(subset=[TARGET_COLUMN, "data_extracao"]).copy()
    test_df = splits["test"].dropna(subset=[TARGET_COLUMN, "data_extracao"]).copy()
    if min(len(train_df), len(valid_df), len(test_df)) == 0:
        raise ValueError("Os splits Gold precisam conter registros treinaveis.")
    return train_df, valid_df, test_df


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