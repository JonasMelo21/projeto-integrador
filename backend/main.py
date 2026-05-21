"""FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database setup
from database import init_db, SessionLocal

# Import routes
from routes import imoveis, dimensoes

# Initialize database and load data if empty
def startup_db():
    """Initialize database and load ADLS data if empty"""
    init_db()
    
    # Check if database is empty
    from models import FactImovel
    db = SessionLocal()
    try:
        count = db.query(FactImovel).count()
        if count == 0:
            print("📥 Database is empty, attempting to load from ADLS...")
            print("⏳ This may take a few minutes...")
            try:
                import subprocess
                import tempfile
                
                # Create temporary directory for downloads
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Use the new Azure CLI script
                    result = subprocess.run(
                        ["bash", "scripts/load_from_adls_cli.sh"],
                        capture_output=True,
                        text=True,
                        timeout=600,  # 10 minutes timeout
                        env={**os.environ, "TEMP_DIR": temp_dir}
                    )
                    
                    if result.returncode == 0:
                        print("✅ ADLS data loaded successfully")
                        # Refresh count
                        db.close()
                        db = SessionLocal()
                        count = db.query(FactImovel).count()
                        print(f"✅ Database now has {count} imóveis")
                    else:
                        print(f"⚠️ ADLS load failed: {result.stderr}")
            except Exception as e:
                print(f"⚠️ Could not load ADLS data: {e}")
                print("💡 Run manually: bash scripts/load_from_adls_cli.sh")
        else:
            print(f"✅ Database ready with {count} imóveis")
    finally:
        db.close()

# Initialize database at startup
startup_db()

# Create FastAPI app
app = FastAPI(
    title="RentMaster Backend",
    description="Local dev API for rental properties",
    version="0.1.0"
)

# CORS configuration - MUST be added BEFORE routes
cors_options = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["*"],
}

app.add_middleware(CORSMiddleware, **cors_options)

# Include routers
app.include_router(imoveis.router, prefix="/api", tags=["imoveis"])
app.include_router(dimensoes.router, prefix="/api", tags=["dimensoes"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "RentMaster Backend running", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}
