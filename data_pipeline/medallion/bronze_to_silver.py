"""Transformação Bronze → Silver

Lê todos os arquivos JSON da camada Bronze, desduplicata pelo id_imovel
mais recente, aplica limpeza/feature engineering e salva como Parquet na Silver.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).parent
BRONZE_DIR = SCRIPT_DIR.parent.parent / "data" / "bronze"
SILVER_DIR = SCRIPT_DIR.parent.parent / "data" / "silver"
SILVER_FILE = SILVER_DIR / "imoveis_limpos.parquet"

COLS_DROP = ["url", "imagem", "imagens", "id_hex"]


def load_bronze() -> pd.DataFrame:
    """Lê todos os JSON da Bronze e retorna um DataFrame concatenado."""
    json_files = list(BRONZE_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"Nenhum arquivo JSON encontrado em: {BRONZE_DIR}")

    print(f"📂 {len(json_files)} arquivo(s) encontrado(s) em bronze:")
    for f in sorted(json_files):
        print(f"   - {f.name}")

    frames = []
    for filepath in json_files:
        df = pd.read_json(filepath, encoding="utf-8")
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    print(f"\n✓ Total bruto após concat: {len(combined)} registros")
    return combined


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Mantém apenas o registro mais recente por id_imovel."""
    if "id_imovel" not in df.columns:
        print("⚠ Coluna 'id_imovel' não encontrada — pulando desduplicação")
        return df

    df["data_extracao"] = pd.to_datetime(df["data_extracao"], errors="coerce")
    df_sorted = df.sort_values("data_extracao", ascending=False)
    df_dedup = df_sorted.drop_duplicates(subset=["id_imovel"], keep="first")
    removed = len(df) - len(df_dedup)
    print(f"✓ Desduplicação: {removed} duplicatas removidas → {len(df_dedup)} registros únicos")
    return df_dedup.reset_index(drop=True)


def parse_preco(series: pd.Series) -> pd.Series:
    """Remove 'R$', pontos e espaços; converte para float."""
    return (
        series.astype(str)
        .str.replace(r"R\$", "", regex=True)
        .str.replace(r"\.", "", regex=True)
        .str.replace(",", ".", regex=False)
        .str.strip()
        .pipe(pd.to_numeric, errors="coerce")
    )


def parse_area(series: pd.Series) -> pd.Series:
    """Extrai número de strings como '560 m²'; converte para float."""
    return (
        series.astype(str)
        .str.extract(r"([\d.,]+)", expand=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )


def parse_inteiro(series: pd.Series) -> pd.Series:
    """Extrai o primeiro inteiro de strings como '4 Quartos' ou 'Sem vaga' → 0."""
    def _extract(val: str) -> float:
        match = re.search(r"\d+", str(val))
        return float(match.group()) if match else 0.0

    return series.apply(_extract)


def clean_text(series: pd.Series) -> pd.Series:
    """Remove \\n, \\t e espaços duplos de colunas de texto."""
    return (
        series.astype(str)
        .str.replace(r"[\n\t\r]+", " ", regex=True)
        .str.replace(r" {2,}", " ", regex=True)
        .str.strip()
    )


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica toda a limpeza e feature engineering."""
    # Descartar colunas desnecessárias
    cols_to_drop = [c for c in COLS_DROP if c in df.columns]
    df = df.drop(columns=cols_to_drop)
    print(f"✓ Colunas descartadas: {cols_to_drop}")

    # Preço
    if "preco" in df.columns:
        df["preco"] = parse_preco(df["preco"])

    # Área
    if "area" in df.columns:
        df["area_m2"] = parse_area(df["area"])
        df = df.drop(columns=["area"])

    # Numéricos
    for col in ["quartos", "suites", "vagas"]:
        if col in df.columns:
            df[col] = parse_inteiro(df[col])

    # Textos
    for col in ["titulo", "descricao"]:
        if col in df.columns:
            df[col] = clean_text(df[col])

    print(f"✓ Transformações aplicadas. Colunas finais: {list(df.columns)}")
    return df


def save_silver(df: pd.DataFrame) -> None:
    """Salva o DataFrame como Parquet na camada Silver."""
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(SILVER_FILE, index=False, engine="pyarrow")
    print(f"\n✓ Silver salva em: {SILVER_FILE}")
    print(f"   Registros: {len(df)} | Colunas: {len(df.columns)}")


def main() -> None:
    print("=" * 60)
    print("  Bronze → Silver ETL")
    print("=" * 60)

    df = load_bronze()
    df = deduplicate(df)
    df = transform(df)
    save_silver(df)

    print("\n📊 Amostra:")
    print(df[["id_imovel", "titulo", "preco", "area_m2", "quartos", "bairro"]].head(5).to_string(index=False))
    print("\n✅ Pipeline Bronze → Silver concluído!")


if __name__ == "__main__":
    main()
