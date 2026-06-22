"""
Vanna training script — popula o ChromaDB com DDL, regras de negócio e
golden queries para o star schema do RentMaster (Brasília/DF).

Usage:
    PYTHONPATH=. uv run python backend/ai/train_vanna.py
"""
import asyncio
import uuid
from pathlib import Path

from backend.ai.vanna_agent import agent_memory, DATABASE_PATH
from vanna.core.tool.models import ToolContext
from vanna.core.user.models import User


async def main():
    ctx = ToolContext(
        user=User(id="training", username="training"),
        conversation_id="training",
        request_id=str(uuid.uuid4()),
        agent_memory=agent_memory,
    )

    # ── Phase A: Instrução crítica — arquitetura das tabelas ─────────────────
    print("Phase A: injetando instrução crítica do sistema...")
    await agent_memory.save_text_memory(content="""
===================================================================
INSTRUÇÃO CRÍTICA DO SISTEMA — ARQUITETURA DE TABELAS RENTMASTER
===================================================================

VOCÊ É UM ASSISTENTE DE ANÁLISE DE IMÓVEIS PARA ALUGUEL EM BRASÍLIA, DF.

BANCO DE DADOS: SQLite local — arquivo rental.db
DIALETO SQL: SQLite (use funções compatíveis: ROUND(), CAST(), LIKE, etc.)

TABELAS DISPONÍVEIS (use EXATAMENTE estes nomes):

➤ TABELA FATO (dados principais dos imóveis):
   fact_imoveis
   - id_imovel       INTEGER  — chave primária
   - id_hex          VARCHAR  — código único do imóvel (scraper)
   - id_imobiliaria_fk INTEGER — FK → dim_imobiliarias.id_imobiliaria
   - id_local_fk     INTEGER  — FK → dim_locais.id_local
   - titulo          VARCHAR  — título do anúncio (ex: "Apto 3 quartos Asa Norte")
   - url             VARCHAR  — link do anúncio original
   - preco           FLOAT    — aluguel mensal em R$ (ex: 3500.00)
   - area_m2         FLOAT    — área em metros quadrados (ex: 85.0)
   - quartos         INTEGER  — número de quartos/dormitórios
   - banheiros       INTEGER  — número de banheiros/suítes
   - vagas           INTEGER  — vagas de garagem
   - imagem          VARCHAR  — URL da foto principal
   - descricao       VARCHAR  — descrição do imóvel
   - data_extracao   DATETIME — data em que foi coletado

➤ DIMENSÃO LOCALIZAÇÃO:
   dim_locais
   - id_local  INTEGER — chave primária
   - bairro    VARCHAR — nome do bairro (ex: 'Asa Norte', 'Asa Sul', 'Sudoeste',
                         'Noroeste', 'Lago Sul', 'Park Way', 'Taguatinga',
                         'Setor Industrial', 'Vicente Pires')
   - cidade    VARCHAR — sempre 'BRASILIA'
   - uf        VARCHAR — sempre 'DF'

➤ DIMENSÃO IMOBILIÁRIA:
   dim_imobiliarias
   - id_imobiliaria INTEGER — chave primária
   - nome_empresa   VARCHAR — nome da imobiliária (ex: 'Alpha Brasilia ...')

JOINS OBRIGATÓRIOS para mostrar bairro e imobiliária:
  JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
  JOIN dim_imobiliarias di ON fi.id_imobiliaria_fk = di.id_imobiliaria

NUNCA use nomes de tabela diferentes de: fact_imoveis, dim_locais, dim_imobiliarias
NÃO existe tabela chamada: properties, imoveis, apartments, rental, listings
===================================================================
""", context=ctx)
    print("  ✓ instrução crítica injetada")

    # ── Phase B: DDL explícito com comentários ───────────────────────────────
    print("Phase B: injetando DDL comentado...")
    ddls = [
        """-- TABELA FATO: imóveis para aluguel em Brasília
CREATE TABLE fact_imoveis (
    id_imovel          INTEGER PRIMARY KEY,
    id_hex             VARCHAR(12) UNIQUE,     -- código único do scraper
    id_imobiliaria_fk  INTEGER REFERENCES dim_imobiliarias(id_imobiliaria),
    id_local_fk        INTEGER REFERENCES dim_locais(id_local),
    titulo             VARCHAR(500),            -- título do anúncio
    url                VARCHAR(1000),           -- link original DFimoveis
    preco              FLOAT,                   -- aluguel mensal R$
    area_m2            FLOAT,                   -- área em m²
    quartos            INTEGER,                 -- dormitórios
    banheiros          INTEGER,                 -- banheiros/suítes
    vagas              INTEGER,                 -- vagas de garagem
    imagem             VARCHAR(1000),
    descricao          VARCHAR(2000),
    data_extracao      DATETIME,
    created_at         DATETIME,
    updated_at         DATETIME
)""",
        """-- DIMENSÃO LOCALIZAÇÃO: bairros de Brasília/DF
CREATE TABLE dim_locais (
    id_local   INTEGER PRIMARY KEY,
    bairro     VARCHAR(255),  -- Asa Norte, Asa Sul, Sudoeste, Noroeste,
                               -- Lago Sul, Park Way, Taguatinga,
                               -- Setor Industrial, Vicente Pires
    cidade     VARCHAR(255),  -- sempre 'BRASILIA'
    uf         VARCHAR(2)     -- sempre 'DF'
)""",
        """-- DIMENSÃO IMOBILIÁRIA: empresas de aluguel
CREATE TABLE dim_imobiliarias (
    id_imobiliaria  INTEGER PRIMARY KEY,
    nome_empresa    VARCHAR(255)  -- nome da imobiliária
)""",
    ]
    for ddl in ddls:
        await agent_memory.save_text_memory(content=ddl, context=ctx)
    print("  ✓ 3 DDLs injetados")

    # ── Phase C: regras de negócio detalhadas ───────────────────────────────
    print("Phase C: injetando regras de negócio...")
    business_rules = [
        """
DOMÍNIO DO NEGÓCIO:
- Plataforma de análise de imóveis para ALUGUEL em Brasília, DF
- Dados coletados do portal DFimoveis via web scraping
- 35 imóveis cadastrados, 9 bairros, múltiplas imobiliárias
- Preços em R$/mês (aluguel mensal)
""",
        """
QUANDO O USUÁRIO PERGUNTAR SOBRE PREÇOS:
- "preço médio", "média de preço" → AVG(fi.preco)
- "preço por m²", "custo por metro" → fi.preco / fi.area_m2
- "mais barato", "menor preço" → ORDER BY preco ASC
- "mais caro", "maior preço" → ORDER BY preco DESC
- Sempre use ROUND(..., 2) para valores monetários
""",
        """
QUANDO O USUÁRIO PERGUNTAR SOBRE BAIRROS:
- JOIN obrigatório: JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
- Use dl.bairro para mostrar o nome
- Bairros disponíveis: Asa Norte, Asa Sul, Sudoeste, Noroeste,
  Lago Sul, Park Way, Taguatinga, Setor Industrial, Vicente Pires
- Para buscar bairro específico: WHERE dl.bairro = 'Asa Norte'
""",
        """
QUANDO O USUÁRIO PERGUNTAR SOBRE IMOBILIÁRIAS:
- JOIN obrigatório: JOIN dim_imobiliarias di ON fi.id_imobiliaria_fk = di.id_imobiliaria
- Use di.nome_empresa para mostrar o nome
- Para contar imóveis por imobiliária: COUNT(*) GROUP BY di.nome_empresa
""",
        """
QUANDO O USUÁRIO PERGUNTAR SOBRE QUARTOS/DORMITÓRIOS:
- Coluna: fact_imoveis.quartos (INTEGER)
- "2 quartos" → WHERE fi.quartos = 2
- "pelo menos 3 quartos" → WHERE fi.quartos >= 3
- "por número de quartos" → GROUP BY fi.quartos
""",
        """
QUANDO O USUÁRIO PERGUNTAR SOBRE GARAGEM/VAGAS:
- Coluna: fact_imoveis.vagas (INTEGER)
- "com garagem", "tem vaga" → WHERE fi.vagas > 0
- "sem garagem" → WHERE fi.vagas = 0 OR fi.vagas IS NULL
""",
        """
QUANDO O USUÁRIO PERGUNTAR SOBRE ÁREA/TAMANHO:
- Coluna: fact_imoveis.area_m2 (FLOAT, em metros quadrados)
- "maior que X m²" → WHERE fi.area_m2 > X
- "área média" → AVG(fi.area_m2)
- Para calcular custo-benefício use: fi.preco / fi.area_m2 (menor = melhor)
""",
        """
CUSTO-BENEFÍCIO E CLASSIFICAÇÃO:
- "melhor custo-benefício" = menor preço por m²
  → ORDER BY (fi.preco / fi.area_m2) ASC
- Faixas de preço sugeridas:
  Até R$2.000 = econômico
  R$2.000-R$4.000 = intermediário
  Acima de R$4.000 = alto padrão
- Para classificar use CASE WHEN preco < 2000 THEN 'Econômico' ...
""",
        """
REGRAS DE SQL SQLITE:
- Use ROUND(valor, casas_decimais) para arredondar
- Não existe ILIKE — use LIKE (case-insensitive no SQLite)
- Para concatenar strings use || (ex: dl.bairro || ', ' || dl.uf)
- Funções de data: strftime('%Y-%m', data_extracao)
- Sempre filtre WHERE area_m2 > 0 antes de dividir por area_m2
- LIMIT padrão para listagens: 10 ou 20 itens
""",
    ]
    for rule in business_rules:
        await agent_memory.save_text_memory(content=rule, context=ctx)
    print(f"  ✓ {len(business_rules)} regras injetadas")

    # ── Phase D: golden queries ──────────────────────────────────────────────
    print("Phase D: injetando golden queries...")
    golden = [
        (
            "Qual a média de preço por bairro?",
            """SELECT dl.bairro,
       ROUND(AVG(fi.preco), 2) AS preco_medio,
       COUNT(*) AS qtd_imoveis
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
GROUP BY dl.bairro
ORDER BY preco_medio DESC""",
        ),
        (
            "Total de imóveis cadastrados",
            """SELECT COUNT(*) AS total_imoveis FROM fact_imoveis""",
        ),
        (
            "Quantos imóveis existem por número de quartos?",
            """SELECT fi.quartos,
       COUNT(*) AS total
FROM fact_imoveis fi
GROUP BY fi.quartos
ORDER BY fi.quartos""",
        ),
        (
            "Quais os imóveis mais baratos por metro quadrado?",
            """SELECT fi.titulo,
       dl.bairro,
       fi.preco,
       fi.area_m2,
       ROUND(fi.preco / fi.area_m2, 2) AS preco_por_m2
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
WHERE fi.area_m2 > 0
ORDER BY preco_por_m2 ASC
LIMIT 10""",
        ),
        (
            "Mostre imóveis com 2 quartos até R$ 3000",
            """SELECT fi.titulo,
       dl.bairro,
       fi.preco,
       fi.area_m2,
       fi.quartos
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
WHERE fi.quartos = 2 AND fi.preco <= 3000
ORDER BY fi.preco ASC""",
        ),
        (
            "Qual o preço médio, mínimo e máximo dos imóveis?",
            """SELECT ROUND(AVG(preco), 2) AS preco_medio,
       ROUND(MIN(preco), 2) AS preco_minimo,
       ROUND(MAX(preco), 2) AS preco_maximo
FROM fact_imoveis""",
        ),
        (
            "Quais bairros têm melhor custo-benefício?",
            """SELECT dl.bairro,
       ROUND(AVG(fi.preco / fi.area_m2), 2) AS custo_por_m2,
       COUNT(*) AS qtd_imoveis,
       ROUND(AVG(fi.preco), 2) AS preco_medio
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
WHERE fi.area_m2 > 0
GROUP BY dl.bairro
ORDER BY custo_por_m2 ASC
LIMIT 10""",
        ),
        (
            "Qual imobiliária tem mais imóveis cadastrados?",
            """SELECT di.nome_empresa,
       COUNT(*) AS total_imoveis
FROM fact_imoveis fi
JOIN dim_imobiliarias di ON fi.id_imobiliaria_fk = di.id_imobiliaria
GROUP BY di.nome_empresa
ORDER BY total_imoveis DESC""",
        ),
        (
            "Liste imóveis com garagem ordenados por preço",
            """SELECT fi.titulo,
       dl.bairro,
       fi.preco,
       fi.vagas,
       fi.quartos
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
WHERE fi.vagas > 0
ORDER BY fi.preco ASC""",
        ),
        (
            "Qual a área média dos imóveis por bairro?",
            """SELECT dl.bairro,
       ROUND(AVG(fi.area_m2), 1) AS area_media_m2,
       COUNT(*) AS qtd
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
GROUP BY dl.bairro
ORDER BY area_media_m2 DESC""",
        ),
        (
            "Mostre a distribuição de imóveis por faixa de preço",
            """SELECT
  CASE
    WHEN preco < 2000 THEN 'Até R$2.000'
    WHEN preco < 4000 THEN 'R$2.000 - R$4.000'
    WHEN preco < 7000 THEN 'R$4.000 - R$7.000'
    ELSE 'Acima de R$7.000'
  END AS faixa_preco,
  COUNT(*) AS qtd_imoveis
FROM fact_imoveis
GROUP BY faixa_preco
ORDER BY MIN(preco)""",
        ),
        (
            "Mostre todos os imóveis da Asa Norte",
            """SELECT fi.titulo,
       fi.preco,
       fi.area_m2,
       fi.quartos,
       fi.vagas,
       di.nome_empresa
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
JOIN dim_imobiliarias di ON fi.id_imobiliaria_fk = di.id_imobiliaria
WHERE dl.bairro = 'Asa Norte'
ORDER BY fi.preco ASC""",
        ),
        (
            "Quais são os imóveis com mais banheiros?",
            """SELECT fi.titulo,
       dl.bairro,
       fi.banheiros,
       fi.preco,
       fi.area_m2
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
ORDER BY fi.banheiros DESC
LIMIT 10""",
        ),
        (
            "Mostre imóveis com pelo menos 3 quartos e garagem",
            """SELECT fi.titulo,
       dl.bairro,
       fi.preco,
       fi.quartos,
       fi.vagas,
       fi.area_m2
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
WHERE fi.quartos >= 3 AND fi.vagas > 0
ORDER BY fi.preco ASC""",
        ),
        (
            "Qual o ranking de bairros por número de imóveis disponíveis?",
            """SELECT dl.bairro,
       COUNT(*) AS total_imoveis,
       ROUND(AVG(fi.preco), 2) AS preco_medio
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
GROUP BY dl.bairro
ORDER BY total_imoveis DESC""",
        ),
    ]

    for question, sql in golden:
        await agent_memory.save_tool_usage(
            question=question,
            tool_name="run_sql",
            args={"sql": sql},
            context=ctx,
            success=True,
            metadata={"source": "golden_queries"},
        )
        print(f"  ✓ {question[:65]}")

    print(f"\n✅ Treinamento completo! {len(golden)} queries + DDL + regras no ChromaDB.")


if __name__ == "__main__":
    asyncio.run(main())
