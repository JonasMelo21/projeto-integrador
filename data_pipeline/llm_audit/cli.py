"""CLI para executar auditoria LLM."""

import argparse
import json
import logging
import sys
from pathlib import Path

from .run_audit import run_audit
from .merge_audit_results import full_pipeline

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Entry point da CLI."""
    parser = argparse.ArgumentParser(
        description="LLM Audit - Auditoria de dados imobiliários via OpenAI",
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # Comando: audit
    audit_parser = subparsers.add_parser(
        "audit",
        help="Executar auditoria LLM em batch"
    )
    audit_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limitar número de imóveis a processar (padrão: todos)"
    )
    audit_parser.add_argument(
        "--only-suspicious",
        action="store_true",
        help="Procesar apenas imóveis com flag_suspeito=True"
    )
    audit_parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="Modelo OpenAI (padrão: gpt-4o-mini)"
    )
    audit_parser.add_argument(
        "--rate-limit-delay",
        type=float,
        default=0.5,
        help="Delay entre requisições em segundos (padrão: 0.5)"
    )
    audit_parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Raiz do projeto (detecção automática se omitido)"
    )

    # Comando: merge
    merge_parser = subparsers.add_parser(
        "merge",
        help="Fazer merge dos resultados de auditoria na base ML"
    )
    merge_parser.add_argument(
        "silver_parquet",
        type=Path,
        help="Caminho do arquivo imoveis_limpos.parquet (Silver)"
    )
    merge_parser.add_argument(
        "audit_json",
        type=Path,
        help="Caminho do arquivo de auditoria JSON"
    )
    merge_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Arquivo de saída (padrão: imoveis_com_auditoria.parquet)"
    )
    merge_parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Raiz do projeto (só usado se --output omitido)"
    )

    # Comando: pipeline (audit + merge em uma execução)
    pipeline_parser = subparsers.add_parser(
        "pipeline",
        help="Executar pipeline completo (audit + merge)"
    )
    pipeline_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limitar número de imóveis a processar"
    )
    pipeline_parser.add_argument(
        "--only-suspicious",
        action="store_true",
        help="Procesar apenas imóveis com flag_suspeito=True"
    )
    pipeline_parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="Modelo OpenAI"
    )
    pipeline_parser.add_argument(
        "--rate-limit-delay",
        type=float,
        default=0.5,
        help="Delay entre requisições"
    )
    pipeline_parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Raiz do projeto"
    )
    pipeline_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Arquivo de saída final"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Executar comando
    if args.command == "audit":
        _cmd_audit(args)
    elif args.command == "merge":
        _cmd_merge(args)
    elif args.command == "pipeline":
        _cmd_pipeline(args)


def _cmd_audit(args):
    """Comando: audit"""
    logger.info("🚀 Iniciando auditoria LLM...")

    try:
        resultado = run_audit(
            project_root=args.project_root,
            limit=args.limit,
            only_suspicious=args.only_suspicious,
            model_name=args.model,
            rate_limit_delay=args.rate_limit_delay,
        )

        logger.info(f"\n✅ Auditoria concluída!")
        print(json.dumps(resultado, indent=2))

        sys.exit(0 if resultado.get("status") == "success" else 1)

    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        sys.exit(1)


def _cmd_merge(args):
    """Comando: merge"""
    # Validar paths
    if not args.silver_parquet.exists():
        logger.error(f"❌ Silver não encontrado: {args.silver_parquet}")
        sys.exit(1)

    if not args.audit_json.exists():
        logger.error(f"❌ Auditoria não encontrada: {args.audit_json}")
        sys.exit(1)

    # Determinar arquivo de saída
    if args.output is None:
        if args.project_root is None:
            args.project_root = Path(__file__).parent.parent.parent
        args.output = args.project_root / "data" / "silver" / "imoveis_com_auditoria.parquet"

    logger.info(f"🔗 Fazendo merge:")
    logger.info(f"   Silver: {args.silver_parquet}")
    logger.info(f"   Auditoria: {args.audit_json}")
    logger.info(f"   Output: {args.output}")

    try:
        resultado = full_pipeline(
            silver_parquet=args.silver_parquet,
            audit_json=args.audit_json,
            output_parquet=args.output,
        )

        logger.info(f"\n✅ Merge concluído!")
        print(json.dumps(resultado, indent=2))

        sys.exit(0 if resultado.get("status") == "success" else 1)

    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        sys.exit(1)


def _cmd_pipeline(args):
    """Comando: pipeline (audit + merge)"""
    logger.info("🚀 Iniciando pipeline completo (audit + merge)...")

    try:
        # 1. Executar auditoria
        audit_resultado = run_audit(
            project_root=args.project_root,
            limit=args.limit,
            only_suspicious=args.only_suspicious,
            model_name=args.model,
            rate_limit_delay=args.rate_limit_delay,
        )

        if audit_resultado.get("status") != "success":
            logger.error("❌ Auditoria falhou")
            sys.exit(1)

        audit_file = Path(audit_resultado["arquivo_saida"])
        logger.info(f"✓ Auditoria concluída: {audit_file}")

        # 2. Determinar paths para merge
        if args.project_root is None:
            args.project_root = Path(__file__).parent.parent.parent

        silver_file = args.project_root / "data" / "silver" / "imoveis_limpos.parquet"

        if not silver_file.exists():
            logger.error(f"❌ Silver não encontrado: {silver_file}")
            sys.exit(1)

        if args.output is None:
            args.output = args.project_root / "data" / "silver" / "imoveis_com_auditoria.parquet"

        # 3. Fazer merge
        logger.info("\n🔗 Iniciando merge...")
        merge_resultado = full_pipeline(
            silver_parquet=silver_file,
            audit_json=audit_file,
            output_parquet=args.output,
        )

        # 4. Resultado final
        logger.info(f"\n✅ Pipeline concluído com sucesso!")
        resultado_final = {
            "audit": audit_resultado,
            "merge": merge_resultado,
        }
        print(json.dumps(resultado_final, indent=2))

        sys.exit(0)

    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
