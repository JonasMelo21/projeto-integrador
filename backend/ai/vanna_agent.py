"""Vanna.AI Text-to-SQL Agent — core assembly for RentMaster"""
import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.servers.fastapi import VannaFastAPIServer
from vanna.integrations.google import GeminiLlmService
from vanna.integrations.sqlite import SqliteRunner
from vanna.integrations.chromadb import ChromaAgentMemory
from vanna.tools import RunSqlTool
from vanna.core.user.resolver import UserResolver
from vanna.core.user.models import User
from vanna.core.user.request_context import RequestContext
from vanna.core.system_prompt.default import DefaultSystemPromptBuilder

# --- Resolved paths ---
_AI_DIR = Path(__file__).parent

# Extrai o caminho do banco de dados da variável de ambiente (criada pelo Docker/env)
db_url_env = os.environ.get("DATABASE_URL")
if db_url_env and db_url_env.startswith("sqlite:///"):
    # Remove o prefixo 'sqlite:///' para obter o caminho real do arquivo
    db_path_str = db_url_env.replace("sqlite:///", "")
    DATABASE_PATH = Path(db_path_str).resolve()
else:
    # Fallback para desenvolvimento local caso a env var falhe:
    # Volta duas pastas a partir deste arquivo para achar a raiz do backend e procura o rental.db
    _BACKEND_ROOT = _AI_DIR.parent
    DATABASE_PATH = _BACKEND_ROOT / "rental.db"

CHROMA_DIR = _AI_DIR / "chroma_db"

# --- Google Gemini LLM ---
_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI-API-KEY")
if not _api_key:
    raise RuntimeError("Set GEMINI_API_KEY or GEMINI-API-KEY in .env")

llm = GeminiLlmService(
    model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
    api_key=_api_key,
)

# --- SQLite runner + tool ---
db_runner = SqliteRunner(database_path=str(DATABASE_PATH))
db_tool = RunSqlTool(sql_runner=db_runner)

# --- Tool registry ---
tools = ToolRegistry()
tools.register_local_tool(db_tool, access_groups=[])

# --- ChromaDB vector memory ---
agent_memory = ChromaAgentMemory(
    collection_name="rentmaster_memory",
    persist_directory=str(CHROMA_DIR),
)

# --- System prompt com schema embutido ---
_SYSTEM_PROMPT = """
Você é um assistente especializado em análise de imóveis para aluguel em Brasília, DF.
Você tem acesso a uma ferramenta SQL (run_sql) para consultar o banco de dados.

==============================================================
SCHEMA DO BANCO DE DADOS (SQLite) — USE EXATAMENTE ESTES NOMES
==============================================================

TABELA FATO — imóveis anunciados:
  fact_imoveis (
    id_imovel          INTEGER  PRIMARY KEY,
    id_imobiliaria_fk  INTEGER  → dim_imobiliarias.id_imobiliaria,
    id_local_fk        INTEGER  → dim_locais.id_local,
    titulo             VARCHAR  — título do anúncio,
    url                VARCHAR  — link original,
    preco              FLOAT    — aluguel mensal em R$,
    area_m2            FLOAT    — área em metros quadrados,
    quartos            INTEGER  — número de quartos,
    banheiros          INTEGER  — número de banheiros/suítes,
    vagas              INTEGER  — vagas de garagem,
    imagem             VARCHAR,
    descricao          VARCHAR,
    data_extracao      DATETIME
  )

DIMENSÃO LOCALIZAÇÃO:
  dim_locais (
    id_local  INTEGER PRIMARY KEY,
    bairro    VARCHAR — valores: 'Asa Norte', 'Asa Sul', 'Sudoeste', 'Noroeste',
                        'Lago Sul', 'Park Way', 'Taguatinga', 'Setor Industrial',
                        'Vicente Pires',
    cidade    VARCHAR — sempre 'BRASILIA',
    uf        VARCHAR — sempre 'DF'
  )

DIMENSÃO IMOBILIÁRIA:
  dim_imobiliarias (
    id_imobiliaria  INTEGER PRIMARY KEY,
    nome_empresa    VARCHAR — nome da imobiliária
  )

==============================================================
JOINS PADRÃO (use sempre que precisar de bairro ou imobiliária):
  JOIN dim_locais dl ON fi.id_local_fk = dl.id_local
  JOIN dim_imobiliarias di ON fi.id_imobiliaria_fk = di.id_imobiliaria

REGRAS DE SQL SQLITE:
- Arredondar: ROUND(valor, 2)
- Não existe ILIKE — use LIKE
- Dividir por area_m2: sempre filtre WHERE area_m2 > 0 antes
- Limite padrão para listagens: LIMIT 20
- NÃO existem tabelas chamadas: properties, imoveis, apartments, listings, rental
==============================================================
"""

_prompt_builder = DefaultSystemPromptBuilder(base_prompt=_SYSTEM_PROMPT)

# --- User resolver ---
class _LocalUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        return User(id="system", username="RentMaster Local")


user_resolver = _LocalUserResolver()

# --- Agent ---
agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    user_resolver=user_resolver,
    agent_memory=agent_memory,
    system_prompt_builder=_prompt_builder,
)

# --- Vanna FastAPI server ---
# Use server.create_app() — not server.app
server = VannaFastAPIServer(agent)