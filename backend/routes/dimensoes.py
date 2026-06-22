"""Dimensões (Dimensions) API Routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import DimImobiliaria, DimLocal
from ..schemas import DimImobiliariaSchema, DimLocalSchema
from typing import List

router = APIRouter()


@router.get("/dimensoes/imobiliarias", response_model=List[DimImobiliariaSchema])
async def list_imobiliarias(db: Session = Depends(get_db)):
    """List all real estate companies"""
    imobiliarias = db.query(DimImobiliaria).all()
    return imobiliarias


@router.get("/dimensoes/locais", response_model=List[DimLocalSchema])
async def list_locais(db: Session = Depends(get_db)):
    """List all locations (neighborhoods)"""
    locais = db.query(DimLocal).all()
    return locais


@router.get("/dimensoes/locais/cidade/{cidade}", response_model=List[DimLocalSchema])
async def locais_by_cidade(
    cidade: str,
    db: Session = Depends(get_db)
):
    """Get locations by city"""
    locais = db.query(DimLocal).filter(
        DimLocal.cidade.ilike(f"%{cidade}%")
    ).all()
    return locais
