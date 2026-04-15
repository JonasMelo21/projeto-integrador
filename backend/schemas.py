"""Pydantic schemas for API requests/responses"""
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class DimImobiliariaSchema(BaseModel):
    id_imobiliaria: int
    nome_empresa: str
    
    class Config:
        from_attributes = True


class DimLocalSchema(BaseModel):
    id_local: int
    bairro: str
    cidade: str
    uf: str
    
    class Config:
        from_attributes = True


class FactImovelSchema(BaseModel):
    id_imovel: int
    id_hex: str
    titulo: str
    url: str
    preco: float
    area_m2: float
    quartos: Optional[int]
    banheiros: Optional[int]
    vagas: Optional[int]
    imagem: str
    descricao: Optional[str]
    data_extracao: datetime
    imobiliaria: Optional[DimImobiliariaSchema]
    local: Optional[DimLocalSchema]
    
    class Config:
        from_attributes = True


class FactImovelListSchema(BaseModel):
    id_imovel: int
    titulo: str
    preco: float
    area_m2: float
    imagem: str
    quartos: Optional[int]
    imobiliaria_nome: Optional[str]
    local_bairro: Optional[str]
    
    class Config:
        from_attributes = True
