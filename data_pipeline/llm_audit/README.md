# LLM Audit Module

**Auditoria de Dados + Extração de Features Qualitativas via LLM (OpenAI)**

## Visão Geral

O módulo `llm_audit` roda em **batch separado do ETL principal** e serve dois propósitos complementares:

1. **Auditoria de Dados (LLM-as-a-Judge)**: Para linhas marcadas como `flag_suspeito=True`, o LLM avalia se o imóvel deve ser MANTIDO, CORRIGIDO (com valores extraídos do texto) ou EXCLUÍDO.

2. **Engenharia de Features Qualitativas**: Para TODA a base (suspeitos ou não), extrai features booleanas inequívocas da descrição:
   - `mobiliado`: Verdadeiro se "mobiliado" é mencionado explicitamente
   - `reformado`: Verdadeiro se "reformado" ou "recém-reformado" é mencionado
   - `tem_lazer`: Verdadeiro se menciona piscina, academia, churrasqueira, quadra, etc.
   - `ar_condicionado`: Verdadeiro se menciona "A/C", "climatizado", etc.

## Arquitetura

```
llm_audit/
├── __init__.py           # Exports públicos
├── schemas.py            # Modelos Pydantic (AuditoriaResultado, NovasFeatures)
├── prompts.py            # Templates de prompts (audit + extract)
├── chain.py              # LangChain chains com structured output
├── data.py               # Carregamento e validação de dados
├── run_audit.py          # Script principal (batch processing)
├── merge_audit_results.py # Integração dos resultados na base ML
└── README.md             # Este arquivo
```

## Setup

### 1. Instalar Dependências

**Com `uv` (recomendado - mais rápido):**
```bash
uv sync --group llm_audit
```

**Ou manualmente:**
```bash
uv pip install -e ".[llm_audit]"
```

**Compatível com pip (para ambientes sem uv):**
```bash
pip install langchain langchain-openai pydantic pandas
```

### 2. Configurar API Key OpenAI

```bash
export OPENAI_API_KEY="sk-..."
```

Ou em Python:
```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
```

## Uso

### 1. Executar Auditoria em Batch

```python
from data_pipeline.llm_audit import run_audit

resultado = run_audit(
    project_root=None,        # Detecta automaticamente
    limit=None,               # None = processar todos
    only_suspicious=False,    # True = apenas flag_suspeito=True
    model_name="gpt-4o-mini", # Modelo OpenAI
    rate_limit_delay=0.5,     # Segundos entre requisições
)

print(resultado)
# Output: {
#   "status": "success",
#   "processados": 900,
#   "erros": 2,
#   "arquivo_saida": "data/auditoria/auditoria_llm_20240101_120000.json",
#   "tempo_execucao_s": 1234.5
# }
```

### 2. Fazer Merge com a Base de ML

```python
from data_pipeline.llm_audit.merge_audit_results import full_pipeline
from pathlib import Path

resultado_merge = full_pipeline(
    silver_parquet=Path("data/silver/imoveis_limpos.parquet"),
    audit_json=Path("data/auditoria/auditoria_llm_*.json"),
    output_parquet=Path("data/silver/imoveis_com_auditoria.parquet"),
)

print(resultado_merge)
# Output: {
#   "status": "success",
#   "registros_processados": 900,
#   "registros_excluidos": 5,
#   "registros_mantidos": 890,
#   "registros_finais": 895,
#   "arquivo_output": "data/silver/imoveis_com_auditoria.parquet"
# }
```

### 3. Script de Linha de Comando

```bash
# Executar auditoria completa
python -m data_pipeline.llm_audit.run_audit

# Fazer merge dos resultados
python data_pipeline/llm_audit/merge_audit_results.py \
    data/silver/imoveis_limpos.parquet \
    data/auditoria/auditoria_llm_*.json \
    data/silver/imoveis_com_auditoria.parquet
```

## Output

### Arquivo de Auditoria JSON

Estrutura append-only em `data/auditoria/auditoria_llm_TIMESTAMP.json`:

```json
{
  "metadados": {
    "timestamp_execucao": "2024-01-01T12:00:00",
    "modelo_llm": "gpt-4o-mini",
    "total_processados": 900,
    "total_erros": 2,
    "versao_pipeline": "2.0"
  },
  "auditoria": [
    {
      "id_hex": "a1b2c3d4...",
      "veredicto": "CORRIGIR",
      "area_m2_corrigida": 75.5,
      "vagas_corrigidas": 2,
      "justificativa": "Descrição menciona '75 m²' e '2 vagas de garagem'",
      "novas_features": {
        "mobiliado": false,
        "reformado": true,
        "tem_lazer": true,
        "ar_condicionado": true
      },
      "timestamp_auditoria": "2024-01-01T12:00:30",
      "modelo_llm": "gpt-4o-mini"
    },
    ...
  ],
  "erros": [
    {
      "id_hex": "x9y8z7w6...",
      "erro": "Descrição vazia ou inválida"
    }
  ]
}
```

### Base Enriquecida (Parquet)

Após merge, a base contém colunas adicionais:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `veredicto` | string | MANTER \| CORRIGIR \| EXCLUIR |
| `area_m2_corrigida` | float | Área corrigida (se veredicto=CORRIGIR) |
| `vagas_corrigidas` | int | Vagas corrigidas (se veredicto=CORRIGIR) |
| `justificativa` | string | Explicação do veredicto |
| `timestamp_auditoria` | datetime | Quando foi auditado |
| `modelo_llm` | string | Qual modelo fez a auditoria |
| `llm_mobiliado` | bool | Extraído da descrição |
| `llm_reformado` | bool | Extraído da descrição |
| `llm_tem_lazer` | bool | Extraído da descrição |
| `llm_ar_condicionado` | bool | Extraído da descrição |

## Fluxo Completo

```
1. Silver (imoveis_limpos.parquet)
   └─> run_audit()
       └─> auditoria_llm_*.json
           └─> merge_audit_with_silver()
               └─> imoveis_com_auditoria.parquet
                   └─> silver_to_gold.py (pipeline normal)
                       └─> Gold + ML splits
```

## Veredictos Explicados

### MANTER
- **Para suspeitos**: Base de decisão fraca; mantém dados como estão
- **Para normais**: Automaticamente aplicado (extração de features apenas)

### CORRIGIR
- LLM identificou valor correto mencionado na descrição
- Aplicado apenas para `area_m2` e `vagas` se mencionados
- Exemplo: "Apto de 75 m²" → corrige de 1 m² para 75 m²

### EXCLUIR
- Anúncio é fraudulento, duplicado ou completamente inutilizável
- Registros são removidos da base final

## Tratamento de Rate Limits

O módulo respeita limites da OpenAI:

- Default: `rate_limit_delay=0.5` segundos entre requisições
- Retries automáticos com exponential backoff via LangChain
- Logs detalhados para monitoramento

```python
resultado = run_audit(rate_limit_delay=1.0)  # Mais conservador
```

## Tratamento de Erros

Erros são:
- **Logados** com detalhes do id_hex e mensagem
- **Capturados** (não para a execução)
- **Registrados** em `auditoria_llm_*.json` seção `erros`
- **Contabilizados** no resultado final

Exemplos:
- Descrição vazia → skip com warning
- Timeout da API → retry automático
- JSON inválido do LLM → erro registrado

## Boas Práticas

1. **Sempre usar limit para testes**:
   ```python
   run_audit(limit=10)  # Testar com 10 imóveis primeiro
   ```

2. **Auditar apenas suspeitos em produção**:
   ```python
   run_audit(only_suspicious=True)  # ~41 imóveis em uma base de 900
   ```

3. **Variar rate_limit se necessário**:
   ```python
   run_audit(rate_limit_delay=2.0)  # Se receber muitos rate limits
   ```

4. **Verificar arquivo de saída antes de merge**:
   ```python
   # Inspecionar auditoria_llm_*.json
   # Contar erros, entender veredictos
   ```

5. **Manter histórico de auditorias**:
   - Timestamps únicos em cada execução
   - Não sobrescreve arquivos antigos
   - Permite rastrear mudanças ao longo do tempo

## Modelos Disponíveis

- `gpt-4o-mini`: Padrão, barato, rápido (~0.015$/1k tokens input)
- `gpt-4o`: Mais preciso, mais caro (~0.005$/1k tokens input)
- `gpt-4-turbo`: Contexto maior, mais caro

## Limitations

- **Descrição vazia**: Imóveis sem descrição são skipped
- **Texto truncado**: Se a descrição for cortada, features podem ser perdidas
- **Ambiguidade**: Em dúvida, o LLM marca como False
- **Idioma**: Optimizado para português brasileiro

## Exemplos Reais

### Exemplo 1: Imóvel Suspeito Corrigido

**Input**:
```
id_hex: a1b2c3d4
flag_suspeito: True
motivo_suspeita: "area ausente ou <= 0"
area_m2: 1 (suspeito)
descricao_completa: "Apartamento espaçoso de 85 m², 3 quartos, 2 suítes, reformado, ar-condicionado..."
```

**Output**:
```
veredicto: "CORRIGIR"
area_m2_corrigida: 85.0
justificativa: "Descrição menciona '85 m²' explicitamente"
llm_reformado: true
llm_ar_condicionado: true
```

### Exemplo 2: Feature Extraction Normal

**Input**:
```
id_hex: x9y8z7w6
flag_suspeito: False
descricao_completa: "Casa aconchegante com piscina, academia e churrasqueira..."
```

**Output**:
```
veredicto: "MANTER"
llm_mobiliado: false
llm_reformado: false
llm_tem_lazer: true  (piscina, academia, churrasqueira)
llm_ar_condicionado: false
```

## Troubleshooting

**Q: OPENAI_API_KEY não encontrada**
A: Defina antes de importar:
```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
```

**Q: Muitos rate limits**
A: Aumente `rate_limit_delay`:
```python
run_audit(rate_limit_delay=2.0)
```

**Q: Descricao_completa tem valores NaN**
A: Verifique `scraper_to_bronze.py` - pode estar truncando. O novo schema deve ter mantido `descricao_completa` inteira.

**Q: Merge resulta em menos registros que esperado**
A: Verifique quantos foram marcados com `veredicto="EXCLUIR"`. Use `only_suspicious=True` se quer auditar apenas suspeitos.

## Próximas Melhorias

- [ ] Suporte a múltiplos modelos em paralelo
- [ ] Fine-tuning do prompt com exemplos few-shot
- [ ] Integração com LLM local (Ollama, vLLM)
- [ ] Dashboard de monitoramento de auditorias
- [ ] Caching de requisições (evitar re-auditar mesmo imóvel)
