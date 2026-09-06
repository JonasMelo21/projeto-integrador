"""Transformação Silver → Gold

A camada Gold NÃO deve ser um único dataset genérico para tudo.
Na prática recomendada para este projeto, seguimos uma abordagem orientada a
modelo dimensional:

- Silver: armazena as dimensões (bairro, imobiliária)
- Gold: armazena a tabela fato e agregados estatísticos por bairro
- O split train/valid/test é decisão do treinamento/modelo e não da camada Gold

A camada Gold deve conter a tabela fato e dimensões derivadas/estatísticas, mas
não um dataset único "imoveis_gold" misturando tudo.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
SILVER_DIR = PROJECT_ROOT / "data" / "silver"
GOLD_DIR = PROJECT_ROOT / "data" / "gold"
SILVER_FILE = SILVER_DIR / "imoveis_limpos.parquet"

HASH_BUCKETS = 1024


def load_silver() -> pd.DataFrame:
    """Carrega os dados da camada Silver."""
    if not SILVER_FILE.exists():
        raise FileNotFoundError(f"Arquivo Silver não encontrado: {SILVER_FILE}")

    df = pd.read_parquet(SILVER_FILE)
    print(f"📂 Dados Silver carregados: {len(df)} registros.")
    return df


def deduplicate_defensive(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicatas por id_hex, mantendo a linha mais recente."""
    if "id_hex" not in df.columns:
        print("⚠ Coluna 'id_hex' não encontrada — pulando desduplicação.")
        return df

    sort_col = "ingestion_datetime" if "ingestion_datetime" in df.columns else "data_extracao"
    df_sorted = df.sort_values(by=sort_col, ascending=False)
    df_dedup = df_sorted.drop_duplicates(subset=["id_hex"], keep="first")

    removed = len(df) - len(df_dedup)
    if removed > 0:
        print(f"🛡️ Desduplicação: {removed} registros duplicados removidos.")
    else:
        print("🛡️ Desduplicação: Nenhuma duplicata encontrada.")

    return df_dedup.reset_index(drop=True)


def time_based_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Helper para o pipeline de treinamento. Não grava splits na camada Gold."""
    df_sorted = df.sort_values("data_extracao").reset_index(drop=True)

    n = len(df_sorted)
    train_end = int(n * 0.70)
    valid_end = int(n * 0.85)

    train_df = df_sorted.iloc[:train_end].copy()
    valid_df = df_sorted.iloc[train_end:valid_end].copy()
    test_df = df_sorted.iloc[valid_end:].copy()

    print("⏱️ Time-based Split calculado para downstream de treinamento.")
    print(f"   - Treino: {len(train_df)}")
    print(f"   - Validação: {len(valid_df)}")
    print(f"   - Teste: {len(test_df)}")

    return train_df, valid_df, test_df


def hash_categorical(value: str, buckets: int) -> int:
    """Hashing determinístico para variáveis categóricas dinâmicas."""
    text = str(value).strip().lower()
    return int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % buckets


def build_dim_imobiliarias(df: pd.DataFrame) -> pd.DataFrame:
    """Cria a dimensão de imobiliárias."""
    dim = (
        df[["imobiliaria"]]
        .dropna()
        .drop_duplicates()
        .rename(columns={"imobiliaria": "nome_imobiliaria"})
        .reset_index(drop=True)
    )
    dim.insert(0, "id_imobiliaria", range(1, len(dim) + 1))
    return dim


def build_dim_bairros(df: pd.DataFrame) -> pd.DataFrame:
    """Cria a dimensão de bairros."""
    dim = (
        df[["bairro"]]
        .dropna()
        .drop_duplicates()
        .rename(columns={"bairro": "bairro"})
        .reset_index(drop=True)
    )
    dim.insert(0, "id_bairro", range(1, len(dim) + 1))
    dim["cidade"] = "Brasília"
    dim["uf"] = "DF"
    return dim


def build_dim_bairros_estatisticas(df: pd.DataFrame) -> pd.DataFrame:
    """Cria a dimensão de estatísticas por bairro."""
    def calc_mad(x: pd.Series) -> float:
        return (x - x.median()).abs().median()

    stats = (
        df.groupby("bairro", dropna=False)
        .agg(
            preco_mediano_por_m2=("preco_por_m2", "median"),
            preco_mad=("preco_por_m2", calc_mad),
            area_mediana_m2=("area_m2", "median"),
            area_mad=("area_m2", calc_mad),
        )
        .reset_index()
    )

    stats["preco_mad"] = stats["preco_mad"].replace(0, 1.0)
    stats["area_mad"] = stats["area_mad"].replace(0, 1.0)

    dim_bairros = build_dim_bairros(df)
    stats = stats.merge(dim_bairros[["id_bairro", "bairro"]], on="bairro", how="left")
    stats = stats[[
        "id_bairro",
        "bairro",
        "preco_mediano_por_m2",
        "preco_mad",
        "area_mediana_m2",
        "area_mad",
    ]]
    return stats


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cria atributos de negócio e ML sem serializar um dataset único em Gold."""
    df = df.copy()
    df["imobiliaria_hash"] = df["imobiliaria"].apply(lambda x: hash_categorical(x, HASH_BUCKETS))

    def calc_mad(x: pd.Series) -> float:
        return (x - x.median()).abs().median()

    bairro_stats = df.groupby("bairro", dropna=False).agg(
        preco_med=("preco_por_m2", "median"),
        preco_mad=("preco_por_m2", calc_mad),
        area_med=("area_m2", "median"),
        area_mad=("area_m2", calc_mad),
    ).reset_index()

    bairro_stats["preco_mad"] = bairro_stats["preco_mad"].replace(0, 1.0)
    bairro_stats["area_mad"] = bairro_stats["area_mad"].replace(0, 1.0)

    merged = df.merge(bairro_stats, on="bairro", how="left")

    global_preco_med = merged["preco_por_m2"].median()
    global_preco_mad = calc_mad(merged["preco_por_m2"]) or 1.0
    global_area_med = merged["area_m2"].median()
    global_area_mad = calc_mad(merged["area_m2"]) or 1.0

    merged["preco_med"] = merged["preco_med"].fillna(global_preco_med)
    merged["preco_mad"] = merged["preco_mad"].fillna(global_preco_mad)
    merged["area_med"] = merged["area_med"].fillna(global_area_med)
    merged["area_mad"] = merged["area_mad"].fillna(global_area_mad)

    cond_preco = [
        merged["preco_por_m2"] < (merged["preco_med"] - merged["preco_mad"]),
        merged["preco_por_m2"] > (merged["preco_med"] + merged["preco_mad"]),
    ]
    merged["target_preco"] = np.select(cond_preco, [0, 2], default=1)

    cond_area = [
        merged["area_m2"] < (merged["area_med"] - merged["area_mad"]),
        merged["area_m2"] > (merged["area_med"] + merged["area_mad"]),
    ]
    merged["area_cat"] = np.select(cond_area, ["Compacto", "Amplo"], default="Padrao")
    merged["bairro_area_cross"] = merged["bairro"].astype(str) + "_" + merged["area_cat"].astype(str)

    print("✓ Feature engineering aplicada sobre a base Gold antes do split final.")
    return merged


def save_dimensions(dim_imobiliarias: pd.DataFrame, dim_bairros: pd.DataFrame, dim_bairros_stats: pd.DataFrame) -> None:
    """Salva as dimensões na camada Silver."""
    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    dim_imobiliarias.to_parquet(SILVER_DIR / "dim_imobiliarias.parquet", index=False)
    dim_bairros.to_parquet(SILVER_DIR / "dim_bairros.parquet", index=False)

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    dim_bairros_stats.to_parquet(GOLD_DIR / "dim_bairros_estatisticas.parquet", index=False)

    print("✅ Dimensões salvas:")
    print(f"   - {SILVER_DIR / 'dim_imobiliarias.parquet'}")
    print(f"   - {SILVER_DIR / 'dim_bairros.parquet'}")
    print(f"   - {GOLD_DIR / 'dim_bairros_estatisticas.parquet'}")


def build_fact_imoveis_gold(df: pd.DataFrame) -> pd.DataFrame:
    """Cria a tabela fato da camada Gold, preservando atributos do imóvel."""
    dim_imobiliarias = build_dim_imobiliarias(df)
    dim_bairros = build_dim_bairros(df)

    fact = df.copy()
    fact = fact.merge(dim_imobiliarias[["id_imobiliaria", "nome_imobiliaria"]], left_on="imobiliaria", right_on="nome_imobiliaria", how="left")
    fact = fact.merge(dim_bairros[["id_bairro", "bairro"]], on="bairro", how="left")

    fact = fact.rename(columns={
        "id_hex": "id_imovel",
        "id_imobiliaria": "id_imobiliaria_fk",
        "id_bairro": "id_bairro_fk",
    })

    fact["id_imovel"] = fact["id_imovel"].astype(str)
    fact["id_imobiliaria_fk"] = fact["id_imobiliaria_fk"].astype("Int64")
    fact["id_bairro_fk"] = fact["id_bairro_fk"].astype("Int64")
    fact["preco"] = pd.to_numeric(fact["preco"], errors="coerce").astype("float64")
    fact["area_m2"] = pd.to_numeric(fact["area_m2"], errors="coerce").astype("float64")
    for col in ["quartos", "suites", "banheiros", "vagas"]:
        if col in fact.columns:
            fact[col] = pd.to_numeric(fact[col], errors="coerce").astype("Int64")

    # Mantém a URL do imóvel no fato Gold para facilitar debug e validação.
    columns_order = [
        "id_imovel",
        "id_imobiliaria_fk",
        "id_bairro_fk",
        "titulo",
        "url",
        "bairro",
        "cidade",
        "uf",
        "preco",
        "area_m2",
        "quartos",
        "suites",
        "banheiros",
        "vagas",
        "preco_por_m2",
        "imobiliaria",
        "imobiliaria_hash",
        "preco_med",
        "preco_mad",
        "area_med",
        "area_mad",
        "target_preco",
        "area_cat",
        "bairro_area_cross",
        "data_extracao",
    ]

    for col in columns_order:
        if col not in fact.columns:
            fact[col] = pd.NA

    fact = fact[columns_order]
    return fact


def save_fact_gold(fact_df: pd.DataFrame) -> None:
    """Salva a tabela fato da Gold."""
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GOLD_DIR / "fact_imoveis_gold.parquet"
    fact_df.to_parquet(output_path, index=False)

    print(f"✅ Fato Gold salvo em: {output_path}")
    print(f"   Registros: {len(fact_df)} | Colunas: {len(fact_df.columns)}")


def main() -> None:
    print("=" * 70)
    print("  Silver → Gold: Dimensões + Tabela Fato")
    print("=" * 70)

    df = load_silver()
    df = deduplicate_defensive(df)
    df = engineer_features(df)

    dim_imobiliarias = build_dim_imobiliarias(df)
    dim_bairros = build_dim_bairros(df)
    dim_bairros_stats = build_dim_bairros_estatisticas(df)

    save_dimensions(dim_imobiliarias, dim_bairros, dim_bairros_stats)

    fact_df = build_fact_imoveis_gold(df)
    save_fact_gold(fact_df)


if __name__ == "__main__":
    main()