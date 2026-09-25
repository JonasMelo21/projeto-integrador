"""Imóveis (Properties) API Routes"""
import hashlib
import joblib
import pandas as pd
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import FactImovel, DimImobiliaria, DimLocal
from backend.schemas import FactImovelSchema, FactImovelListSchema
from typing import List
from data_pipeline.medallion.bronze_to_silver import extract_tipo_imovel

router = APIRouter()

# ==========================================
# MACHINE LEARNING INFERENCE SETUP
# ==========================================
PROJECT_ROOT = Path(__file__).parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "ml_pipeline" / "models" / "random_forest_optimized.joblib"
STATS_PATH = PROJECT_ROOT / "data" / "gold" / "dim_bairros_estatisticas.parquet"

# Carrega o modelo na memória global da API
try:
    rf_model = joblib.load(MODEL_PATH)
    print(f"🤖 Modelo ML carregado com sucesso: {MODEL_PATH.name}")
except Exception as e:
    print(f"⚠️ Aviso: Modelo de ML não encontrado. As classificações serão nulas. Erro: {e}")
    rf_model = None

try:
    area_statistics = pd.read_parquet(STATS_PATH)
except Exception:
    area_statistics = pd.DataFrame()

# Mapeamento de saída do modelo
PRICE_CLASSES = {0: "Barato", 1: "Preço Justo", 2: "Caro"}

def predict_classificacao(imovel_dict: dict) -> str | None:
    """Aplica as transformações e faz a inferência do modelo em tempo real."""
    if rf_model is None:
        return None

    try:
        # 1. Hashing Trick (Imobiliária)
        imobiliaria_nome = str(imovel_dict.get("imobiliaria_nome") or "UNKNOWN").strip().lower()
        imob_hash = int(hashlib.md5(imobiliaria_nome.encode('utf-8')).hexdigest(), 16) % 1024

        # 2. Reproduz a categorizacao de area ajustada no treino.
        area = float(imovel_dict.get("area_m2") or 0)
        titulo = imovel_dict.get("titulo") or ""
        tipo_imovel = imovel_dict.get("tipo_imovel") or extract_tipo_imovel(
            imovel_dict.get("url"), titulo
        )
        bairro = str(imovel_dict.get("local_bairro") or "Outro")
        matching_stats = area_statistics.loc[
            (area_statistics["bairro"] == bairro)
            & (area_statistics["tipo_imovel"] == tipo_imovel)
        ] if {"bairro", "tipo_imovel"}.issubset(area_statistics.columns) else pd.DataFrame()
        if not matching_stats.empty:
            area_med = float(matching_stats.iloc[0]["area_mediana_m2"])
            area_mad = float(matching_stats.iloc[0]["area_mad"])
            if area < area_med - area_mad:
                area_cat = "Compacto"
            elif area > area_med + area_mad:
                area_cat = "Amplo"
            else:
                area_cat = "Padrao"
        elif area < 45:
            area_cat = "Compacto"
        elif area > 120:
            area_cat = "Amplo"
        else:
            area_cat = "Padrao"

        bairro_area_cross = f"{bairro}_{area_cat}"

        # 3. Montar o DataFrame com exata assinatura que o modelo espera
        # Lembrando que usamos 'banheiros' na BD para mapear as 'suites' do scraper
        features = pd.DataFrame([{
            "bairro_area_cross": bairro_area_cross,
            "tipo_imovel": tipo_imovel,
            "imobiliaria_hash": imob_hash,
            "area_m2": area,
            "quartos": int(imovel_dict.get("quartos") or 0),
            "suites": int(imovel_dict.get("suites") or 0),
            "vagas": int(imovel_dict.get("vagas") or 0)
        }])

        # 4. Inferência
        pred = rf_model.predict(features)[0]
        return PRICE_CLASSES.get(pred, "Preço Justo")

    except Exception as e:
        print(f"Erro na inferência: {e}")
        return None
# ==========================================

@router.get("/imoveis", response_model=List[FactImovelListSchema])
async def list_imoveis(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all properties with pagination and ML Price Classification"""
    imoveis = db.query(
        FactImovel.id_imovel,
        FactImovel.titulo,
        FactImovel.preco,
        FactImovel.area_m2,
        FactImovel.imagem,
        FactImovel.quartos,
        FactImovel.banheiros, # Necessário para a inferência
        FactImovel.vagas,     # Necessário para a inferência
        DimImobiliaria.nome_empresa.label("imobiliaria_nome"),
        DimLocal.bairro.label("local_bairro"),
    ).outerjoin(
        DimImobiliaria, FactImovel.id_imobiliaria_fk == DimImobiliaria.id_imobiliaria
    ).outerjoin(
        DimLocal, FactImovel.id_local_fk == DimLocal.id_local
    ).offset(skip).limit(limit).all()
    
    resultados = []
    for row in imoveis:
        imovel_dict = dict(row._mapping)
        # Invoca a inteligência artificial para este imóvel
        imovel_dict["classificacao_preco"] = predict_classificacao(imovel_dict)
        resultados.append(imovel_dict)
        
    return resultados


@router.get("/imoveis/stats")
async def imoveis_stats(db: Session = Depends(get_db)):
    """Get statistics about properties"""
    total = db.query(FactImovel).count()
    avg_preco = db.query(func.avg(FactImovel.preco)).scalar() or 0
    avg_area = db.query(func.avg(FactImovel.area_m2)).scalar() or 0
    
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
    """Get property details by ID with ML Price Classification"""
    # 1. Busca os dados com JOIN manual para evitar erros de relacionamento (lazy loading)
    result = db.query(FactImovel, DimImobiliaria, DimLocal).outerjoin(
        DimImobiliaria, FactImovel.id_imobiliaria_fk == DimImobiliaria.id_imobiliaria
    ).outerjoin(
        DimLocal, FactImovel.id_local_fk == DimLocal.id_local
    ).filter(FactImovel.id_imovel == id_imovel).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Property not found")
        
    # 2. Desempacota o resultado da query
    imovel, imobiliaria, local = result
        
    # 3. Monta o dicionário para a inteligência artificial
    imovel_dict = {
        "area_m2": imovel.area_m2,
        "titulo": imovel.titulo,
        "url": imovel.url,
        "quartos": imovel.quartos,
        "vagas": imovel.vagas,
        "imobiliaria_nome": imobiliaria.nome_empresa if imobiliaria else "UNKNOWN",
        "local_bairro": local.bairro if local else "Outro"
    }
    
    # 4. Anexa os objetos manualmente para o Pydantic serializar e injeta a previsão
    imovel.imobiliaria = imobiliaria
    imovel.local = local
    imovel.classificacao_preco = predict_classificacao(imovel_dict)
    
    return imovel


@router.get("/imoveis/by-hex/{id_hex}", response_model=FactImovelSchema)
async def get_imovel_by_hex(
    id_hex: str,
    db: Session = Depends(get_db)
):
    """Get property by hex ID with ML Price Classification"""
    result = db.query(FactImovel, DimImobiliaria, DimLocal).outerjoin(
        DimImobiliaria, FactImovel.id_imobiliaria_fk == DimImobiliaria.id_imobiliaria
    ).outerjoin(
        DimLocal, FactImovel.id_local_fk == DimLocal.id_local
    ).filter(FactImovel.id_hex == id_hex).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Property not found")
        
    imovel, imobiliaria, local = result
        
    imovel_dict = {
        "area_m2": imovel.area_m2,
        "titulo": imovel.titulo,
        "url": imovel.url,
        "quartos": imovel.quartos,
        "vagas": imovel.vagas,
        "imobiliaria_nome": imobiliaria.nome_empresa if imobiliaria else "UNKNOWN",
        "local_bairro": local.bairro if local else "Outro"
    }
    
    imovel.imobiliaria = imobiliaria
    imovel.local = local
    imovel.classificacao_preco = predict_classificacao(imovel_dict)
    
    return imovel