# RentMaster - Moneyball de Aluguel 🏠📊

Plataforma inteligente que extrai imóveis para aluguel em tempo real, analisa preços com ML e fornece assistente virtual.

**240 imóveis** | **21 imobiliárias** | **39 localidades**

---

## 🎯 O Projeto

1. **Scraper** - Web scraping automático de portais imobiliários
2. **ADLS** - Armazenamento em Azure Data Lake Storage
3. **FastAPI** - Backend com 240 imóveis em SQLite
4. **Frontend** - Interface HTML pura com busca e filtros
5. **Docker** - Containerização para local e cloud

---

## 🚀 Como Começar

### Local (sem Docker)
```bash
# Backend
cd backend && python -m venv .venv_clean && source .venv_clean/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (outro terminal)
cd frontend && python -m http.server 5173
```

Acesse: http://localhost:5173

### Com Docker
```bash
docker compose build
docker compose up
```

Acesse: http://localhost:5173

---

## 📖 Documentação

- **[docs/SETUP.md](docs/SETUP.md)** - Como rodar (local e Docker)
- **[CONTEXT.md](CONTEXT.md)** - Regras de codificação
- **[docs/guides/SCRAPER.md](docs/guides/SCRAPER.md)** - Detalhes do scraper

---

## 🏗️ Tech Stack

- **Backend**: FastAPI + Uvicorn + SQLAlchemy
- **Frontend**: HTML5 puro (sem build tools)
- **Database**: SQLite (local)
- **Data**: ADLS Gen2 (Azure)
- **Docker**: Multi-service composition

---

## 📊 API Endpoints

```
GET  /api/imoveis?limit=50              # Lista imóveis
GET  /api/imoveis/{id}                  # Detalhes
GET  /api/imoveis/stats                 # Estatísticas
GET  /api/dimensoes/imobiliarias        # Empresas
GET  /api/dimensoes/locais              # Localidades
```

---

## 🐳 Docker

```bash
docker compose build  # Build
docker compose up     # Rodar
docker compose logs -f backend  # Logs
docker compose down   # Parar
```

---

## 🔧 Variáveis de Ambiente

### backend/scripts/.env.adls
```
AZURE_STORAGE_ACCOUNT=rentmasterstorageaccount
AZURE_STORAGE_KEY=<sua_chave>
ADLS_CONTAINER=bronze
ADLS_PATH=raw/
```

---

## 📁 Estrutura

```
backend/           → FastAPI app
frontend/          → Interface HTML
scrapper/          → Web scraper
docs/              → Documentação
docker-compose.yml → Orquestração
```

---

## 🚀 Próximos Passos

1. **Leia**: [docs/SETUP.md](docs/SETUP.md) para começar
2. **Code**: Veja [CONTEXT.md](CONTEXT.md) para regras
3. **Test**: Use os comandos em [docs/SETUP.md](docs/SETUP.md)

---

**Desenvolvido por**: Projeto Integrador III - CEUB
