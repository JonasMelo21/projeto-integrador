"""Database setup and session management"""
import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

# Database URL - supports Azure SQL Serverless or local SQLite for fallback
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DB_SERVER = os.getenv("DB_SERVER", "").strip()
DB_NAME = os.getenv("DB_NAME", "").strip()
DB_USER = os.getenv("DB_USER", "").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD", "").strip()
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server").strip()

# Build a SQL Server connection string from individual environment variables
def build_sqlserver_url() -> str:
    """Build the SQLAlchemy URL for Azure SQL Serverless."""
    if not (DB_SERVER and DB_NAME and DB_USER and DB_PASSWORD):
        return ""

    odbc_conn = (
        f"DRIVER={DB_DRIVER};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Authentication=SqlPassword"
    )
    return f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(odbc_conn)}"

if not DATABASE_URL:
    DATABASE_URL = build_sqlserver_url()

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is required. Set DATABASE_URL or DB_SERVER/DB_NAME/DB_USER/DB_PASSWORD."
    )

# Engine configuration based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite config with StaticPool for threading
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # SQL Server config with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False,
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
