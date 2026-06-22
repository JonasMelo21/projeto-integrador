"""Database setup and session management"""
import os
from pathlib import Path 
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

# Volta duas pastas a partir de backend/database.py para achar a raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"

# Garante que a pasta 'data' exista, evitando erros se ela for deletada
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Tenta ler a variável de ambiente primeiro (usado pelo Docker). 
# Se não achar (script rodando local), força o caminho absoluto para data/rental.db
DEFAULT_DB_PATH = f"sqlite:///{DATA_DIR}/rental.db"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DB_PATH)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)