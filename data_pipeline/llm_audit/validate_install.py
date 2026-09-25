"""Script para validar instalação e setup do módulo llm_audit."""

import os
import sys
from pathlib import Path

# Carregar .env se existir
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass


def check_imports():
    """Verifica se todas as dependências estão instaladas."""
    print("\n📦 Verificando dependências...")

    dependencies = {
        "langchain": "langchain",
        "langchain_openai": "langchain-openai",
        "pydantic": "pydantic",
        "pandas": "pandas",
    }

    missing = []
    for module_name, package_name in dependencies.items():
        try:
            __import__(module_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name}")
            missing.append(package_name)

    if missing:
        print(f"\n❌ Dependências faltando: {', '.join(missing)}")
        print(f"   Execute: pip install {' '.join(missing)}")
        return False

    print("✅ Todas as dependências instaladas")
    return True


def check_api_key():
    """Verifica se OPENAI_API_KEY está configurada."""
    print("\n🔑 Verificando OPENAI_API_KEY...")

    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("  ✗ OPENAI_API_KEY não encontrada")
        print("   Execute: export OPENAI_API_KEY=\"sk-...\"")
        return False

    if not api_key.startswith("sk-"):
        print("  ✗ OPENAI_API_KEY inválida (não começa com 'sk-')")
        return False

    print(f"  ✓ OPENAI_API_KEY configurada (primeiros 20 chars: {api_key[:20]}...)")
    return True


def check_silver_file():
    """Verifica se o arquivo Silver existe."""
    print("\n📂 Verificando arquivo Silver...")

    # Detectar projeto root (mesmo do diagnose_silver.py)
    project_root = Path(__file__).parent.parent.parent
    silver_file = project_root / "data" / "silver" / "imoveis_limpos.parquet"

    print(f"   Procurando em: {silver_file}")

    if not silver_file.exists():
        print(f"  ✗ Silver não encontrado: {silver_file}")
        print("   Execute: uv run python -m data_pipeline.medallion.bronze_to_silver")
        return False

    print(f"  ✓ Arquivo encontrado ({silver_file.stat().st_size / (1024*1024):.2f} MB)")

    # Tentar carregar
    try:
        import pandas as pd
        df = pd.read_parquet(silver_file)
        print(f"  ✓ Lido com sucesso: {len(df)} registros")

        # Verificar colunas necessárias
        required_cols = {
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
        missing_cols = required_cols - set(df.columns)

        if missing_cols:
            print(f"  ✗ Colunas faltando: {missing_cols}")
            print(f"   Colunas presentes: {sorted(df.columns)}")
            return False

        print(f"  ✓ Todas as colunas necessárias presentes")
        return True

    except ImportError as e:
        print(f"  ✗ Erro de importação: {e}")
        print("   Execute: uv sync --group llm_audit")
        return False
    except Exception as e:
        print(f"  ✗ Erro ao carregar Silver: {e}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


def check_module_structure():
    """Verifica estrutura do módulo."""
    print("\n🏗️ Verificando estrutura do módulo...")

    module_root = Path(__file__).parent
    required_files = {
        "__init__.py",
        "schemas.py",
        "prompts.py",
        "chain.py",
        "data.py",
        "run_audit.py",
        "merge_audit_results.py",
        "cli.py",
        "validate_install.py",
        "README.md",
    }

    missing = []
    for filename in required_files:
        filepath = module_root / filename
        if filepath.exists():
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename}")
            missing.append(filename)

    if missing:
        print(f"❌ Arquivos faltando: {missing}")
        return False

    print("✅ Estrutura do módulo OK")
    return True


def check_audit_dir():
    """Verifica se diretório de auditoria existe/pode ser criado."""
    print("\n📁 Verificando diretório de auditoria...")

    project_root = Path(__file__).parent.parent.parent
    audit_dir = project_root / "data" / "auditoria"

    try:
        audit_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Diretório de auditoria pronto: {audit_dir}")
        return True
    except Exception as e:
        print(f"  ✗ Erro ao criar diretório: {e}")
        return False


def test_imports():
    """Tenta importar o módulo completo."""
    print("\n🧪 Testando imports do módulo...")

    try:
        from data_pipeline.llm_audit import (
            AuditoriaResultado,
            NovasFeatures,
            create_audit_chain,
            run_audit,
        )
        print("  ✓ Imports principais OK")

        from data_pipeline.llm_audit.merge_audit_results import full_pipeline
        print("  ✓ Merge imports OK")

        from data_pipeline.llm_audit.cli import main
        print("  ✓ CLI imports OK")

        print("✅ Todos os imports funcionando")
        return True

    except Exception as e:
        print(f"✗ Erro ao importar: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todas as validações."""
    print("=" * 70)
    print("  LLM Audit - Validação de Instalação e Setup")
    print("=" * 70)

    checks = [
        ("Dependências", check_imports),
        ("OPENAI_API_KEY", check_api_key),
        ("Arquivo Silver", check_silver_file),
        ("Estrutura do módulo", check_module_structure),
        ("Diretório de auditoria", check_audit_dir),
        ("Imports do módulo", test_imports),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Erro ao executar {name}: {e}")
            results[name] = False

    # Resumo
    print("\n" + "=" * 70)
    print("  RESUMO")
    print("=" * 70)

    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 Tudo pronto! Execute:")
        print("   python -m data_pipeline.llm_audit.cli audit --limit 5")
    else:
        print("\n⚠️ Corrija os problemas acima antes de executar a auditoria")
        sys.exit(1)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
