"""
Vanna training script — run once to populate ChromaDB with DDL, business rules
and golden queries for the RentMaster star schema.

Usage:
    PYTHONPATH=. uv run python backend/ai/train_vanna.py
"""
import asyncio
import sqlite3
import uuid
from pathlib import Path

from backend.ai.vanna_agent import agent_memory, DATABASE_PATH
from vanna.core.tool.models import ToolContext
from vanna.core.user.models import User

_PROJECT_ROOT = Path(__file__).parent.parent.parent


async def main():
    ctx = ToolContext(
        user=User(id="training", username="training"),
        conversation_id="training",
        request_id=str(uuid.uuid4()),
        agent_memory=agent_memory,
    )

    # ── Phase A: DDL from SQLite schema ─────────────────────────────────────
    print("Phase A: injecting DDL...")
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL"
    )
    for table_name, ddl in cursor.fetchall():
        await agent_memory.save_text_memory(content=ddl, context=ctx)
        print(f"  ✓ {table_name}")
    conn.close()

    # ── Phase B: business context ────────────────────────────────────────────
    print("Phase B: injecting business rules...")
    business_rules = [
        "O banco de dados contém imóveis para aluguel em Brasília, DF, Brasil.",
        "A tabela principal é fact_imoveis, que contém preco (aluguel mensal em R$), area_m2, quartos, banheiros (suítes), vagas de garagem.",
        "dim_locais contém bairro, cidade (sempre 'BRASILIA') e uf (sempre 'DF').",
        "dim_imobiliarias contém nome_empresa (nome da imobiliária).",
        "fact_imoveis.id_local_fk referencia dim_locais.id_local.",
        "fact_imoveis.id_imobiliaria_fk referencia dim_imobiliarias.id_imobiliaria.",
        "Classificação por custo: use NTILE(100) OVER (ORDER BY preco/area_m2) para percentil. >= p90 = 'Alto Padrão', >= p75 = 'Caro', p25-p74 = 'Médio', < p25 = 'Barato'.",
        "Para calcular preço por m², use preco / area_m2.",
        "Sempre use JOIN com dim_locais e dim_imobiliarias para mostrar nomes amigáveis ao usuário.",
        "Quando o usuário perguntar sobre 'bairros mais baratos' ou 'custo-benefício', ordene por AVG(preco/area_m2) ASC.",
    ]
    for rule in business_rules:
        await agent_memory.save_text_memory(content=rule, context=ctx)
        print(f"  ✓ {rule[:60]}...")

    # ── Phase C: golden queries ──────────────────────────────────────────────
    print("Phase C: injecting golden queries...")
    golden = [
        (
            "Qual a média de preço por bairro?",
            """
SELECT dl.bairro, ROUND(AVG(fi.preco), 2) AS preco_medio, COUNT(*) AS qtd_imoveis
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
GROUP BY dl.bairro
ORDER BY preco_medio DESC
""",
        ),
        (
            "Quais os imóveis mais baratos por metro quadrado?",
            """
SELECT fi.titulo, dl.bairro, fi.preco, fi.area_m2,
       ROUND(fi.preco / fi.area_m2, 2) AS preco_por_m2
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
WHERE fi.area_m2 > 0
ORDER BY preco_por_m2 ASC
LIMIT 10
""",
        ),
        (
            "Quantos imóveis existem por número de quartos?",
            """
SELECT quartos, COUNT(*) AS total
FROM fact_imoveis
GROUP BY quartos
ORDER BY quartos
""",
        ),
        (
            "Qual a imobiliária com mais imóveis cadastrados?",
            """
SELECT di.nome_empresa, COUNT(*) AS total_imoveis
FROM fact_imoveis fi
JOIN dim_imobiliarias di ON fi.id_imobiliaria_fk = di.id_imobiliaria
GROUP BY di.nome_empresa
ORDER BY total_imoveis DESC
""",
        ),
        (
            "Mostre imóveis com 2 quartos até R$ 3000",
            """
SELECT fi.titulo, dl.bairro, fi.preco, fi.area_m2, fi.quartos
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
WHERE fi.quartos = 2 AND fi.preco <= 3000
ORDER BY fi.preco ASC
""",
        ),
        (
            "Qual o preço médio geral dos imóveis?",
            """
SELECT ROUND(AVG(preco), 2) AS preco_medio_geral,
       ROUND(MIN(preco), 2) AS preco_minimo,
       ROUND(MAX(preco), 2) AS preco_maximo
FROM fact_imoveis
""",
        ),
        (
            "Quais bairros têm imóveis com melhor custo-benefício (menor preço por m²)?",
            """
SELECT dl.bairro,
       ROUND(AVG(fi.preco / fi.area_m2), 2) AS custo_por_m2,
       COUNT(*) AS qtd_imoveis,
       ROUND(AVG(fi.preco), 2) AS preco_medio
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
WHERE fi.area_m2 > 0
GROUP BY dl.bairro
ORDER BY custo_por_m2 ASC
LIMIT 10
""",
        ),
        (
            "Liste imóveis com vagas de garagem ordenados por preço",
            """
SELECT fi.titulo, dl.bairro, fi.preco, fi.vagas, fi.quartos
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
WHERE fi.vagas > 0
ORDER BY fi.preco ASC
""",
        ),
        (
            "Qual a área média dos imóveis por bairro?",
            """
SELECT dl.bairro, ROUND(AVG(fi.area_m2), 1) AS area_media_m2, COUNT(*) AS qtd
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
GROUP BY dl.bairro
ORDER BY area_media_m2 DESC
""",
        ),
        (
            "Mostre a distribuição de preços por faixa",
            """
SELECT
  CASE
    WHEN preco < 1500 THEN 'Até R$1.500'
    WHEN preco < 2500 THEN 'R$1.500 - R$2.500'
    WHEN preco < 4000 THEN 'R$2.500 - R$4.000'
    ELSE 'Acima de R$4.000'
  END AS faixa_preco,
  COUNT(*) AS qtd_imoveis
FROM fact_imoveis
GROUP BY faixa_preco
ORDER BY MIN(preco)
""",
        ),
        (
            "Quais imóveis têm mais banheiros?",
            """
SELECT fi.titulo, dl.bairro, fi.banheiros, fi.preco, fi.area_m2
FROM fact_imoveis fi
JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
ORDER BY fi.banheiros DESC
LIMIT 10
""",
        ),
        (
            "Total de imóveis cadastrados",
            """
SELECT COUNT(*) AS total_imoveis FROM fact_imoveis
""",
        ),
    ]

    for question, sql in golden:
        await agent_memory.save_tool_usage(
            question=question,
            tool_name="run_sql",
            args={"sql": sql.strip()},
            context=ctx,
            success=True,
            metadata={"source": "golden_queries"},
        )
        print(f"  ✓ {question[:60]}")

    print("\n✅ Training complete! ChromaDB populated.")


if __name__ == "__main__":
    asyncio.run(main())
