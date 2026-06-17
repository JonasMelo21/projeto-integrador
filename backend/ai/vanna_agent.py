"""Vanna.AI Text-to-SQL Agent — core assembly for RentMaster"""
import os
from pathlib import Path

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

# --- Resolved paths ---
_AI_DIR = Path(__file__).parent
_PROJECT_ROOT = _AI_DIR.parent.parent

DATABASE_PATH = _PROJECT_ROOT / "data" / "rental.db"
CHROMA_DIR = _AI_DIR / "chroma_db"

# --- Google Gemini LLM ---
# Vanna 2.x uses GEMINI_API_KEY (no hyphen). The .env has GEMINI-API-KEY,
# so we read it explicitly and pass as api_key.
_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI-API-KEY")
if not _api_key:
    raise RuntimeError("Set GEMINI_API_KEY or GEMINI-API-KEY in .env")

llm = GeminiLlmService(
    model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
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


# --- User resolver (generic system user for local dev) ---
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
)

# --- Vanna FastAPI server ---
# Use server.create_app() — not server.app
server = VannaFastAPIServer(agent)
