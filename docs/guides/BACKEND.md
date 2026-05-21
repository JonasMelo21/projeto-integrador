# Backend FastAPI - Guia Completo 🚀

> **Como entender, estender e manter a API FastAPI do RentMaster**.

---

## 📌 Visão Rápida

- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: SQLite (local), Azure SQL Serverless (production)
- **Server**: Uvicorn
- **Arquivo Principal**: `backend/main.py`

---

## 🏗️ Arquitetura de Arquivos

```
backend/
├── Dockerfile                      # Container FastAPI
├── requirements.txt                # Dependências pip
├── main.py                         # ⭐ Entrada da aplicação
├── database.py                     # Setup SQLAlchemy + conexão
├── models.py                       # Modelos ORM (dim_*, fact_*)
├── schemas.py                      # Pydantic schemas (validação)
│
├── routes/
│   ├── __init__.py
│   ├── imoveis.py                 # GET /api/imoveis
│   └── dimensoes.py               # GET /api/dimensoes/*
│
└── scripts/
    ├── load_from_adls.py          # Carrega dados do ADLS para SQLite
    └── .env.adls                  # Credenciais Azure (não commitr!)
```

---

## 🧠 Componentes Principais

### 1️⃣ `main.py` - Aplicação FastAPI

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import init_db, get_session
from .routes import imoveis, dimensoes

app = FastAPI(
    title="RentMaster API",
    description="API para consultas de imóveis",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Rotas
app.include_router(imoveis.router)
app.include_router(dimensoes.router)

# Frontend estático
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
```

**Responsabilidades**:
- ✅ Criar aplicação FastAPI
- ✅ Registrar middlewares (CORS, logs)
- ✅ Incluir rotas
- ✅ Servir frontend estático

### 2️⃣ `database.py` - Conexão e Setup

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite (local) ou Azure SQL (production)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rental.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Criar tabelas e carregar dados iniciais"""
    Base.metadata.create_all(bind=engine)
    
    # Se banco vazio, carregar dados do ADLS
    with SessionLocal() as db:
        count = db.query(FactImovel).count()
        if count == 0:
            logger.info("Banco vazio, carregando do ADLS...")
            load_from_adls(db)
```

**Responsabilidades**:
- ✅ Gerenciar engine SQLAlchemy
- ✅ Criar sessionmaker
- ✅ Inicializar banco na startup

### 3️⃣ `models.py` - Definição do Schema

```python
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DimImobiliaria(Base):
    __tablename__ = "dim_imobiliarias"
    id_imobiliaria = Column(Integer, primary_key=True)
    nome_empresa = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DimLocal(Base):
    __tablename__ = "dim_locais"
    id_local = Column(Integer, primary_key=True)
    bairro = Column(String)
    cidade = Column(String)
    uf = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class FactImovel(Base):
    __tablename__ = "fact_imoveis"
    id_imovel = Column(Integer, primary_key=True)
    id_hex = Column(String, unique=True, index=True)  # SHA-256 hash 12 chars
    id_imobiliaria = Column(Integer, ForeignKey("dim_imobiliarias.id_imobiliaria"))
    id_local = Column(Integer, ForeignKey("dim_locais.id_local"))
    preco = Column(Float)
    area_m2 = Column(Float)
    quartos = Column(Integer)
    banheiros = Column(Integer)
    vagas = Column(Integer)
    data_extracao = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Responsabilidades**:
- ✅ Definir tabelas (dim_*, fact_*)
- ✅ Relacionamentos via ForeignKey
- ✅ Índices para query rápida

### 4️⃣ `schemas.py` - Validação Pydantic

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ImovelResponse(BaseModel):
    id_imovel: int
    id_hex: str
    titulo: str
    preco: float
    area_m2: float
    quartos: int
    imobiliaria: str
    bairro: str
    cidade: str

    class Config:
        from_attributes = True  # Converter ORM → dict

class ImovelStatsResponse(BaseModel):
    total_imoveis: int
    preco_medio: float
    area_media: float
    preco_minimo: float
    preco_maximo: float
```

---

## 🔌 Rotas (Endpoints)

### `/api/imoveis` - Listar Imóveis

```bash
curl "http://localhost:8000/api/imoveis?limit=10&offset=0"
```

**Query Parameters**:
- `limit` (int, default=50): Quantidade por página
- `offset` (int, default=0): Saltar N registros
- `min_preco` (float, optional): Filtro
- `max_preco` (float, optional): Filtro
- `quartos` (int, optional): Filtro
- `cidade` (str, optional): Filtro

**Response**:
```json
{
  "total": 240,
  "limit": 10,
  "offset": 0,
  "imoveis": [
    {
      "id_imovel": 1,
      "id_hex": "7c2bf7dac4f5",
      "titulo": "Imóvel em Brasília",
      "preco": 2500.0,
      "area_m2": 120.0,
      "quartos": 3,
      "imobiliaria": "Imobiliária ABC",
      "bairro": "Asa Sul",
      "cidade": "Brasília"
    }
  ]
}
```

### `/api/imoveis/{id}` - Detalhes

```bash
curl "http://localhost:8000/api/imoveis/1"
```

### `/api/imoveis/stats` - Estatísticas

```bash
curl "http://localhost:8000/api/imoveis/stats"
```

**Response**:
```json
{
  "total_imoveis": 240,
  "preco_medio": 3200.0,
  "preco_minimo": 800.0,
  "preco_maximo": 12000.0,
  "area_media": 95.5,
  "quartos_media": 2.3
}
```

### `/api/dimensoes/imobiliarias` - Empresas

```bash
curl "http://localhost:8000/api/dimensoes/imobiliarias"
```

**Response**:
```json
{
  "total": 21,
  "imobiliarias": [
    { "id": 1, "nome": "Imobiliária ABC" },
    { "id": 2, "nome": "Imobiliária XYZ" }
  ]
}
```

### `/api/dimensoes/locais` - Localidades

```bash
curl "http://localhost:8000/api/dimensoes/locais"
```

**Response**:
```json
{
  "total": 39,
  "locais": [
    { "id": 1, "bairro": "Asa Sul", "cidade": "Brasília", "uf": "DF" },
    { "id": 2, "bairro": "Lago Sul", "cidade": "Brasília", "uf": "DF" }
  ]
}
```

---

## 🚀 Como Começar a Desenvolver

### Setup Local

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# source .venv/Scripts/activate  # Windows

pip install -r requirements.txt
```

### Rodar Servidor

```bash
# Development (auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testar Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Listar imoveis
curl "http://localhost:8000/api/imoveis?limit=3"

# Stats
curl http://localhost:8000/api/imoveis/stats

# Swagger UI (documentação interativa)
# Abra: http://localhost:8000/docs
```

---

## ✨ Adicionar Nova Rota

### 1. Criar arquivo em `routes/nova_rota.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_session
from ..models import FactImovel

router = APIRouter(prefix="/api/nova", tags=["nova"])

@router.get("/dados")
async def get_dados(db: Session = Depends(get_session)):
    """Endpoint novo"""
    dados = db.query(FactImovel).limit(10).all()
    return {"dados": dados}
```

### 2. Importar em `main.py`

```python
from .routes import nova_rota

app.include_router(nova_rota.router)
```

### 3. Testar

```bash
curl http://localhost:8000/api/nova/dados
```

---

## 🔐 Variáveis de Ambiente

Criar `.env` na raiz de `backend/`:

```
DATABASE_URL=sqlite:///./rental.db
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

Carregar em `main.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
```

---

## 📝 Padrões de Codificação

✅ **Type Hints Obrigatórios**:
```python
async def get_imovel(id: int, db: Session = Depends(get_session)) -> ImovelResponse:
    ...
```

✅ **Docstrings**:
```python
async def get_imovel(id: int) -> ImovelResponse:
    """
    Retorna detalhes de um imóvel.
    
    Args:
        id: ID do imóvel
    
    Returns:
        ImovelResponse com dados do imóvel
    
    Raises:
        HTTPException: Se imóvel não encontrado (404)
    """
```

✅ **Error Handling**:
```python
from fastapi import HTTPException

@router.get("/{id}")
async def get(id: int, db: Session = Depends(get_session)):
    obj = db.query(Model).filter(Model.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Não encontrado")
    return obj
```

---

## 🐛 Troubleshooting

### Port 8000 já em uso

```bash
lsof -i :8000 | awk 'NR!=1 {print $2}' | xargs kill -9
```

### ImportError nos modelos

```bash
# Certifique-se que está em backend/
cd backend
python -m uvicorn main:app --reload
```

### Banco sem dados

```bash
python scripts/load_from_adls.py
```

---

## 📚 Próximas Etapas

1. **Autenticação JWT** - Proteger endpoints
2. **Rate Limiting** - Limitar requisições
3. **Caching** - Redis para queries frecuentes
4. **Logging Estruturado** - Salvar logs em Azure
5. **ML Endpoints** - Integrar modelo XGBoost

Leia: [../SETUP.md](../SETUP.md) para testes cloud.

---

**Última atualização**: Sprint 2, Maio 2026
**Autor**: RentMaster Team
