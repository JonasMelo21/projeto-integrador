"""Database setup and session management"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

# Database URL - supports both SQLite (local) and SQL Server (Azure)
# For SQLite: DATABASE_URL="sqlite:///./rental.db"
# For SQL Server: DATABASE_URL="mssql+pyodbc://user:pass@server.database.windows.net:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./rental.db"  # Default to local SQLite for backward compatibility
)

# Engine configuration based on database type
if "sqlite" in DATABASE_URL:
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
        pool_pre_ping=True,  # Verify connections before using
        echo=False,  # Set to True for SQL debugging
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
