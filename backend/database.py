"""Database setup and session management"""
import os
from pathlib import Path 
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

# Descobre o caminho absoluto da pasta 'backend' onde este arquivo database.py está
BASE_DIR = Path(__file__).parent.resolve()

# Tenta ler a variável de ambiente primeiro (usado pelo Docker). 
# Se não achar (script rodando local), força o caminho absoluto para backend/rental.db
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR}/rental.db")


# Engine with StaticPool for SQLite (needed for threading)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM base
Base = declarative_base()


def get_db():
    """Dependency for FastAPI to inject DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
