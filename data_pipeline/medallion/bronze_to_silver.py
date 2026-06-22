"""Transformação Bronze → Silver

Lê todos os arquivos JSON da camada Bronze, desduplicata pelo id_imovel
mais recente, aplica limpeza/feature engineering e salva como Parquet na Silver.
"""

from __future__ import annotations

import re
import time
from pathlib import Path

import pandas as pd

# 1. Caminhos atualizados para o contexto da raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"
SILVER_FILE = SILVER_DIR / "imoveis_limpos.parquet"

# 2. 'id_hex' removido da lista de descarte para ser mantido na Silver
COLS_DROP = ["url", "imagem", "imagens", "id_imovel"] 


def load_bronze() -> pd.DataFrame:
    """Lê todos os JSON da Bronze e retorna um DataFrame concatenado com o source_file."""
    json_files = list(BRONZE_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"Nenhum arquivo JSON encontrado em: {BRONZE_DIR}")

    print(f"📂 {len(json_files)} arquivo(s) encontrado(s) em bronze:")
    
    frames = []
    for filepath in sorted(json_files):
        print(f"   - {filepath.name}")
        df = pd.read_json(filepath, encoding="utf-8")
        # Registra a origem do dado (source_file)
        df["source_file"] = filepath.name
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    print(f"\n✓ Total bruto após concat: {len(combined)} registros")
    return combined


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Mantém apenas o registro mais recente por id_hex."""
    # Usando id_hex como chave primária de desduplicação conforme o novo schema
    if "id_hex" not in df.columns:
        print("⚠ Coluna 'id_hex' não encontrada — pulando desduplicação")
        return df

    df["data_extracao"] = pd.to_datetime(df["data_extracao"], errors="coerce")
    df_sorted = df.sort_values("data_extracao", ascending=False)
    df_dedup = df_sorted.drop_duplicates(subset=["id_hex"], keep="first")
    removed = len(df) - len(df_dedup)
    
    # Converte a data_extracao para timestamp float (como no seu exemplo JSON)
    df_dedup["data_extracao"] = df_dedup["data_extracao"].apply(lambda x: x.timestamp() * 1000 if pd.notnull(x) else None)
    
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
    """Remove \n, \t e espaços duplos de colunas de texto."""
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
    
    # Tratamentos básicos numéricos e de texto
    if "preco" in df.columns:
        df["preco"] = parse_preco(df["preco"])
    if "area" in df.columns:
        df["area_m2"] = parse_area(df["area"])
        df = df.drop(columns=["area"])
    for col in ["quartos", "suites", "vagas"]:
        if col in df.columns:
            df[col] = parse_inteiro(df[col])
    for col in ["titulo", "descricao"]:
        if col in df.columns:
            df[col] = clean_text(df[col])

    # 3. Engenharia de Features (Feature Engineering)
    
    # Preço por m²
    if "preco" in df.columns and "area_m2" in df.columns:
        df["preco_por_m2"] = df.apply(
            lambda x: round(x["preco"] / x["area_m2"], 2) if pd.notnull(x["area_m2"]) and x["area_m2"] > 0 else None,
            axis=1
        )
        
    # Comprimento de textos (para análise de NLP depois)
    if "titulo" in df.columns:
        df["titulo_len"] = df["titulo"].astype(str).apply(len)
    if "descricao" in df.columns:
        df["descricao_len"] = df["descricao"].astype(str).apply(len)
        
    # Campos Nulos Padrões
    if "banheiros" not in df.columns:
        df["banheiros"] = None
        
    # Metadados do Pipeline
    df["ingestion_datetime"] = time.time() * 1000
    df["pipeline_version"] = "1.0"

    print(f"✓ Transformações e features criadas. Colunas finais: {list(df.columns)}")
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
    print(df[["id_hex", "titulo", "preco", "area_m2", "preco_por_m2"]].head(5).to_string(index=False))
    print("\n✅ Pipeline Bronze → Silver concluído!")


if __name__ == "__main__":
    main()