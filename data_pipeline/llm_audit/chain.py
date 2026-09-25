"""LangChain chain para auditoria e extração de features."""

import os
import logging
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

from .schemas import AuditoriaResultado, NovasFeatures, VerdictEnum
from .prompts import AUDIT_SUSPICIOUS_PROMPT, EXTRACT_FEATURES_PROMPT

logger = logging.getLogger(__name__)


def create_audit_chain(model_name: str = "gpt-4o-mini"):
    """
    Cria a chain de auditoria com structured output forçado pelo Pydantic.

    Args:
        model_name: Nome do modelo OpenAI a usar.

    Returns:
        Chain configurada para retornar AuditoriaResultado estruturado.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada nas variáveis de ambiente")

    llm = ChatOpenAI(
        api_key=api_key,
        model=model_name,
        temperature=0,
        timeout=30,
        max_retries=3,
    )

    # Força structured output usando Pydantic
    llm_with_structured_output = llm.with_structured_output(AuditoriaResultado)

    # Chain para auditoria de suspeitos
    audit_chain = AUDIT_SUSPICIOUS_PROMPT | llm_with_structured_output

    # Chain para extração de features
    extract_chain = EXTRACT_FEATURES_PROMPT | llm_with_structured_output

    return {
        "audit": audit_chain,
        "extract": extract_chain,
        "model_name": model_name,
    }


def run_audit_for_row(
    chains: dict,
    id_hex: str,
    descricao_completa: str,
    tipo_imovel: str,
    bairro: str,
    preco: float,
    area_m2: float,
    vagas: Optional[int],
    flag_suspeito: bool,
    motivo_suspeita: str = "",
) -> Optional[AuditoriaResultado]:
    """
    Executa a auditoria para uma linha específica do dataset.

    Args:
        chains: Dict contendo as chains "audit", "extract" e "model_name".
        id_hex: ID único do imóvel.
        descricao_completa: Descrição completa do anúncio.
        tipo_imovel: Tipo do imóvel (apartamento, casa, etc).
        bairro: Nome do bairro.
        preco: Preço do aluguel.
        area_m2: Área em m².
        vagas: Número de vagas de garagem.
        flag_suspeito: Se o imóvel foi marcado como suspeito.
        motivo_suspeita: Motivo da suspeita (se flag_suspeito=True).

    Returns:
        AuditoriaResultado ou None em caso de erro.
    """
    try:
        if not descricao_completa or str(descricao_completa).strip() == "":
            logger.warning(f"Descrição vazia para {id_hex}, pulando")
            return None

        # Preparar inputs
        input_data = {
            "id_hex": id_hex,
            "descricao_completa": str(descricao_completa).strip(),
            "tipo_imovel": str(tipo_imovel).strip(),
            "bairro": str(bairro).strip(),
            "preco": float(preco) if preco else 0,
            "area_m2": float(area_m2) if area_m2 else 0,
            "vagas": int(vagas) if vagas else 0,
            "motivo_suspeita": str(motivo_suspeita).strip() if motivo_suspeita else "",
        }

        # Selecionar chain apropriada
        chain = chains["audit"] if flag_suspeito else chains["extract"]

        # Executar
        resultado = chain.invoke(input_data)

        # Garantir que o modelo está preenchido
        if isinstance(resultado, dict):
            resultado = AuditoriaResultado(**resultado)

        resultado.modelo_llm = chains["model_name"]

        logger.info(f"✓ Auditado {id_hex}: {resultado.veredicto}")
        return resultado

    except Exception as e:
        logger.error(f"✗ Erro ao auditar {id_hex}: {str(e)}")
        return None
