"""FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database setup referenciando a pasta backend
from backend.database import init_db, SessionLocal
from backend.models import FactImovel
from backend.routes import imoveis, dimensoes
from backend.ai.vanna_agent import server as vanna_server


def startup_db():
    """Initialize database"""
    init_db()

    db = SessionLocal()
    try:
        count = db.query(FactImovel).count()
        if count == 0:
            print("⚠️  Database is empty. Run: uv run python backend/scripts/load_json_to_sqlite.py")
        else:
            print(f"✅ Database ready with {count} imóveis")
    finally:
        db.close()


startup_db()

# Create FastAPI app
app = FastAPI(
    title="RentMaster Backend",
    description="API for rental properties + Vanna AI Text-to-SQL",
    version="0.2.0",
)

# CORS — must be before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Named routes first
app.include_router(imoveis.router, prefix="/api", tags=["imoveis"])
app.include_router(dimensoes.router, prefix="/api", tags=["dimensoes"])


@app.get("/health")
async def health():
    return {"status": "ok"}

app.mount("/", vanna_server.create_app())
