"""Transformação Silver → Gold

Prepara os dados para Machine Learning seguindo as boas práticas de ML Systems (Chip Huyen):
1. Desduplicação Defensiva (Garante integridade mesmo se a Silver falhar).
2. Time-based Split para evitar data leakage.
3. Target Discretization usando Mediana e MAD (Desvio Absoluto Mediano).
4. Area Discretization para Feature Crossing espacial não-linear.
5. Hashing Trick para variáveis categóricas dinâmicas (Imobiliárias).
"""

from __future__ import annotations

import hashlib
import numpy as np
import pandas as pd
from pathlib import Path

# Caminhos do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent
SILVER_FILE = PROJECT_ROOT / "data" / "silver" / "imoveis_limpos.parquet"
GOLD_DIR = PROJECT_ROOT / "data" / "gold"

# Quantidade de buckets para o Hashing Trick
HASH_BUCKETS = 1024


def load_silver() -> pd.DataFrame:
    """Carrega os dados limpos da camada Silver."""
    if not SILVER_FILE.exists():
        raise FileNotFoundError(f"Arquivo Silver não encontrado: {SILVER_FILE}")
    
    df = pd.read_parquet(SILVER_FILE)
    print(f"📂 Dados Silver carregados: {len(df)} registros brutos.")
    return df


def deduplicate_defensive(df: pd.DataFrame) -> pd.DataFrame:
    """
    Camada de proteção extra: garante que não haja ids duplicados na Gold.
    Mantém a versão mais recente baseada no ingestion_datetime ou data_extracao.
    """
    if "id_hex" not in df.columns:
        print("⚠ Coluna 'id_hex' não encontrada — pulando desduplicação")
        return df

    # Tenta usar a data de ingestão da pipeline, faz fallback pra extração
    sort_col = "ingestion_datetime" if "ingestion_datetime" in df.columns else "data_extracao"
    
    df_sorted = df.sort_values(by=sort_col, ascending=False)
    df_dedup = df_sorted.drop_duplicates(subset=["id_hex"], keep="first")
    
    removed = len(df) - len(df_dedup)
    if removed > 0:
        print(f"🛡️ Desduplicação Gold: {removed} duplicatas bloqueadas e removidas.")
    else:
        print("🛡️ Desduplicação Gold: Nenhuma duplicata encontrada. Dados íntegros.")
        
    return df_dedup.reset_index(drop=True)


def time_based_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Divide os dados pelo tempo (Time-based Split) para evitar vazamento futuro."""
    df_sorted = df.sort_values("data_extracao").reset_index(drop=True)
    
    n = len(df_sorted)
    train_end = int(n * 0.70)
    valid_end = int(n * 0.85)
    
    train_df = df_sorted.iloc[:train_end].copy()
    valid_df = df_sorted.iloc[train_end:valid_end].copy()
    test_df = df_sorted.iloc[valid_end:].copy()
    
    print(f"⏱️ Time-based Split:")
    print(f"   - Treino: {len(train_df)} registros")
    print(f"   - Validação: {len(valid_df)} registros")
    print(f"   - Teste: {len(test_df)} registros")
    
    return train_df, valid_df, test_df


def hash_categorical(val: str, buckets: int) -> int:
    """Hashing Trick determinístico via MD5 para contornar novas categorias no futuro."""
    val_str = str(val).strip().lower()
    return int(hashlib.md5(val_str.encode('utf-8')).hexdigest(), 16) % buckets


def engineer_features(
    train_df: pd.DataFrame, 
    valid_df: pd.DataFrame, 
    test_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Cria labels e features sem Data Leakage (Estatísticas extraídas SOMENTE do Treino)."""
    
    # 1. HASHING TRICK: Imobiliárias
    for df in [train_df, valid_df, test_df]:
        df['imobiliaria_hash'] = df['imobiliaria'].apply(lambda x: hash_categorical(x, HASH_BUCKETS))

    # 2. CALCULAR MEDIANA E MAD (Somente no Treino)
    def calc_mad(x):
        return (x - x.median()).abs().median()

    # Fallbacks globais (Caso apareça um bairro novo na Validação/Teste)
    global_preco_med = train_df['preco_por_m2'].median()
    global_preco_mad = calc_mad(train_df['preco_por_m2']) or 1.0
    global_area_med = train_df['area_m2'].median()
    global_area_mad = calc_mad(train_df['area_m2']) or 1.0

    # Estatísticas por bairro
    bairro_stats = train_df.groupby('bairro').agg(
        preco_med=('preco_por_m2', 'median'),
        preco_mad=('preco_por_m2', calc_mad),
        area_med=('area_m2', 'median'),
        area_mad=('area_m2', calc_mad)
    ).reset_index()

    # Prevenir MAD zerado (quando todos os imóveis de um bairro tem valor igual)
    bairro_stats['preco_mad'] = bairro_stats['preco_mad'].replace(0, 1.0)
    bairro_stats['area_mad'] = bairro_stats['area_mad'].replace(0, 1.0)

    # 3. APLICAR DISCRETIZAÇÃO E FEATURE CROSSING
    def apply_transformations(df: pd.DataFrame) -> pd.DataFrame:
        # Mesclar estatísticas do treino
        df_merged = df.merge(bairro_stats, on='bairro', how='left')
        
        # Preencher bairros não vistos no treino com estatísticas globais
        df_merged['preco_med'] = df_merged['preco_med'].fillna(global_preco_med)
        df_merged['preco_mad'] = df_merged['preco_mad'].fillna(global_preco_mad)
        df_merged['area_med'] = df_merged['area_med'].fillna(global_area_med)
        df_merged['area_mad'] = df_merged['area_mad'].fillna(global_area_mad)
        
        # Variável Target: 0 (Barato), 1 (Justo), 2 (Caro)
        cond_preco = [
            df_merged['preco_por_m2'] < (df_merged['preco_med'] - df_merged['preco_mad']),
            df_merged['preco_por_m2'] > (df_merged['preco_med'] + df_merged['preco_mad'])
        ]
        df_merged['target_preco'] = np.select(cond_preco, [0, 2], default=1)
        
        # Discretização da Área: Compacto, Padrão, Amplo
        cond_area = [
            df_merged['area_m2'] < (df_merged['area_med'] - df_merged['area_mad']),
            df_merged['area_m2'] > (df_merged['area_med'] + df_merged['area_mad'])
        ]
        df_merged['area_cat'] = np.select(cond_area, ['Compacto', 'Amplo'], default='Padrao')
        
        # Feature Crossing (Não Linear)
        df_merged['bairro_area_cross'] = df_merged['bairro'].astype(str) + '_' + df_merged['area_cat']
        
        return df_merged

    train_gold = apply_transformations(train_df)
    valid_gold = apply_transformations(valid_df)
    test_gold = apply_transformations(test_df)

    print("✓ Labeling (MAD) e Engenharia de Features concluídas.")
    return train_gold, valid_gold, test_gold


def save_gold(train_df: pd.DataFrame, valid_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
    """Salva os datasets finais em Parquet na camada Gold prontas para os modelos."""
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Selecionar as colunas que o modelo vai consumir de fato
    final_cols = [
        "id_hex", 
        "bairro_area_cross", 
        "imobiliaria_hash", 
        "quartos", 
        "suites", 
        "vagas",
        "target_preco" # Nossa Label Final
    ]
    
    # Salvar
    train_df[final_cols].to_parquet(GOLD_DIR / "train.parquet", index=False)
    valid_df[final_cols].to_parquet(GOLD_DIR / "valid.parquet", index=False)
    test_df[final_cols].to_parquet(GOLD_DIR / "test.parquet", index=False)
    
    print(f"✅ Camada Gold gerada com sucesso em: {GOLD_DIR}")


def main():
    print("=" * 60)
    print("  Silver → Gold ETL (ML Feature Engineering)")
    print("=" * 60)
    
    df = load_silver()
    df = deduplicate_defensive(df) # <-- Nova barreira contra duplicatas
    train_df, valid_df, test_df = time_based_split(df)
    train_df, valid_df, test_df = engineer_features(train_df, valid_df, test_df)
    save_gold(train_df, valid_df, test_df)


if __name__ == "__main__":
    main()