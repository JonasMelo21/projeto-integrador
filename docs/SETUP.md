# 🚀 Setup & Testing Guide

## ⚡ Quick Start (Local - Sem Docker)

### Pré-requisitos
```bash
python3 -m venv backend/.venv_clean
source backend/.venv_clean/bin/activate
pip install -q -r backend/requirements.txt
```

### Terminal 1: Backend
```bash
cd backend
source .venv_clean/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Esperado:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Frontend
```bash
cd frontend
python -m http.server 5173
```

Esperado:
```
Serving HTTP on 0.0.0.0 port 5173
```

### Abrir no navegador
```
http://localhost:5173
```

---

## 🐳 Com Docker

### Build e Iniciar
```bash
docker compose build
docker compose up
```

Esperado:
```
backend    | INFO:     Application startup complete.
frontend   | [1] signal 17 (sigchld)
```

### Acessar
```
Frontend: http://localhost:5173
Backend:  http://localhost:8000
```

---

## 🧪 Testando

### Backend Health
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### API de Imóveis
```bash
curl http://localhost:8000/api/imoveis?limit=2 | jq
```

Esperado:
```json
[
  {
    "id_imovel": 1,
    "titulo": "SQNW 108 Bloco D",
    "endereco": "NOROESTE, BRASILIA",
    "preco": 10900.0,
    "area": 150.0,
    ...
  }
]
```

### API de Estatísticas
```bash
curl http://localhost:8000/api/imoveis/stats | jq
```

### Frontend
```bash
# Abrir em navegador
http://localhost:5173

# Grid com 240 imóveis deve aparecer
# Busca deve funcionar em tempo real
# Clique em um imóvel para ver detalhes
```

---

## 🔄 Dados do ADLS

### Carregar 240 imóveis
```bash
cd backend
python scripts/load_from_adls.py
```

Esperado:
```
✅ Carregando configurações...
✅ Banco inicializado
✅ Total carregado: 240 imóveis
```

### Verificar dados no SQLite
```bash
sqlite3 backend/rental.db "SELECT COUNT(*) FROM fact_imoveis;"
# 240
```

---

## 📊 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check |
| GET | `/api/imoveis` | Lista imóveis (paginado) |
| GET | `/api/imoveis/{id}` | Detalhes de um imóvel |
| GET | `/api/imoveis/stats` | Estatísticas gerais |
| GET | `/api/dimensoes/imobiliarias` | Lista de imobiliárias |
| GET | `/api/dimensoes/locais` | Lista de localidades |

---

## 🔧 Variáveis de Ambiente

### backend/scripts/.env.adls
```
AZURE_STORAGE_ACCOUNT=rentmasterstorageaccount
AZURE_STORAGE_KEY=<sua_chave_aqui>
ADLS_CONTAINER=bronze
ADLS_PATH=raw/
```

### Carregar do ADLS
Arquivos disponíveis em `bronze/raw/`:
```
imoveis_20260408_183715.json (30 imóveis)
imoveis_20260414_195102.json (31 imóveis)
imoveis_20260414_221801.json (29 imóveis)
imoveis_20260414_222407.json (29 imóveis)
imoveis_20260414_222843.json (29 imóveis)
imoveis_20260414_224008.json (29 imóveis)
imoveis_20260415_060240.json (29 imóveis)
imoveis_20260415_132527.json (30 imóveis) ← Mais recente
─────────────────────────────────────
Total: 240 imóveis
```

---

## 🐛 Troubleshooting

### Port em uso
```bash
lsof -i :8000 | awk 'NR!=1 {print $2}' | xargs kill -9
lsof -i :5173 | awk 'NR!=1 {print $2}' | xargs kill -9
```

### Backend não responde
```bash
docker compose logs backend
docker compose restart backend
```

### Sem dados no frontend
```bash
# Verifique se os dados foram carregados
sqlite3 backend/rental.db "SELECT COUNT(*) FROM fact_imoveis;"

# Se vazio, carregar:
python backend/scripts/load_from_adls.py
```

### ModuleNotFoundError
```bash
# Certifique-se que está na pasta backend/
cd backend
python scripts/load_from_adls.py  # ✅ Correto
```

### Docker não encontrado
Instale em: https://www.docker.com/products/docker-desktop

---

## 📁 Estrutura de Arquivos

```
backend/
├── Dockerfile                    # Container FastAPI
├── requirements.txt              # Dependências
├── main.py                       # Aplicação
├── database.py                   # Setup ORM
├── models.py                     # Modelos
├── routes/
│   ├── imoveis.py               # GET /api/imoveis
│   └── dimensoes.py             # GET /api/dimensoes
└── scripts/
    ├── load_from_adls.py        # Carrega dados do ADLS
    └── .env.adls                # Credenciais Azure

frontend/
├── Dockerfile                    # Container Nginx
├── nginx.conf                    # Config Nginx
├── index.html                    # UI
├── style.css                     # Estilos
└── script.js                     # Lógica

scrapper/
├── Dockerfile                    # Container scraper (→ ACR)
├── scrapper.py                   # Scraper principal
└── debug_scraper.py              # Debug tools

docker-compose.yml               # Orquestração
```

---

## 📝 Resumo de Comandos

| Tarefa | Comando |
|--------|---------|
| Setup local | `python3 -m venv backend/.venv_clean && source backend/.venv_clean/bin/activate && pip install -r backend/requirements.txt` |
| Carregar dados | `python backend/scripts/load_from_adls.py` |
| Backend local | `cd backend && uvicorn main:app --reload` |
| Frontend local | `cd frontend && python -m http.server 5173` |
| Docker build | `docker compose build` |
| Docker up | `docker compose up` |
| Docker logs | `docker compose logs -f backend` |
| Docker down | `docker compose down` |
| Testar API | `curl http://localhost:8000/api/imoveis?limit=2` |

---

## ✅ Checklist antes de começar

- [ ] Python 3.11+ instalado
- [ ] Docker Desktop instalado (se usar containers)
- [ ] Arquivo `backend/scripts/.env.adls` configurado
- [ ] Portas 8000 e 5173 livres
- [ ] ~500MB de espaço em disco (dados + containers)
