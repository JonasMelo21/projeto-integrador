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

# Mantém a URL e imagem do imóvel na Silver para debug e rastreio posterior.
COLS_DROP = ["imagens", "id_imovel", "banheiros"]

TIPO_PATTERNS = [
    ("apartamento", r"\b(apartamento|apto|kitnet|flat)\b"),
    ("galpao", r"\b(galpao|galp[aã]o|barracao|barrac[aã]o)\b"),
    ("lote", r"\b(lote|terreno)\b"),
    ("sala", r"\b(sala|conjunto comercial|consultorio|escritorio)\b"),
    ("casa", r"\b(casa|sobrado|chacara|ch[aá]cara)\b"),
]
RESIDENTIAL_TYPES = {"apartamento", "casa", "sala", "outro"}


def normalize_for_matching(value: object) -> str:
    """Normaliza texto para as regras de classificacao sem acentos."""
    text = str(value or "").lower()
    replacements = str.maketrans({"á": "a", "ã": "a", "â": "a", "é": "e", "ê": "e", "í": "i", "ó": "o", "ô": "o", "õ": "o", "ú": "u", "ç": "c"})
    return re.sub(r"\s+", " ", text.translate(replacements)).strip()


def extract_tipo_imovel(url: object, titulo: object) -> str:
    """Extrai o tipo do imovel da URL e do titulo, com fallback auditavel."""
    text = normalize_for_matching(f"{url or ''} {titulo or ''}")
    for tipo, pattern in TIPO_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return tipo
    return "outro"


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
    """Converte numeros brasileiros sem confundir milhar e decimal."""
    return series.map(parse_number).astype(float)


def parse_area(series: pd.Series) -> pd.Series:
    """Extrai e converte areas como '560 m2', '1.234 m2' ou '1,5 m2'."""
    return series.map(lambda value: parse_number(re.search(r"[\d.,]+", str(value or "")).group() if re.search(r"[\d.,]+", str(value or "")) else None)).astype(float)


def parse_number(value: object) -> float | None:
    text = str(value or "").replace("R$", "").replace(" ", "").strip()
    if not text or text.lower() in {"n/a", "nan", "none"}:
        return None
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    elif text.count(".") == 1 and len(text.rsplit(".", 1)[1]) == 3:
        text = text.replace(".", "")
    try:
        return float(text)
    except ValueError:
        return None


def parse_inteiro(series: pd.Series) -> pd.Series:
    """Extrai o primeiro inteiro de strings como '4 Quartos'; retorna nulo se não houver informação explícita."""
    def _extract(val: str):
        if val is None:
            return pd.NA

        text = str(val).strip()
        if text in {"", "N/A", "nan", "None", "NaN"}:
            return pd.NA

        match = re.search(r"\d+", text)
        if not match:
            return pd.NA

        return int(match.group())

    return series.apply(_extract).astype("Int64")


def clean_text(series: pd.Series) -> pd.Series:
    """Remove \n, \t e espaços duplos de colunas de texto."""
    return (
        series.astype(str)
        .str.replace(r"[\n\t\r]+", " ", regex=True)
        .str.replace(r" {2,}", " ", regex=True)
        .str.strip()
    )


def apply_sanity_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Marca anomalias sem remover linhas da base principal."""
    df = df.copy()
    df["flag_suspeito"] = False
    reasons = pd.Series("", index=df.index, dtype="object")

    def add_reason(mask: pd.Series, reason: str) -> None:
        nonlocal reasons
        reasons = reasons.where(~mask, reasons.where(reasons.eq(""), reasons + "; ") + reason)
        df.loc[mask, "flag_suspeito"] = True

    add_reason(df["preco"].isna() | (df["preco"] <= 0), "preco ausente ou <= 0")
    add_reason(df["area_m2"].isna() | (df["area_m2"] <= 0), "area ausente ou <= 0")
    residential = df["tipo_imovel"].isin(RESIDENTIAL_TYPES)
    add_reason(residential & (df["area_m2"] < 10), "area residencial < 10 m2")
    add_reason(residential & (df["area_m2"] > 2000), "area residencial > 2000 m2")
    add_reason((df["tipo_imovel"].isin({"galpao", "lote"})) & (df["area_m2"] > 20000), "area nao residencial > 20000 m2")
    add_reason(df["vagas"].notna() & (df["vagas"] > 20), "vagas > 20")
    add_reason(df["preco"].notna() & ((df["preco"] < 100) | (df["preco"] > 200000)), "preco fora de [100, 200000]")

    df["motivo_suspeita"] = reasons
    return df


def impute_grouped_medians(df: pd.DataFrame) -> pd.DataFrame:
    """Preenche atributos numericos por bairro e tipo, com fallback global."""
    df = df.copy()
    group_columns = ["bairro", "tipo_imovel"]
    for column in ["quartos", "suites", "vagas"]:
        grouped = df.groupby(group_columns, dropna=False)[column].transform("median")
        fallback = df[column].median()
        values = df[column].astype("float64").fillna(grouped).fillna(fallback)
        df[column] = values.round().astype("Int64")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica toda a limpeza e feature engineering."""
    # Descartar colunas desnecessárias
    cols_to_drop = [c for c in COLS_DROP if c in df.columns]
    df = df.drop(columns=cols_to_drop)
    
    # Tratamentos básicos numéricos e de texto
    if "preco" in df.columns:
        df["preco"] = parse_preco(df["preco"]).astype(float)
    if "area" in df.columns:
        df["area_m2"] = parse_area(df["area"]).astype(float)
        df = df.drop(columns=["area"])
    for col in ["quartos", "suites", "vagas"]:
        if col in df.columns:
            df[col] = parse_inteiro(df[col])
    for col in ["titulo", "descricao", "descricao_completa"]:
        if col in df.columns:
            df[col] = clean_text(df[col])

    df["tipo_imovel"] = df.apply(
        lambda row: extract_tipo_imovel(row.get("url"), row.get("titulo")), axis=1
    )
    df = apply_sanity_flags(df)
    df = impute_grouped_medians(df)

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
        
    # Metadados do Pipeline
    df["ingestion_datetime"] = time.time() * 1000
    df["pipeline_version"] = "2.0"

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