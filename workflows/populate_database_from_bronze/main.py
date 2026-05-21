#!/usr/bin/env python3
"""
RentMaster Bronze to Database Pipeline
Populates SQLite database from Azure Blob Storage (bronze/raw/)
Sends email notification on success/failure
"""

import json
import logging
import os
import sqlite3
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


# ============================================================================
# CONFIGURATION
# ============================================================================

# Azure Storage
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "rentmasterstorageaccount")
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "bronze")
BLOB_PREFIX = os.getenv("BLOB_PREFIX", "raw/")

# Database
DB_PATH = os.getenv("DB_PATH", "./rental.db")

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


# ============================================================================
# DATABASE
# ============================================================================

def create_connection(db_path: str) -> Optional[sqlite3.Connection]:
    """Create SQLite database connection"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        logger.info(f"✅ Connected to database: {db_path}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"❌ Database connection error: {e}")
        return None


def ensure_table_exists(conn: sqlite3.Connection) -> bool:
    """Create imoveis table if not exists"""
    try:
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='imoveis'"
        )
        if cursor.fetchone():
            logger.info("✅ Table 'imoveis' already exists")
            return True
        
        # Create table
        sql = """
        CREATE TABLE imoveis (
            id_hex TEXT PRIMARY KEY,
            titulo TEXT NOT NULL,
            url TEXT,
            preco REAL,
            descricao TEXT,
            quartos INTEGER,
            suites INTEGER,
            vagas INTEGER,
            area_m2 REAL,
            imobiliaria TEXT,
            data_extracao TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(sql)
        conn.commit()
        logger.info("✅ Table 'imoveis' created")
        return True
    
    except sqlite3.Error as e:
        logger.error(f"❌ Failed to create table: {e}")
        return False


def transform_imovel(raw: Dict) -> Optional[Dict]:
    """Transform and validate raw property data"""
    try:
        # Required fields
        if not raw.get("id_hex") or not raw.get("titulo"):
            logger.warning(f"⚠️  Missing required fields in: {raw.get('id_hex', 'unknown')}")
            return None
        
        return {
            "id_hex": raw["id_hex"],
            "titulo": raw["titulo"],
            "url": raw.get("url", ""),
            "preco": parse_preco(raw.get("preco", "")),
            "descricao": raw.get("descricao", "")[:500],  # Max 500 chars
            "quartos": parse_number(raw.get("quartos")),
            "suites": parse_number(raw.get("suites")),
            "vagas": parse_number(raw.get("vagas")),
            "area_m2": parse_area(raw.get("area")),
            "imobiliaria": raw.get("imobiliaria", ""),
            "data_extracao": raw.get("data_extracao", ""),
        }
    except Exception as e:
        logger.error(f"❌ Error transforming property: {e}")
        return None


def load_into_db(conn: sqlite3.Connection, imovel: Dict) -> bool:
    """
    Insert or update (UPSERT) property into database
    Uses INSERT OR REPLACE to avoid duplicates
    """
    try:
        cursor = conn.cursor()
        
        sql = """
        INSERT OR REPLACE INTO imoveis (
            id_hex, titulo, url, preco, descricao, quartos, suites, vagas,
            area_m2, imobiliaria, data_extracao, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        cursor.execute(sql, (
            imovel["id_hex"],
            imovel["titulo"],
            imovel["url"],
            imovel["preco"],
            imovel["descricao"],
            imovel["quartos"],
            imovel["suites"],
            imovel["vagas"],
            imovel["area_m2"],
            imovel["imobiliaria"],
            imovel["data_extracao"],
        ))
        
        return True
    except sqlite3.Error as e:
        logger.error(f"❌ Database insert error for {imovel.get('id_hex')}: {e}")
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
    1. Connect to Azure Storage
    2. List JSON blobs
    3. Load into SQLite
    4. Send email notification
    """
    try:
        logger.info("=" * 70)
        logger.info("🚀 Starting Bronze to Database Pipeline")
        logger.info("=" * 70)
        
        # Initialize database
        conn = create_connection(DB_PATH)
        if not conn:
            raise Exception("Failed to connect to database")
        
        if not ensure_table_exists(conn):
            raise Exception("Failed to create table")
        
        # List blobs
        blob_names = list_json_blobs()
        if not blob_names:
            logger.warning("⚠️  No JSON files found in bronze/raw/")
            message = "No JSON files found in bronze/raw/"
            return False, message
        
        # Process each blob
        inserted = 0
        updated = 0
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
                transformed = transform_imovel(raw_imovel)
                if not transformed:
                    failed += 1
                    continue
                
                if load_into_db(conn, transformed):
                    inserted += 1
                else:
                    failed += 1
        
        # Commit changes
        conn.commit()
        
        # Get final count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM imoveis")
        total = cursor.fetchone()["total"]
        conn.close()
        
        # Summary
        message = f"""
Workflow: Populate Database from Bronze
Status: ✅ SUCCESS

Statistics:
  Total Properties Processed: {len(blob_names)} files
  Successfully Inserted: {inserted}
  Failed: {failed}
  Database Total Records: {total}

Configuration:
  Storage Account: {STORAGE_ACCOUNT_NAME}
  Container: {CONTAINER_NAME}
  Database: {DB_PATH}
  
Timestamp: {datetime.now().isoformat()}
"""
        
        logger.info("=" * 70)
        logger.info("✅ Pipeline completed successfully!")
        logger.info("=" * 70)
        
        return True, message
    
    except Exception as e:
        error_message = f"""
Workflow: Populate Database from Bronze
Status: ❌ FAILED

Error Details:
{str(e)}

Configuration:
  Storage Account: {STORAGE_ACCOUNT_NAME}
  Container: {CONTAINER_NAME}
  Database: {DB_PATH}
  
Timestamp: {datetime.now().isoformat()}
"""
        logger.error(f"❌ Pipeline failed: {e}")
        return False, error_message


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
