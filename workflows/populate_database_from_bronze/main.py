#!/usr/bin/env python3
"""
RentMaster Bronze to Database Pipeline
Populates Azure SQL Serverless database from Azure Blob Storage (bronze/raw/)
Sends email notification on success/failure
"""

import json
import logging
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Tuple

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError


# ============================================================================
# CONFIGURATION
# ============================================================================

# Azure Storage
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "rentmasterstorageaccount")
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "bronze")
BLOB_PREFIX = os.getenv("BLOB_PREFIX", "raw/")

# Database - SQL Server connection string
DB_CONNECTION_STRING = os.getenv(
    "DB_CONNECTION_STRING",
    "mssql+pyodbc://user:password@server.database.windows.net:1433/rentmaster_db?driver=ODBC+Driver+17+for+SQL+Server"
)

# Email
EMAIL_FROM = os.getenv("EMAIL_FROM", "python_pipeline@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # App Password
EMAIL_TO = os.getenv("EMAIL_TO", "jonashonorato4@gmail.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# ============================================================================
# LOGGING
# ============================================================================

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup structured logging"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger("bronze_pipeline")
    logger.setLevel(log_level)
    logger.addHandler(handler)
    
    return logger


logger = setup_logging(LOG_LEVEL)


# ============================================================================
# SQLALCHEMY DATABASE SETUP
# ============================================================================

Base = declarative_base()


class FactImovel(Base):
    """Imovel/Property Fact Table"""
    __tablename__ = "FactImovel"

    id = Column(Integer, primary_key=True)
    id_hex = Column(String(64), unique=True, nullable=False, index=True)  # SHA256 hash of URL
    url = Column(String(500), nullable=False)
    titulo = Column(String(255), nullable=True)
    preco = Column(Float, nullable=True)
    area_m2 = Column(Float, nullable=True)
    quartos = Column(Integer, nullable=True)
    banheiros = Column(Integer, nullable=True)
    vagas = Column(Integer, nullable=True)
    endereco = Column(String(500), nullable=True)
    id_imobiliaria = Column(Integer, nullable=True)
    id_local = Column(Integer, nullable=True)
    data_extracao = Column(DateTime, nullable=False)


def get_db_engine():
    """Create SQLAlchemy engine for SQL Server"""
    try:
        engine = create_engine(
            DB_CONNECTION_STRING,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False,
        )
        logger.info(f"✅ Connected to database: {DB_CONNECTION_STRING[:50]}...")
        return engine
    except Exception as e:
        logger.error(f"❌ Failed to create database engine: {e}")
        raise


def ensure_database_ready(engine) -> bool:
    """Ensure database schema exists"""
    try:
        Base.metadata.create_all(engine)
        logger.info("✅ Database schema verified/created")
        return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Failed to create schema: {e}")
        return False


# ============================================================================
# AZURE STORAGE
# ============================================================================

def get_blob_client() -> BlobServiceClient:
    """
    Connect to Azure Blob Storage using Managed Identity (production)
    or DefaultAzureCredential (local development with az cli)
    """
    try:
        credential = DefaultAzureCredential()
        account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        client = BlobServiceClient(account_url=account_url, credential=credential)
        logger.info(f"✅ Connected to Storage Account: {STORAGE_ACCOUNT_NAME}")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to connect to Storage: {e}")
        raise


def list_json_blobs() -> List[str]:
    """
    List all JSON files in bronze/raw/ container
    Returns list of blob names
    """
    try:
        client = get_blob_client()
        container_client = client.get_container_client(CONTAINER_NAME)
        
        blobs = []
        for blob in container_client.list_blobs(name_starts_with=BLOB_PREFIX):
            if blob.name.endswith(".json"):
                blobs.append(blob.name)
        
        logger.info(f"📋 Found {len(blobs)} JSON files in {CONTAINER_NAME}/{BLOB_PREFIX}")
        return blobs
    except Exception as e:
        logger.error(f"❌ Failed to list blobs: {e}")
        raise


def download_blob_content(blob_name: str) -> Optional[str]:
    """Download blob content as string"""
    try:
        client = get_blob_client()
        blob_client = client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
        content = blob_client.download_blob().readall().decode("utf-8")
        return content
    except Exception as e:
        logger.error(f"❌ Failed to download {blob_name}: {e}")
        return None


# ============================================================================
# DATA PARSING
# ============================================================================

def parse_preco(preco_str: str) -> Optional[float]:
    """Convert price string ' 10.900' -> 10900.0"""
    try:
        if not preco_str:
            return None
        # Remove spaces and 'R$'
        cleaned = preco_str.strip().replace("R$", "").strip()
        # Replace . with empty (thousands separator) and , with . (decimal)
        cleaned = cleaned.replace(".", "").replace(",", ".")
        return float(cleaned)
    except (ValueError, AttributeError):
        logger.warning(f"⚠️  Invalid price: {preco_str}")
        return None


def parse_number(text: str) -> Optional[int]:
    """Extract number from text: '3 Quartos' -> 3"""
    try:
        import re
        if not text:
            return None
        match = re.search(r"\d+", str(text))
        return int(match.group()) if match else None
    except (ValueError, AttributeError):
        logger.warning(f"⚠️  Invalid number in text: {text}")
        return None


def parse_area(area_str: str) -> Optional[float]:
    """Convert area string '151 m²' -> 151.0"""
    try:
        if not area_str:
            return None
        import re
        match = re.search(r"[\d.]+", str(area_str))
        if match:
            value = match.group().replace(".", "").replace(",", ".")
            return float(value)
        return None
    except (ValueError, AttributeError):
        logger.warning(f"⚠️  Invalid area: {area_str}")
        return None


def transform_imovel(raw: Dict, db_session: Session) -> Optional[FactImovel]:
    """Transform and validate raw property data into ORM object"""
    try:
        # Required fields
        if not raw.get("id_hex") or not raw.get("titulo"):
            logger.warning(f"⚠️  Missing required fields in: {raw.get('id_hex', 'unknown')}")
            return None
        
        # Parse data_extracao if it's a string, otherwise use as-is
        data_extracao = raw.get("data_extracao")
        if isinstance(data_extracao, str):
            try:
                from datetime import datetime as dt
                data_extracao = dt.fromisoformat(data_extracao)
            except (ValueError, TypeError):
                data_extracao = datetime.now()
        elif data_extracao is None:
            data_extracao = datetime.now()
        
        # Create ORM object
        imovel = FactImovel(
            id_hex=raw["id_hex"],
            url=raw.get("url", ""),
            titulo=raw["titulo"],
            preco=parse_preco(raw.get("preco", "")),
            area_m2=parse_area(raw.get("area")),
            quartos=parse_number(raw.get("quartos")),
            banheiros=parse_number(raw.get("banheiros")),
            vagas=parse_number(raw.get("vagas")),
            endereco=raw.get("endereco", "")[:500],
            id_imobiliaria=None,  # Will be populated by dimension lookup if needed
            id_local=None,  # Will be populated by dimension lookup if needed
            data_extracao=data_extracao,
        )
        
        return imovel
    except Exception as e:
        logger.error(f"❌ Error transforming property: {e}")
        return None


def load_into_db(db_session: Session, imovel: FactImovel) -> bool:
    """
    Insert or update (UPSERT) property into database
    Uses SQLAlchemy merge for upsert on id_hex
    """
    try:
        # Merge will insert or update based on primary key
        db_session.merge(imovel)
        return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Database insert error for {imovel.id_hex}: {e}")
        db_session.rollback()
        return False


# ============================================================================
# EMAIL
# ============================================================================

def send_email(subject: str, body: str, success: bool = True) -> bool:
    """Send email notification"""
    try:
        if not EMAIL_PASSWORD:
            logger.warning("⚠️  EMAIL_PASSWORD not set. Skipping email notification.")
            return False
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        
        # HTML body
        status_color = "green" if success else "red"
        status_icon = "✅" if success else "❌"
        
        html = f"""
        <html>
            <head></head>
            <body style="font-family: Arial, sans-serif;">
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px;">
                    <h2 style="color: {status_color};">{status_icon} {subject}</h2>
                    <pre style="background-color: white; padding: 15px; border-radius: 3px; overflow-x: auto;">
{body}
                    </pre>
                    <p style="color: #666; font-size: 12px;">
                        Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, "html"))
        
        # Send
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Email sent to {EMAIL_TO}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        return False


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_pipeline() -> Tuple[bool, str]:
    """
    Main ETL pipeline:
    1. Connect to Azure SQL Serverless via SQLAlchemy
    2. List JSON blobs from Azure Blob Storage
    3. Transform and load data into database
    4. Send email notification
    """
    engine = None
    db_session = None
    
    try:
        logger.info("=" * 70)
        logger.info("🚀 Starting Bronze to Database Pipeline (SQL Server)")
        logger.info("=" * 70)
        
        # Initialize database
        engine = get_db_engine()
        if not ensure_database_ready(engine):
            raise Exception("Failed to prepare database schema")
        
        # Create session factory
        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()
        
        # List blobs
        blob_names = list_json_blobs()
        if not blob_names:
            logger.warning("⚠️  No JSON files found in bronze/raw/")
            message = "No JSON files found in bronze/raw/"
            return False, message
        
        # Process each blob
        inserted = 0
        failed = 0
        
        for blob_name in blob_names:
            logger.info(f"📥 Processing: {blob_name}")
            
            # Download content
            content = download_blob_content(blob_name)
            if not content:
                failed += 1
                continue
            
            # Parse JSON
            try:
                data = json.loads(content)
                if not isinstance(data, list):
                    data = [data]
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON in {blob_name}: {e}")
                failed += 1
                continue
            
            # Process each property
            for raw_imovel in data:
                transformed = transform_imovel(raw_imovel, db_session)
                if not transformed:
                    failed += 1
                    continue
                
                if load_into_db(db_session, transformed):
                    inserted += 1
                else:
                    failed += 1
        
        # Commit all changes
        db_session.commit()
        
        # Get final count
        total = db_session.query(FactImovel).count()
        
        # Summary
        message = f"""
Workflow: Populate Database from Bronze
Status: ✅ SUCCESS

Statistics:
  Total Files Processed: {len(blob_names)}
  Successfully Inserted/Updated: {inserted}
  Failed: {failed}
  Database Total Records: {total}

Configuration:
  Storage Account: {STORAGE_ACCOUNT_NAME}
  Container: {CONTAINER_NAME}
  Database: Azure SQL Serverless
  
Timestamp: {datetime.now().isoformat()}
"""
        
        logger.info("=" * 70)
        logger.info("✅ Pipeline completed successfully!")
        logger.info("=" * 70)
        
        return True, message
    
    except Exception as e:
        if db_session:
            db_session.rollback()
        
        error_message = f"""
Workflow: Populate Database from Bronze
Status: ❌ FAILED

Error Details:
{str(e)}

Configuration:
  Storage Account: {STORAGE_ACCOUNT_NAME}
  Container: {CONTAINER_NAME}
  Database: Azure SQL Serverless
  
Timestamp: {datetime.now().isoformat()}
"""
        logger.error(f"❌ Pipeline failed: {e}")
        return False, error_message
    
    finally:
        # Cleanup
        if db_session:
            db_session.close()
        if engine:
            engine.dispose()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    success, message = run_pipeline()
    
    # Send email
    subject = "✅ Database Population Success" if success else "❌ Database Population Failed"
    send_email(subject, message, success)
    
    # Exit code
    exit(0 if success else 1)
