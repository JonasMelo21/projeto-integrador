"""Pydantic schemas para auditoria LLM e extração de features qualitativas."""

from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VerdictEnum(str, Enum):
    """Enum para veredicto da auditoria."""
    MANTER = "MANTER"
    CORRIGIR = "CORRIGIR"
    EXCLUIR = "EXCLUIR"


class NovasFeatures(BaseModel):
    """Features qualitativas extraídas da descrição do imóvel."""

    mobiliado: bool = Field(
        default=False,
        description="Se o imóvel é mobiliado (só True se mencionado explicitamente)"
    )
    reformado: bool = Field(
        default=False,
        description="Se o imóvel foi reformado (só True se mencionado explicitamente)"
    )
    tem_lazer: bool = Field(
        default=False,
        description="Se tem lazer (piscina, academia, churrasqueira, etc.)"
    )
    ar_condicionado: bool = Field(
        default=False,
        description="Se tem ar-condicionado (só True se mencionado explicitamente)"
    )


class AuditoriaResultado(BaseModel):
    """Resultado completo da auditoria LLM para um imóvel."""

    id_hex: str = Field(
        description="ID único do imóvel (hex)"
    )
    veredicto: VerdictEnum = Field(
        description="Ação recomendada: MANTER, CORRIGIR ou EXCLUIR"
    )
    area_m2_corrigida: Optional[float] = Field(
        default=None,
        description="Área corrigida em m², se o LLM identificou erro (para flag_suspeito=True)"
    )
    vagas_corrigidas: Optional[int] = Field(
        default=None,
        description="Número de vagas corrigidas (para flag_suspeito=True)"
    )
    justificativa: str = Field(
        description="Justificativa curta do veredicto e/ou correções"
    )
    novas_features: NovasFeatures = Field(
        description="Features qualitativas extraídas da descrição"
    )
    timestamp_auditoria: datetime = Field(
        default_factory=datetime.utcnow,
        description="Quando a auditoria foi realizada"
    )
    modelo_llm: str = Field(
        default="gpt-4o-mini",
        description="Modelo LLM utilizado"
    )
