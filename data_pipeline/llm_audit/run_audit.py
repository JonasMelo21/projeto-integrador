"""Script principal para executar auditoria LLM em batch."""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

# Carregar .env se existir
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

from .chain import create_audit_chain, run_audit_for_row
from .data import (
    load_silver_data,
    validate_required_columns,
    prepare_audit_batch,
    get_audit_output_dir,
)
from .schemas import AuditoriaResultado

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_audit(
    project_root: Optional[Path] = None,
    limit: Optional[int] = None,
    only_suspicious: bool = False,
    model_name: str = "gpt-4o-mini",
    rate_limit_delay: float = 0.5,
) -> dict:
    """
    Executa a auditoria LLM em batch para os imóveis da Silver.

    Args:
        project_root: Raiz do projeto (detecção automática se None).
        limit: Limite de registros a processar (None = todos).
        only_suspicious: Se True, processa apenas imóveis com flag_suspeito=True.
        model_name: Modelo OpenAI a usar.
        rate_limit_delay: Delay entre requisições (segundos) para evitar rate limits.

    Returns:
        Dict com estatísticas da execução.
    """
    start_time = datetime.utcnow()
    logger.info("=" * 70)
    logger.info(f"Iniciando auditoria LLM - {start_time.isoformat()}")
    logger.info("=" * 70)

    # 1. Carregar dados
    df = load_silver_data(project_root)
    if not validate_required_columns(df):
        raise ValueError("Validação de colunas falhou")

    # 2. Preparar batch
    batch = prepare_audit_batch(
        df,
        limit=limit,
        only_suspicious=only_suspicious,
    )

    if batch.empty:
        logger.warning("Nenhum registro para auditar")
        return {"status": "empty", "processados": 0}

    # 3. Criar chains
    try:
        chains = create_audit_chain(model_name)
        logger.info(f"✓ Chain criada com modelo: {model_name}")
    except ValueError as e:
        logger.error(f"Erro ao criar chain: {e}")
        raise

    # 4. Processar cada linha
    resultados = []
    erros = []

    total = len(batch)
    for idx, (_, row) in enumerate(batch.iterrows(), 1):
        try:
            resultado = run_audit_for_row(
                chains=chains,
                id_hex=str(row["id_hex"]),
                descricao_completa=row["descricao_completa"],
                tipo_imovel=str(row["tipo_imovel"]),
                bairro=str(row["bairro"]),
                preco=float(row["preco"]) if pd.notna(row["preco"]) else 0,
                area_m2=float(row["area_m2"]) if pd.notna(row["area_m2"]) else 0,
                vagas=int(row["vagas"]) if pd.notna(row["vagas"]) else 0,
                flag_suspeito=bool(row.get("flag_suspeito", False)),
                motivo_suspeita=str(row.get("motivo_suspeita", "")),
            )

            if resultado:
                resultados.append(resultado)
                logger.info(f"[{idx}/{total}] ✓ {str(row['id_hex'])}")
            else:
                erros.append({"id_hex": str(row["id_hex"]), "erro": "Retorno None"})
                logger.warning(f"[{idx}/{total}] ✗ {str(row['id_hex'])} retornou None")

            # Rate limiting para evitar excesso de requisições
            if idx < total:
                time.sleep(rate_limit_delay)

        except Exception as e:
            erros.append({"id_hex": str(row["id_hex"]), "erro": str(e)})
            logger.error(f"[{idx}/{total}] ✗ Erro ao processar {str(row['id_hex'])}: {e}")

    # 5. Salvar resultados
    output_dir = get_audit_output_dir(project_root)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"auditoria_llm_{timestamp}.json"

    # Serializar resultados
    dados_saida = {
        "metadados": {
            "timestamp_execucao": datetime.utcnow().isoformat(),
            "modelo_llm": model_name,
            "total_processados": len(resultados),
            "total_erros": len(erros),
            "versao_pipeline": "2.0",
        },
        "auditoria": [
            {
                **resultado.model_dump(),
                "timestamp_auditoria": resultado.timestamp_auditoria.isoformat(),
            }
            for resultado in resultados
        ],
        "erros": erros,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dados_saida, f, indent=2, ensure_ascii=False)

    logger.info(f"\n✅ Auditoria concluída!")
    logger.info(f"   - Arquivo: {output_file}")
    logger.info(f"   - Processados: {len(resultados)}")
    logger.info(f"   - Erros: {len(erros)}")
    logger.info(f"   - Tempo total: {(datetime.utcnow() - start_time).total_seconds():.1f}s")

    return {
        "status": "success",
        "processados": len(resultados),
        "erros": len(erros),
        "arquivo_saida": str(output_file),
        "tempo_execucao_s": (datetime.utcnow() - start_time).total_seconds(),
    }


if __name__ == "__main__":
    # Exemplo de uso direto
    resultado = run_audit(
        limit=5,  # Para testes, processar apenas 5
        only_suspicious=False,
        rate_limit_delay=1.0,
    )
    print(f"\n{json.dumps(resultado, indent=2)}")
