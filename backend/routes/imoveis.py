"""Imóveis (Properties) API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import FactImovel, DimImobiliaria, DimLocal
from backend.schemas import FactImovelSchema, FactImovelListSchema
from typing import List

router = APIRouter()


@router.get("/imoveis", response_model=List[FactImovelListSchema])
async def list_imoveis(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all properties with pagination"""
    imoveis = db.query(
        FactImovel.id_imovel,
        FactImovel.titulo,
        FactImovel.preco,
        FactImovel.area_m2,
        FactImovel.imagem,
        FactImovel.quartos,
        DimImobiliaria.nome_empresa.label("imobiliaria_nome"),
        DimLocal.bairro.label("local_bairro"),
    ).join(
        DimImobiliaria, FactImovel.id_imobiliaria_fk == DimImobiliaria.id_imobiliaria
    ).join(
        DimLocal, FactImovel.id_local_fk == DimLocal.id_local
    ).offset(skip).limit(limit).all()
    
    return [dict(row._mapping) for row in imoveis]


@router.get("/imoveis/stats")
async def imoveis_stats(db: Session = Depends(get_db)):
    """Get statistics about properties"""
    total = db.query(FactImovel).count()
    avg_preco = db.query(
        func.avg(FactImovel.preco)
    ).scalar() or 0
    avg_area = db.query(
        func.avg(FactImovel.area_m2)
    ).scalar() or 0
    
    return {
        "total_imoveis": total,
        "preco_medio": round(avg_preco, 2),
        "area_media_m2": round(avg_area, 2)
    }


@router.get("/imoveis/{id_imovel}", response_model=FactImovelSchema)
async def get_imovel(
    id_imovel: int,
    db: Session = Depends(get_db)
):
    """Get property details by ID"""
    imovel = db.query(FactImovel).filter(
        FactImovel.id_imovel == id_imovel
    ).first()
    
    if not imovel:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return imovel


@router.get("/imoveis/by-hex/{id_hex}", response_model=FactImovelSchema)
async def get_imovel_by_hex(
    id_hex: str,
    db: Session = Depends(get_db)
):
    """Get property by hex ID (business key from scraper)"""
    imovel = db.query(FactImovel).filter(
        FactImovel.id_hex == id_hex
    ).first()
    
    if not imovel:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return imovel
