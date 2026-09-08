# Backend - RentMaster API

API REST construída em **FastAPI** que serve como o intermediário entre o aplicativo mobile e os dados armazenados. O backend realiza:
- Autenticação via Google OAuth
- Listagem e busca de imóveis
- Classificação de preços em tempo real usando modelo de ML
- Gestão de sessões de usuários

---

## 📊 Arquitetura do Backend

```
Backend (FastAPI)
├── Authentication (Google OAuth 2.0)
│   └── JWT token validation + session management
├── Data Access Layer (SQLAlchemy ORM)
│   └── SQLite database
├── ML Inference Layer
│   └── Random Forest model (joblib)
└── REST API Routes
    ├── /auth/ → Autenticação
    ├── /api/imoveis → Listagem e busca
    └── /api/dimensoes → Estatísticas
```

---

## 📁 Estrutura de Arquivos

```
backend/
├── main.py                    # Entry point FastAPI
├── database.py               # Configuração SQLAlchemy + SQLite
├── models.py                 # ORM SQLAlchemy (tabelas)
├── schemas.py                # Pydantic schemas (validação)
├── routes/
│   ├── auth.py              # POST /auth/google
│   ├── imoveis.py           # GET /api/imoveis + ML inference
│   └── dimensoes.py         # GET /api/dimensoes
├── Dockerfile               # Container backend
└── AUTH_SETUP.md            # Documentação OAuth setup
```

---

## 🔑 Arquivos Principais

### `main.py`
- Inicializa a aplicação FastAPI
- Configura middleware CORS
- Registra rotas (auth, imoveis, dimensoes)
- Inicializa banco de dados
- Define health check endpoint

### `database.py`
- Configuração SQLAlchemy
- Connection SQLite
- Função `get_db()` para dependency injection
- Schema criação automática

### `models.py`
- **FactImovel**: Tabela principal de imóveis
- **DimImobiliaria**: Dimensão de imobiliárias
- **DimLocal**: Dimensão de localidades (bairros)
- **User**: Tabela de usuários autenticados

### `schemas.py`
- Pydantic models para validação de entrada/saída
- **FactImovelSchema**: Schema completo de imóvel
- **FactImovelListSchema**: Schema reduzido para listagens

### `routes/auth.py`
- `POST /auth/google` - Valida idToken do Google
- Extrai email e nome
- Cria/atualiza sessão do usuário
- Retorna JWT session token

### `routes/imoveis.py`
- `GET /api/imoveis` - Lista imóveis com paginação (skip/limit)
- **ML Inference**: Cada imóvel recebe classificação em tempo real (Barato/Justo/Caro)
- `GET /api/imoveis/{id}` - Detalhe de imóvel único com classificação
- `GET /api/imoveis/by-hex/{id_hex}` - Busca por ID hexadecimal
- `GET /api/imoveis/stats` - Estatísticas agregadas

### `routes/dimensoes.py`
- `GET /api/dimensoes/bairros` - Lista de todos os bairros
- `GET /api/dimensoes/imobiliarias` - Lista de imobiliárias
- Estatísticas por bairro

---

## 🧠 Fluxo de ML Inference

O backend carrega o modelo treinado (`ml_pipeline/models/random_forest_optimized.joblib`) na inicialização e o mantém em memória.

**Quando você requisita um imóvel:**

```
GET /api/imoveis
  ↓
1. Busca dados do SQLite (propriedades + dimensões)
  ↓
2. Para cada imóvel, monta dicionário com features:
   - area_m2
   - quartos
   - banheiros (suites)
   - vagas
   - imobiliaria_nome → hash MD5 (reduz cardinalidade)
   - local_bairro + categorização de área → bairro_area_cross
  ↓
3. Cria DataFrame com exata assinatura esperada pelo modelo
  ↓
4. Random Forest prediz: 0 (Barato), 1 (Preço Justo), 2 (Caro)
  ↓
5. Mapeia classe para label humano
  ↓
6. Anexa classificacao_preco ao retorno JSON
```

**Nota**: O backend faz inferência em **tempo real** — não pré-computa. Cada requisição dispara o modelo.

---

## 🔐 Fluxo de Autenticação

```
1. Mobile faz login com Google
   ↓ (retorna idToken)
2. POST /auth/google { idToken }
   ↓
3. Backend valida idToken com Google
   - Verifica signature
   - Valida expiration
   - Valida audience claim (aud)
   ↓
4. Extrai email e nome
   ↓
5. Cria/atualiza User no SQLite
   ↓
6. Gera JWT session token
   ↓
7. Retorna sessionToken ao mobile
   ↓
8. Mobile armazena em localStorage/keychain
   ↓
9. Todas as requisições futuras incluem:
   Authorization: Bearer {sessionToken}
```

---

## 📊 Modelo de Dados

### FactImovel (Tabela Principal)
```sql
id_imovel          INTEGER PRIMARY KEY
id_hex            TEXT UNIQUE (gerado pela pipeline)
id_imobiliaria_fk  INTEGER FK → DimImobiliaria
id_local_fk        INTEGER FK → DimLocal
titulo            TEXT
preco             FLOAT
area_m2           FLOAT
quartos           INTEGER
banheiros         INTEGER
vagas             INTEGER
imagem            TEXT (URL)
data_extracao     TIMESTAMP
```

### DimImobiliaria (Dimensão)
```sql
id_imobiliaria    INTEGER PRIMARY KEY
nome_empresa      TEXT
```

### DimLocal (Dimensão)
```sql
id_local          INTEGER PRIMARY KEY
bairro            TEXT
cidade            TEXT
uf                TEXT
```

### User (Sessões)
```sql
id_user           INTEGER PRIMARY KEY
email             TEXT UNIQUE
nome              TEXT
google_sub        TEXT (Google subject claim)
created_at        TIMESTAMP
last_login        TIMESTAMP
```

---

## 🚀 Como Rodar

### Opção 1: Docker (Recomendado)

```powershell
# Build e run
docker compose up -d backend

# Ver logs
docker compose logs -f backend

# Backend disponível em
# http://localhost:8000

# Swagger docs
# http://localhost:8000/docs
```

### Opção 2: Local (com uv)

```bash
# Instalar apenas dependências de backend
uv sync --group backend

# Executar FastAPI
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Como Testar

### Health Check
```powershell
curl http://localhost:8000/health
# Resultado: {"status": "ok"}
```

### Acessar Swagger
Abra: `http://localhost:8000/docs`

Você verá todos os endpoints documentados interativamente.

### Testar Listagem de Imóveis (sem auth)
```powershell
curl "http://localhost:8000/api/imoveis?skip=0&limit=5"
```

Resposta (com classificação ML):
```json
[
  {
    "id_imovel": 1,
    "titulo": "Apartamento 2 quartos",
    "preco": 2500.0,
    "area_m2": 75.0,
    "classificacao_preco": "Preço Justo",
    ...
  }
]
```

### Testar Autenticação
Você precisa de um `idToken` real do Google:

```powershell
$body = @{
    idToken = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ..."
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/auth/google" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"

# Resposta:
# {
#   "sessionToken": "eyJhbGciOiJIUzI1NiIs...",
#   "email": "usuario@gmail.com",
#   "nome": "João Silva"
# }
```

### Usar sessionToken em Requests Autenticados
```powershell
$headers = @{
    "Authorization" = "Bearer {sessionToken}"
}

curl -H $headers http://localhost:8000/api/imoveis
```

---

## 📋 Dependências

Veja o grupo `backend` em `pyproject.toml`:

```toml
backend = [
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.29.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
    "joblib>=1.5.3",     # Para carregar modelo ML
    "pandas>=2.0.0",     # Para criar DataFrame no inference
]
```

---

## 🔍 Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

```env
# Google OAuth
GOOGLE_WEB_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com

# Database (já default)
DATABASE_URL=sqlite:////app/data/rental.db

# Environment
ENV=development
```

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| Erro "Modelo de ML não encontrado" | Certifique-se que `ml_pipeline/models/random_forest_optimized.joblib` existe |
| Port 8000 em uso | `netstat -ano \| find "8000"` e mate o processo |
| CORS error | Verifique `CORSMiddleware` em `main.py` |
| Google auth falha | Verifique `GOOGLE_WEB_CLIENT_ID` em `.env` |
| Database lock | Reinicie container: `docker compose restart backend` |

---

## 🔧 Como Adicionar Novos Endpoints

1. Crie um arquivo em `backend/routes/seu_modulo.py`:

```python
from fastapi import APIRouter, Depends
from backend.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/seu-endpoint")
async def seu_endpoint(db: Session = Depends(get_db)):
    # Sua lógica aqui
    return {"resultado": "ok"}
```

2. Registre em `backend/main.py`:

```python
from backend.routes import seu_modulo
app.include_router(seu_modulo.router, prefix="/api", tags=["seu_modulo"])
```

3. Teste em `http://localhost:8000/docs`

---

## 📚 Referências

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)

---

**Status**: ✅ Em produção com ML inference em tempo real

**Última Atualização**: Setembro 2026
