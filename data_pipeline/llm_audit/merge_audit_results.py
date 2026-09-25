"""Utilitário para fazer merge dos resultados de auditoria LLM na base de ML."""

import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def load_audit_results(audit_json_path: Path) -> pd.DataFrame:
    """
    Carrega resultados de auditoria do JSON e retorna um DataFrame.

    Args:
        audit_json_path: Caminho do arquivo JSON de auditoria.

    Returns:
        DataFrame com os resultados de auditoria.
    """
    with open(audit_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extrair apenas os registros de auditoria
    audit_records = data.get("auditoria", [])

    if not audit_records:
        logger.warning("Nenhum registro de auditoria encontrado")
        return pd.DataFrame()

    audit_df = pd.DataFrame(audit_records)

    # Normalizar novas_features (que é um sub-objeto)
    if "novas_features" in audit_df.columns:
        features_df = pd.json_normalize(audit_df["novas_features"])
        # Renomear para evitar conflitos
        features_df = features_df.rename(columns={
            col: f"feat_{col}" for col in features_df.columns
        })
        audit_df = pd.concat([audit_df, features_df], axis=1)
        audit_df = audit_df.drop(columns=["novas_features"])

    logger.info(f"✓ Carregado: {len(audit_df)} registros de auditoria")
    return audit_df


def merge_audit_with_silver(
    silver_parquet: Path,
    audit_json: Path,
    output_parquet: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Faz merge dos resultados de auditoria com os dados da Silver.

    Args:
        silver_parquet: Caminho do arquivo imoveis_limpos.parquet (Silver).
        audit_json: Caminho do arquivo de auditoria JSON.
        output_parquet: Opcional, salva resultado enriquecido neste arquivo.

    Returns:
        DataFrame enriquecido com features de auditoria.
    """
    # Carregar dados
    silver_df = pd.read_parquet(silver_parquet)
    audit_df = load_audit_results(audit_json)

    if audit_df.empty:
        logger.warning("Auditoria vazia, retornando Silver original")
        return silver_df

    # Merge via id_hex
    merged = silver_df.merge(
        audit_df[["id_hex", "veredicto", "area_m2_corrigida",
                   "vagas_corrigidas", "justificativa", "timestamp_auditoria",
                   "modelo_llm", "feat_mobiliado", "feat_reformado",
                   "feat_tem_lazer", "feat_ar_condicionado"]],
        on="id_hex",
        how="left",
        suffixes=("", "_auditoria")
    )

    logger.info(f"✓ Merge realizado: {len(merged)} registros")

    # Aplicar correções se veredicto == "CORRIGIR"
    corrigir_mask = merged["veredicto"] == "CORRIGIR"

    # Corrigir área se necessário
    if "area_m2_corrigida" in merged.columns:
        merged.loc[corrigir_mask & merged["area_m2_corrigida"].notna(), "area_m2"] = \
            merged.loc[corrigir_mask & merged["area_m2_corrigida"].notna(), "area_m2_corrigida"]

    # Corrigir vagas se necessário
    if "vagas_corrigidas" in merged.columns:
        merged.loc[corrigir_mask & merged["vagas_corrigidas"].notna(), "vagas"] = \
            merged.loc[corrigir_mask & merged["vagas_corrigidas"].notna(), "vagas_corrigidas"]

    # Renomear features para serem mais claras
    if "feat_mobiliado" in merged.columns:
        merged = merged.rename(columns={
            "feat_mobiliado": "llm_mobiliado",
            "feat_reformado": "llm_reformado",
            "feat_tem_lazer": "llm_tem_lazer",
            "feat_ar_condicionado": "llm_ar_condicionado",
        })

    # Salvar se especificado
    if output_parquet:
        output_parquet.parent.mkdir(parents=True, exist_ok=True)
        merged.to_parquet(output_parquet, index=False)
        logger.info(f"✓ Resultado enriquecido salvo em: {output_parquet}")

    return merged


def apply_audit_verdicts(
    merged_df: pd.DataFrame,
    output_file: Optional[Path] = None,
) -> tuple[pd.DataFrame, int, int]:
    """
    Aplica os veredictos da auditoria:
    - EXCLUIR: Remove da base
    - CORRIGIR: Já aplicado no merge
    - MANTER: Mantém como está

    Args:
        merged_df: DataFrame já mergeado com auditoria.
        output_file: Opcional, salva resultado final neste arquivo.

    Returns:
        (DataFrame final, count_excluidos, count_mantidos)
    """
    initial_count = len(merged_df)

    # Remover linhas com veredicto EXCLUIR
    excluir_count = (merged_df["veredicto"] == "EXCLUIR").sum()
    final_df = merged_df[merged_df["veredicto"] != "EXCLUIR"].copy()

    mantidos_count = (final_df["veredicto"] == "MANTER").sum()
    corrigidos_count = (final_df["veredicto"] == "CORRIGIR").sum()

    logger.info(f"\n📊 Aplicação de Veredictos:")
    logger.info(f"   - Inicial: {initial_count}")
    logger.info(f"   - Excluídos: {excluir_count}")
    logger.info(f"   - Mantidos (sem auditoria): {(final_df['veredicto'].isna()).sum()}")
    logger.info(f"   - Mantidos (com auditoria): {mantidos_count}")
    logger.info(f"   - Corrigidos: {corrigidos_count}")
    logger.info(f"   - Final: {len(final_df)}")

    # Salvar se especificado
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        final_df.to_parquet(output_file, index=False)
        logger.info(f"✓ Base final salva em: {output_file}")

    return final_df, excluir_count, mantidos_count


def full_pipeline(
    silver_parquet: Path,
    audit_json: Path,
    output_parquet: Optional[Path] = None,
) -> dict:
    """
    Pipeline completo: merge + aplicação de veredictos.

    Args:
        silver_parquet: Caminho do Silver.
        audit_json: Caminho do JSON de auditoria.
        output_parquet: Caminho para salvar resultado final.

    Returns:
        Dict com estatísticas da operação.
    """
    logger.info("=" * 70)
    logger.info("Iniciando merge de resultados de auditoria LLM")
    logger.info("=" * 70)

    # Merge
    merged_df = merge_audit_with_silver(silver_parquet, audit_json)

    # Aplicar veredictos
    final_df, excluidos, mantidos = apply_audit_verdicts(merged_df, output_parquet)

    return {
        "status": "success",
        "registros_processados": len(merged_df),
        "registros_excluidos": excluidos,
        "registros_mantidos": mantidos,
        "registros_finais": len(final_df),
        "arquivo_output": str(output_parquet) if output_parquet else None,
    }


if __name__ == "__main__":
    # Exemplo de uso
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 2:
        silver_path = Path(sys.argv[1])
        audit_path = Path(sys.argv[2])
        output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None

        resultado = full_pipeline(silver_path, audit_path, output_path)
        print(f"\n✅ Resultado: {json.dumps(resultado, indent=2)}")
    else:
        print("Uso: python merge_audit_results.py <silver.parquet> <audit.json> [output.parquet]")
