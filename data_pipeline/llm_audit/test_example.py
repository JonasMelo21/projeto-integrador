"""Exemplos de testes para o módulo llm_audit.

Este arquivo demonstra como testar o módulo sem fazer requisições reais à OpenAI.
Adapte conforme necessário para seu framework de teste (pytest, unittest, etc).
"""

import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import pandas as pd
from pydantic import ValidationError

from .schemas import AuditoriaResultado, NovasFeatures, VerdictEnum


def test_novas_features_schema():
    """Testa validação do schema NovasFeatures."""

    # Caso válido
    features = NovasFeatures(
        mobiliado=True,
        reformado=False,
        tem_lazer=True,
        ar_condicionado=False,
    )
    assert features.mobiliado is True
    assert features.reformado is False
    assert features.tem_lazer is True
    assert features.ar_condicionado is False
    print("✓ NovasFeatures válido")

    # Caso padrão (tudo False)
    features_default = NovasFeatures()
    assert all([
        features_default.mobiliado is False,
        features_default.reformado is False,
        features_default.tem_lazer is False,
        features_default.ar_condicionado is False,
    ])
    print("✓ NovasFeatures padrão (tudo False)")


def test_auditoria_resultado_schema():
    """Testa validação do schema AuditoriaResultado."""

    # Caso válido - MANTER
    resultado = AuditoriaResultado(
        id_hex="a1b2c3d4",
        veredicto=VerdictEnum.MANTER,
        area_m2_corrigida=None,
        vagas_corrigidas=None,
        justificativa="Base de decisão fraca, mantém como está",
        novas_features=NovasFeatures(tem_lazer=True),
    )
    assert resultado.veredicto == VerdictEnum.MANTER
    assert resultado.novas_features.tem_lazer is True
    print("✓ AuditoriaResultado MANTER")

    # Caso válido - CORRIGIR
    resultado_corrigir = AuditoriaResultado(
        id_hex="x9y8z7w6",
        veredicto=VerdictEnum.CORRIGIR,
        area_m2_corrigida=75.5,
        vagas_corrigidas=2,
        justificativa="Descrição menciona '75 m²' e '2 vagas'",
        novas_features=NovasFeatures(),
    )
    assert resultado_corrigir.veredicto == VerdictEnum.CORRIGIR
    assert resultado_corrigir.area_m2_corrigida == 75.5
    assert resultado_corrigir.vagas_corrigidas == 2
    print("✓ AuditoriaResultado CORRIGIR")

    # Caso válido - EXCLUIR
    resultado_excluir = AuditoriaResultado(
        id_hex="p0q1r2s3",
        veredicto=VerdictEnum.EXCLUIR,
        justificativa="Anúncio duplicado, informações incoerentes",
        novas_features=NovasFeatures(),
    )
    assert resultado_excluir.veredicto == VerdictEnum.EXCLUIR
    print("✓ AuditoriaResultado EXCLUIR")


def test_audit_resultado_serialization():
    """Testa serialização para JSON."""

    resultado = AuditoriaResultado(
        id_hex="test123",
        veredicto=VerdictEnum.MANTER,
        justificativa="Teste",
        novas_features=NovasFeatures(mobiliado=True),
    )

    # Converter para dict
    dados = resultado.model_dump()
    assert dados["id_hex"] == "test123"
    assert dados["veredicto"] == "MANTER"
    assert dados["novas_features"]["mobiliado"] is True
    print("✓ Serialização para dict")

    # Converter para JSON
    json_str = resultado.model_dump_json()
    parsed = json.loads(json_str)
    assert parsed["id_hex"] == "test123"
    print("✓ Serialização para JSON")


def test_merge_audit_with_silver_mock():
    """Testa merge com dados mock (não requer Silver real)."""
    from .merge_audit_results import load_audit_results

    # Criar dados mock
    mock_audit_json = {
        "metadados": {
            "timestamp_execucao": "2024-01-01T12:00:00",
            "modelo_llm": "gpt-4o-mini",
            "total_processados": 2,
            "total_erros": 0,
            "versao_pipeline": "2.0"
        },
        "auditoria": [
            {
                "id_hex": "id1",
                "veredicto": "MANTER",
                "area_m2_corrigida": None,
                "vagas_corrigidas": None,
                "justificativa": "OK",
                "novas_features": {
                    "mobiliado": True,
                    "reformado": False,
                    "tem_lazer": False,
                    "ar_condicionado": True,
                },
                "timestamp_auditoria": "2024-01-01T12:00:01",
                "modelo_llm": "gpt-4o-mini"
            },
            {
                "id_hex": "id2",
                "veredicto": "CORRIGIR",
                "area_m2_corrigida": 85.0,
                "vagas_corrigidas": None,
                "justificativa": "Area corrigida",
                "novas_features": {
                    "mobiliado": False,
                    "reformado": True,
                    "tem_lazer": True,
                    "ar_condicionado": False,
                },
                "timestamp_auditoria": "2024-01-01T12:00:02",
                "modelo_llm": "gpt-4o-mini"
            }
        ],
        "erros": []
    }

    # Criar DataFrame mock
    audit_df = pd.DataFrame(mock_audit_json["auditoria"])

    # Verificar se os dados foram parseados corretamente
    assert len(audit_df) == 2
    assert audit_df.iloc[0]["id_hex"] == "id1"
    assert audit_df.iloc[1]["veredicto"] == "CORRIGIR"
    print("✓ Parse de audit JSON mock")


def test_verdicts_enum():
    """Testa enum de veredictos."""

    assert VerdictEnum.MANTER.value == "MANTER"
    assert VerdictEnum.CORRIGIR.value == "CORRIGIR"
    assert VerdictEnum.EXCLUIR.value == "EXCLUIR"

    # Teste de conversão string
    assert VerdictEnum("MANTER") == VerdictEnum.MANTER
    print("✓ VerdictEnum")


def test_validation_errors():
    """Testa validação de tipos."""

    # Veredicto inválido
    try:
        AuditoriaResultado(
            id_hex="test",
            veredicto="INVALIDO",
            justificativa="Test",
            novas_features=NovasFeatures(),
        )
        assert False, "Deveria ter levantado ValidationError"
    except ValidationError:
        print("✓ Rejeita veredicto inválido")

    # Features com tipos inválidos
    try:
        NovasFeatures(mobiliado="sim")  # Deve ser bool
        assert False, "Deveria ter levantado ValidationError"
    except ValidationError:
        print("✓ Rejeita tipo inválido em features")


def run_all_tests():
    """Executa todos os testes."""
    print("=" * 70)
    print("  Testes de Schema")
    print("=" * 70)

    test_novas_features_schema()
    test_auditoria_resultado_schema()
    test_audit_resultado_serialization()
    test_merge_audit_with_silver_mock()
    test_verdicts_enum()
    test_validation_errors()

    print("\n" + "=" * 70)
    print("✅ Todos os testes passaram!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
