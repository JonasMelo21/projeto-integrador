"""Carrega dados da camada Gold para a tabela imoveis_classificados no Supabase.

Este script:
1. Lê fact_imoveis_gold.parquet da camada Gold
2. Mapeia as colunas para o schema do Supabase
3. Converte target_preco (0, 1, 2) em ml_label ('Barato', 'Justo', 'Caro')
4. Faz upsert em lotes para não sobrecarregar a API
5. Registra progresso com logs detalhados
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv

try:
    from supabase import create_client
except ImportError:
    print("❌ Biblioteca 'supabase' não instalada. Execute:")
    print("   uv add supabase")
    sys.exit(1)

# Carregar variáveis de ambiente do .env
load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent
GOLD_DIR = PROJECT_ROOT / "data" / "gold"
GOLD_FILE = GOLD_DIR / "fact_imoveis_gold.parquet"

# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Target e classes do ML
TARGET_TO_LABEL = {
    0: "Barato",
    1: "Justo",
    2: "Caro",
}

BATCH_SIZE = 100


def validate_env() -> None:
    """Valida as variáveis de ambiente necessárias."""
    if not SUPABASE_URL:
        raise ValueError(
            "❌ Variável de ambiente SUPABASE_URL não está definida.\n"
            "Adicione ao seu .env:\n"
            "   SUPABASE_URL=https://seu-projeto.supabase.co"
        )
    if not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError(
            "❌ Variável de ambiente SUPABASE_SERVICE_ROLE_KEY não está definida.\n"
            "Adicione ao seu .env (obtém da dashboard Supabase → Settings → API):\n"
            "   SUPABASE_SERVICE_ROLE_KEY=seu-service-role-key"
        )
    print("✅ Variáveis de ambiente validadas.")


def load_gold_data() -> pd.DataFrame:
    """Carrega os dados da camada Gold."""
    if not GOLD_FILE.exists():
        raise FileNotFoundError(
            f"❌ Arquivo Gold não encontrado: {GOLD_FILE}\n"
            "Execute 'python -m data_pipeline.medallion.silver_to_gold' primeiro."
        )

    df = pd.read_parquet(GOLD_FILE)
    print(f"📂 Dados Gold carregados: {len(df)} registros, {len(df.columns)} colunas.")
    return df


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Mapeia as colunas do Gold para o schema do Supabase.

    Nota: Em silver_to_gold.py, id_hex foi renomeado para id_imovel.
    Portanto, id_imovel aqui é na verdade o id_hex original (chave primária única).
    """
    df = df.copy()

    # Renomear e selecionar apenas as colunas necessárias
    column_mapping = {
        "id_imovel": "id_hex",  # id_imovel é na verdade id_hex original (chave única)
        "titulo": "titulo",
        "url": "url",
        "preco": "preco",
        "bairro": "bairro",
        "quartos": "quartos",
        "vagas": "vagas",
        "area_m2": "area",
    }

    # Renomear colunas existentes
    df_mapped = df.rename(columns=column_mapping)

    # Manter id_imovel também (era id_imovel real extraído da URL)
    # Tentar encontrar a coluna original se não foi renomeada
    if "id_imovel" not in df_mapped.columns and "id_imovel" in df.columns:
        df_mapped["id_imovel"] = df["id_imovel"]

    # Selecionar colunas do Supabase
    required_cols = [
        "id_hex",
        "id_imovel",
        "titulo",
        "url",
        "preco",
        "bairro",
        "quartos",
        "vagas",
        "area",
        "target_preco",
    ]

    for col in required_cols:
        if col not in df_mapped.columns and col not in ["target_preco"]:
            df_mapped[col] = None

    print("✅ Colunas mapeadas com sucesso.")
    return df_mapped


def add_ml_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Converte target_preco em ml_label."""
    df = df.copy()

    if "target_preco" not in df.columns:
        print("⚠️  Coluna 'target_preco' não encontrada. Usando classificação padrão.")
        df["ml_label"] = "Justo"
    else:
        df["ml_label"] = df["target_preco"].map(TARGET_TO_LABEL).fillna("Justo")
        label_counts = df["ml_label"].value_counts()
        print(f"📊 Distribuição de ml_labels:")
        for label, count in label_counts.items():
            print(f"   - {label}: {count}")

    return df


def prepare_for_supabase(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara o DataFrame para inserção no Supabase."""
    df = df.copy()

    # Colunas que a tabela Supabase espera
    supabase_columns = [
        "id_hex",
        "id_imovel",
        "titulo",
        "url",
        "preco",
        "bairro",
        "quartos",
        "vagas",
        "area",
        "imagem",
        "ml_label",
    ]

    # Adicionar coluna imagem se não existir (será NULL)
    if "imagem" not in df.columns:
        df["imagem"] = None

    # Selecionar apenas as colunas necessárias
    df = df[supabase_columns]

    # Tratar tipos de dados
    df["id_hex"] = df["id_hex"].astype(str)
    df["id_imovel"] = df["id_imovel"].astype(str)
    df["preco"] = pd.to_numeric(df["preco"], errors="coerce")
    df["quartos"] = pd.to_numeric(df["quartos"], errors="coerce").astype("Int64")
    df["vagas"] = pd.to_numeric(df["vagas"], errors="coerce").astype("Int64")
    df["area"] = pd.to_numeric(df["area"], errors="coerce")

    # Preencher NULLs obrigatórios
    df["url"] = df["url"].fillna("unknown")
    df["preco"] = df["preco"].fillna(0.0)
    df["ml_label"] = df["ml_label"].fillna("Justo")

    # Converter NaN residuais para None (NULL em SQL)
    # Isso é necessário pois pandas pode ter float NaN que não é JSON-compliant
    for col in df.columns:
        if df[col].dtype == "float64":
            df[col] = df[col].apply(lambda x: None if pd.isna(x) else x)

    # Remover linhas com id_hex ou url inválidos (obrigatórios)
    df = df.dropna(subset=["id_hex", "url"])

    # Remove duplicatas por id_hex (mantém o primeiro)
    # Nota: O Gold já deve estar desduplicado, mas aplicamos como precaução
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["id_hex"], keep="first")
    after_dedup = len(df)
    if before_dedup > after_dedup:
        removed = before_dedup - after_dedup
        print(f"🛡️  Desduplicação: {removed} registros com id_hex duplicado removidos.")
    else:
        print(f"✅ Desduplicação: Nenhuma duplicata encontrada.")

    print(f"✅ Dados preparados: {len(df)} registros prontos para upsert.")
    return df


def upsert_batches(client: Any, df: pd.DataFrame, batch_size: int = BATCH_SIZE) -> int:
    """Faz upsert em lotes para não sobrecarregar a API."""
    total_records = 0
    total_batches = (len(df) + batch_size - 1) // batch_size

    for batch_idx in range(total_batches):
        start_idx = batch_idx * batch_size
        end_idx = min((batch_idx + 1) * batch_size, len(df))
        batch_df = df.iloc[start_idx:end_idx].copy()

        # Converter para dicionários para inserção
        # Substitui NaN/NaT por None (NULL) para compatibilidade com JSON
        batch_df = batch_df.where(pd.notna(batch_df), None)
        records = batch_df.to_dict(orient="records")

        # Sanitizar valores NaN residuais (float NaN não é JSON-compliant)
        for record in records:
            for key, value in record.items():
                if isinstance(value, float) and (value != value):  # NaN check
                    record[key] = None

        try:
            response = client.table("imoveis_classificados").upsert(records).execute()
            total_records += len(records)
            batch_num = batch_idx + 1
            print(
                f"✅ Batch {batch_num}/{total_batches}: "
                f"{len(records)} registros upsertados "
                f"(Total: {total_records})"
            )
        except Exception as e:
            print(f"❌ Erro ao fazer upsert do batch {batch_idx + 1}: {str(e)}")
            raise

    return total_records


def delete_all_properties(client: Any) -> int:
    """Deleta todos os registros da tabela imoveis_classificados."""
    try:
        print("🗑️  Deletando registros anteriores...")
        response = client.table("imoveis_classificados").delete().neq("id_hex", "").execute()
        print(f"✅ Registros deletados com sucesso.")
        return 1
    except Exception as e:
        print(f"⚠️  Erro ao deletar registros: {str(e)}")
        raise


def verify_data(client: Any) -> None:
    """Verifica os dados inseridos no Supabase."""
    try:
        # Contar registros
        response = client.table("imoveis_classificados").select("id_hex", count="exact").execute()
        total_count = response.count if hasattr(response, 'count') else len(response.data)
        print(f"✅ Verificação: Total de registros na tabela: {total_count}")

        # Amostra dos dados
        sample = client.table("imoveis_classificados").select("*").limit(3).execute()
        if sample.data:
            print("📋 Amostra dos primeiros 3 registros:")
            for record in sample.data:
                print(f"   - {record.get('id_hex')}: {record.get('titulo')} ({record.get('ml_label')})")
    except Exception as e:
        print(f"⚠️  Não foi possível verificar os dados: {str(e)}")


def main() -> None:
    """Função principal."""
    print("=" * 70)
    print("  Gold → Supabase: Carregando imoveis_classificados")
    print("=" * 70)

    # Validar ambiente
    validate_env()

    # Carregar dados
    df = load_gold_data()

    # Mapear colunas
    df = map_columns(df)

    # Adicionar labels de ML
    df = add_ml_labels(df)

    # Preparar para Supabase
    df = prepare_for_supabase(df)

    # Conectar ao Supabase
    print(f"\n🔌 Conectando ao Supabase...")
    try:
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("✅ Conexão estabelecida.")
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {str(e)}")
        sys.exit(1)

    # Deletar registros anteriores
    print(f"\n🗑️  Limpando dados anteriores...")
    delete_all_properties(client)

    # Fazer upsert
    print(f"\n📤 Iniciando upsert em lotes de {BATCH_SIZE} registros...\n")
    total_upserted = upsert_batches(client, df)

    # Verificar dados
    print(f"\n🔍 Verificando dados inseridos...")
    verify_data(client)

    print("\n" + "=" * 70)
    print(f"✨ Sucesso! {total_upserted} registros carregados para o Supabase.")
    print("=" * 70)


if __name__ == "__main__":
    main()
