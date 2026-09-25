"""Prompts para auditoria LLM de imóveis."""

from langchain_core.prompts import PromptTemplate


# Prompt para auditoria de imóveis suspeitos
AUDIT_SUSPICIOUS_PROMPT = PromptTemplate(
    input_variables=[
        "descricao_completa",
        "tipo_imovel",
        "bairro",
        "preco",
        "area_m2",
        "vagas",
        "motivo_suspeita",
        "id_hex",
    ],
    template="""Você é um auditor imobiliário experiente analisando um anúncio suspeito de aluguel.

DADOS DO IMÓVEL:
- ID: {id_hex}
- Tipo: {tipo_imovel}
- Bairro: {bairro}
- Preço: R$ {preco}
- Área: {area_m2} m²
- Vagas de garagem: {vagas}

MOTIVO DA SUSPEITA:
{motivo_suspeita}

DESCRIÇÃO COMPLETA DO ANÚNCIO:
{descricao_completa}

TAREFAS:
1. **Auditoria**: Baseado APENAS no texto da descrição fornecida, avalie se o veredicto deve ser:
   - "MANTER": Os dados parecem corretos, ou a base de decisão é fraca para corrigir.
   - "CORRIGIR": É possível extrair valores corrigidos da descrição (ex: "50 m²" ou "2 vagas").
   - "EXCLUIR": O anúncio é claramente fraudulento, duplicado ou inutilizável.

2. **Extração de Features Qualitativas**: Analise a descrição e determine INEQUIVOCAMENTE (só marque como True se tiver menção explícita):
   - `mobiliado`: Verdadeiro APENAS se mencionado que é "mobiliado" ou "mobiliadO".
   - `reformado`: Verdadeiro APENAS se mencionado "reformado", "recém-reformado", etc.
   - `tem_lazer`: Verdadeiro APENAS se mencionar piscina, academia, churrasqueira, quadra, sauna, etc.
   - `ar_condicionado`: Verdadeiro APENAS se mencionado "ar-condicionado", "A/C", ou "climatizado".
   - **Dúvida = False**: Em caso de ambiguidade ou falta de menção, use False.

3. **Justificativa**: Uma sentença curta explicando seu veredicto e/ou correções.

Responda APENAS com um objeto JSON válido, sem texto adicional.
""",
)


# Prompt para extração de features de imóveis normais
EXTRACT_FEATURES_PROMPT = PromptTemplate(
    input_variables=[
        "descricao_completa",
        "tipo_imovel",
        "bairro",
        "preco",
        "area_m2",
        "vagas",
        "id_hex",
    ],
    template="""Você é um especialista em análise de anúncios imobiliários.

DADOS DO IMÓVEL:
- ID: {id_hex}
- Tipo: {tipo_imovel}
- Bairro: {bairro}
- Preço: R$ {preco}
- Área: {area_m2} m²
- Vagas de garagem: {vagas}

DESCRIÇÃO COMPLETA DO ANÚNCIO:
{descricao_completa}

TAREFA:
Analise a descrição e extraia APENAS as features qualitativas presentes, sendo INEQUÍVOCO:
- `mobiliado`: Verdadeiro APENAS se mencionado explicitamente que é "mobiliado" ou similar.
- `reformado`: Verdadeiro APENAS se mencionado "reformado", "recém-reformado", etc.
- `tem_lazer`: Verdadeiro APENAS se mencionar piscina, academia, churrasqueira, quadra, sauna, etc.
- `ar_condicionado`: Verdadeiro APENAS se mencionado "ar-condicionado", "A/C", "climatizado", etc.
- **Dúvida = False**: Em caso de ambiguidade ou falta de menção, use False.

O veredicto deve ser automaticamente "MANTER" (imóvel não é suspeito).

Responda APENAS com um objeto JSON válido, sem texto adicional.
""",
)


def get_audit_prompt(flag_suspeito: bool) -> PromptTemplate:
    """Retorna o prompt apropriado baseado no status de suspeita."""
    return AUDIT_SUSPICIOUS_PROMPT if flag_suspeito else EXTRACT_FEATURES_PROMPT
