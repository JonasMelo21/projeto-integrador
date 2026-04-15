"""FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import database setup
from database import init_db

# Import routes
from routes import imoveis, dimensoes

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="RentMaster Backend",
    description="Local dev API for rental properties",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
