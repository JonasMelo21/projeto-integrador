"""Carregamento e preparação de dados para auditoria LLM."""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def get_silver_path(project_root: Optional[Path] = None) -> Path:
    """Retorna o caminho do arquivo Silver (imoveis_limpos.parquet)."""
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    silver_file = project_root / "data" / "silver" / "imoveis_limpos.parquet"
    return silver_file


def load_silver_data(project_root: Optional[Path] = None) -> pd.DataFrame:
    """
    Carrega os dados da camada Silver.

    Args:
        project_root: Raiz do projeto (detecção automática se None).

    Returns:
        DataFrame com os dados de imóveis da Silver.

    Raises:
        FileNotFoundError: Se o arquivo Silver não existir.
    """
    silver_file = get_silver_path(project_root)

    if not silver_file.exists():
        raise FileNotFoundError(f"Arquivo Silver não encontrado: {silver_file}")

    df = pd.read_parquet(silver_file)
    logger.info(f"✓ Silver carregado: {len(df)} registros")

    return df


def validate_required_columns(df: pd.DataFrame) -> bool:
    """
    Valida se todas as colunas necessárias estão presentes.

    Args:
        df: DataFrame a validar.

    Returns:
        True se válido, False caso contrário.
    """
    required = {
        "id_hex",
        "descricao_completa",
        "tipo_imovel",
        "bairro",
        "preco",
        "area_m2",
        "vagas",
        "flag_suspeito",
        "motivo_suspeita",
    }

    missing = required - set(df.columns)
    if missing:
        logger.error(f"Colunas faltando no Silver: {missing}")
        return False

    logger.info(f"✓ Validação de colunas OK")
    return True


def prepare_audit_batch(
    df: pd.DataFrame,
    limit: Optional[int] = None,
    only_suspicious: bool = False,
) -> pd.DataFrame:
    """
    Prepara um batch de imóveis para auditoria.

    Args:
        df: DataFrame da Silver.
        limit: Limite de registros (None = todos).
        only_suspicious: Se True, filtra apenas flag_suspeito=True.

    Returns:
        DataFrame preparado para auditoria.
    """
    batch = df.copy()

    # Filtrar suspeitos se necessário
    if only_suspicious:
        batch = batch[batch["flag_suspeito"] == True].copy()
        logger.info(f"Filtrado apenas suspeitos: {len(batch)} registros")

    # Aplicar limite
    if limit:
        batch = batch.head(limit)
        logger.info(f"Aplicado limite de {limit} registros")

    # Garantir que descricao_completa não é nula
    batch = batch[batch["descricao_completa"].notna()].copy()
    logger.info(f"Filtrado registros com descrição vazia: {len(batch)} restantes")

    return batch


def get_audit_output_dir(project_root: Optional[Path] = None) -> Path:
    """Retorna o caminho do diretório de output de auditoria."""
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    audit_dir = project_root / "data" / "auditoria"
    audit_dir.mkdir(parents=True, exist_ok=True)

    return audit_dir
