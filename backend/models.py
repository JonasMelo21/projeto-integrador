"""SQLAlchemy ORM Models for Star Schema"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database import Base


class DimImobiliaria(Base):
    """Dimension: Real Estate Companies"""
    __tablename__ = "dim_imobiliarias"
    
    id_imobiliaria = Column(Integer, primary_key=True, index=True)
    nome_empresa = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DimLocal(Base):
    """Dimension: Locations (neighborhoods)"""
    __tablename__ = "dim_locais"
    
    id_local = Column(Integer, primary_key=True, index=True)
    bairro = Column(String(255), index=True)
    cidade = Column(String(255), index=True)
    uf = Column(String(2))
    created_at = Column(DateTime, default=datetime.utcnow)


class FactImovel(Base):
    """Fact Table: Properties"""
    __tablename__ = "fact_imoveis"
    
    id_imovel = Column(Integer, primary_key=True, index=True)
    id_hex = Column(String(12), unique=True, index=True)  # Business key from scraper
    id_imobiliaria_fk = Column(Integer, ForeignKey("dim_imobiliarias.id_imobiliaria"))
    id_local_fk = Column(Integer, ForeignKey("dim_locais.id_local"))
    
    # Property details (from JSON)
    titulo = Column(String(500))
    url = Column(String(1000))
    preco = Column(Float)  # Monthly rental price
    area_m2 = Column(Float)
    quartos = Column(Integer)
    banheiros = Column(Integer)
    vagas = Column(Integer)
    imagem = Column(String(1000))
    descricao = Column(String(2000))
    
    # Metadata
    data_extracao = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
