# 📱 RentMaster - *Moneyball* de Aluguel

> Aplicativo móvel inteligente que combate a assimetria de informações no mercado imobiliário do Distrito Federal. Com Machine Learning e IA, ajuda locatários a identificar se um aluguel é justo, caro ou uma barganha.

> 💡 **Nota de Referência:** A imagem a seguir é utilizada exclusivamente para fins ilustrativos e de referência criativa, demonstrando a obra cinematográfica "*Moneyball*" que serviu de inspiração para a concepção analítica deste projeto. Todos os direitos reservados aos seus respectivos criadores.

![logo do filme moneyball](images/moneyball_filme_logo.webp)

---

## 🎯 O Problema e a Solução

Para quem busca moradia no Distrito Federal, a inflação e a opacidade nos preços dos aluguéis residenciais são desafios reais, gerando uma severa assimetria de informações onde o locatário não possui métricas claras para avaliar se o valor cobrado é justo.

O **RentMaster** atua como um mediador imparcial. Através de um aplicativo móvel nativo, utiliza tecnologia de ponta para quebrar essa barreira de desinformação. Algoritmos de Machine Learning analisam variáveis de mercado, permitindo aos usuários identificar anomalias, negociar reduções baseadas em dados e garantir locações por valores verdadeiramente justos.

---

## ✨ Funcionalidades Principais

1. **Login Seguro com Google OAuth**: 
   - Autenticação nativa do Google
   - Validação de tokens JWT no backend
   - Sessões seguras

2. **Pipeline de Dados (Medallion Architecture)**: 
   - Módulo de `web scraping` automatizado (`scraper_to_bronze`)
   - Refinamento e estruturação em camadas Bronze, Silver e Gold
   - ~50.000 imóveis processados

3. **Motor de Inteligência (Machine Learning)**: 
   - Modelos de precificação preditiva com `Random Forest`
   - Identificação de preços justos, caros ou barganha
   - Explicabilidade via feature importance

4. **Assistente Virtual de IA**: 
   - Integração com `Vanna AI` para análise natural language
   - Pergunte em português: *"Qual o preço médio de 2 quartos?"*
   - SQL gerado automaticamente

5. **Interface Mobile Nativa**: 
   - Aplicativo Flutter para iOS e Android
   - Design responsivo e otimizado para toque
   - Performance máxima com consumo mínimo de bateria

---

## 🏗️ Tech Stack

| Camada | Tecnologia |
|--------|-----------|
| **Frontend Mobile** | Flutter, Dart |
| **Backend / API** | Python, FastAPI, SQLAlchemy |
| **Machine Learning** | Scikit-Learn (Random Forest), Pandas, NumPy |
| **IA Conversacional** | Vanna AI (RAG Analytics) |
| **Armazenamento** | SQLite (Local), Azure Data Lake (Pipeline) |
| **Autenticação** | Google OAuth 2.0 |
| **Infraestrutura** | Docker, Docker Compose |
| **Package Manager Backend** | UV (Python) |

---

## ⚠️ Restrições de Ambiente (Desenvolvimento)

Este projeto foi otimizado para desenvolvimento em **Windows com Docker**. Não há dependência de SDKs locais complexos:

| Requisito | Status | Detalhes |
|-----------|--------|----------|
| Flutter SDK Local | ❌ Não Required | Usar Docker: `ghcr.io/cirruslabs/flutter:latest` |
| Java/Android Studio | ❌ Não Required | Emulador isolado em container ou Project IDX |
| Python Local | ❌ Não Required | Backend roda em Docker container |
| Backend Docker | ✅ Required | `docker compose up -d backend` |

---

## 🚀 Como Começar

### ✅ Pré-requisitos

- **Windows 10+** com PowerShell
- **Docker Desktop** instalado
- **Git** para clonar o repositório
- **Conta Google** para testar OAuth

### 1️⃣ Clonar e Configurar Variáveis de Ambiente

```powershell
# Clone o repositório
git clone https://github.com/seu-usuario/rentmaster.git
cd rentmaster

# Copie o template de ambiente
cp backend\.env.example backend\.env

# Edite backend\.env e adicione seu GOOGLE_WEB_CLIENT_ID
# Obter em: https://console.cloud.google.com/
```

### 2️⃣ Subir o Backend (FastAPI)

```powershell
# Construir e iniciar backend em background
docker compose up --build -d backend

# Verificar se está rodando
docker compose ps

# Ver logs em tempo real
docker compose logs -f backend
```

✅ Backend disponível em: **http://localhost:8000**

**Endpoints úteis**:
- Health Check: `http://localhost:8000/health`
- Swagger API Docs: `http://localhost:8000/docs`
- Auth Endpoint: `POST http://localhost:8000/auth/google`

### 3️⃣ Desenvolver o App Mobile (Flutter)

#### Opção A: Project IDX (Recomendado - Cloud)

```powershell
# Abrir o projeto no Google Project IDX
# https://idx.google.com
# 1. Importar este repositório
# 2. Selecionar "Flutter" como template
# 3. IDE pronta com Flutter SDK
```

#### Opção B: Docker Local (Para compilação)

```powershell
# Instalar dependências Flutter usando Docker
docker run --rm -v ${PWD}/mobile:/app -w /app ghcr.io/cirruslabs/flutter:latest flutter pub get

# Build APK
docker run --rm -v ${PWD}/mobile:/app -w /app ghcr.io/cirruslabs/flutter:latest flutter build apk

# Build iOS
docker run --rm -v ${PWD}/mobile:/app -w /app ghcr.io/cirruslabs/flutter:latest flutter build ios
```

#### Opção C: DartPad (Prototipagem Rápida)

Copie código de `mobile/lib/main.dart` para https://dartpad.dev para testes rápidos.

### 4️⃣ Testar a Integração Completa

```bash
# Terminal 1: Backend já está rodando
docker compose logs -f backend

# Terminal 2: Mobile (via Project IDX ou emulador)
# 1. Abra o app
# 2. Clique em "Continuar com o Google"
# 3. Faça login com sua conta Google
# 4. ✅ Deve navegar para tela "Sobre"
```

---

## 📁 Estrutura do Projeto

```
rentmaster/
├── mobile/                          # 📱 Aplicativo Flutter
│   ├── lib/
│   │   ├── main.dart               # Entry point
│   │   ├── screens/                # Telas do app
│   │   ├── config/
│   │   │   └── api_client.dart     # Cliente HTTP
│   │   └── models/                 # Modelos de dados
│   ├── pubspec.yaml                # Dependências Dart/Flutter
│   └── GOOGLE_SIGNIN_SETUP.md       # Setup Google Sign-In
│
├── backend/                         # 🔌 API FastAPI
│   ├── main.py                     # Entry point FastAPI
│   ├── routes/
│   │   ├── auth.py                 # POST /auth/google
│   │   ├── imoveis.py              # GET /api/imoveis
│   │   └── dimensoes.py            # Dimensões
│   ├── models.py                   # SQLAlchemy ORM
│   ├── database.py                 # Configuração SQLite
│   ├── Dockerfile                  # Container backend
│   └── AUTH_SETUP.md               # Setup autenticação
│
├── data_pipeline/                  # 🔄 ETL (Bronze → Silver → Gold)
│   ├── scraper_to_bronze/
│   ├── silver_layer/
│   └── gold_layer/
│
├── ml_pipeline/                    # 🧠 Modelos de ML
│   ├── preprocessing/
│   ├── training/                   # Random Forest
│   └── inference/
│
├── ai/                             # 🤖 Agentes IA
│   ├── vanna_agent.py              # Chatbot RAG
│   └── prompts/
│
├── data/                           # 📊 Armazenamento
│   └── rental.db                   # SQLite
│
├── docs/
│   └── PI IV/
│       └── nova_arquitetura.md     # Documentação completa
│
├── docker-compose.yml              # Orquestração (backend only)
├── README.md                       # Este arquivo
├── .env.example                    # Template de variáveis
└── pyproject.toml                  # Dependências Python
```

---

## 🔄 Fluxo de Autenticação

```
1. Usuário abre app mobile
   ↓
2. Tela de Login → "Continuar com o Google"
   ↓
3. Google Sign-In (plugin nativo)
   ├─ Abre diálogo de login
   ├─ Usuário autentica
   └─ Retorna: idToken
   ↓
4. Frontend POST /auth/google { idToken }
   ↓
5. Backend valida token
   ├─ google.oauth2.id_token.verify_oauth2_token()
   ├─ Verifica audience (aud claim)
   └─ Extrai email e nome
   ↓
6. Backend retorna sessionToken
   ↓
7. Frontend armazena em storage local
   ↓
8. Todas as requisições futuras incluem: Authorization: Bearer {sessionToken}
   ↓
9. Navegação para Dashboard ✅
```

---

## 📚 Documentação Adicional

- **[Nova Arquitetura](docs/PI%20IV/nova_arquitetura.md)** - Diagrama completo da solução
- **[Auth Setup (Backend)](backend/AUTH_SETUP.md)** - Instalação e configuração
- **[Google Sign-In Setup (Mobile)](mobile/GOOGLE_SIGNIN_SETUP.md)** - Setup do OAuth
- **[Quick Start](QUICK_START.md)** - 3 minutos para começar

---

## 🐳 Comandos Docker Úteis

```powershell
# Subir backend em background
docker compose up -d backend

# Parar tudo
docker compose down

# Ver logs em tempo real
docker compose logs -f backend

# Executar comando no container backend
docker compose exec backend python -m pytest

# Remover volumes (limpar banco de dados)
docker compose down -v

# Rebuild imagem
docker compose build --no-cache backend
```

---

## 🧪 Testando Localmente

### Backend Health Check

```powershell
# Verificar se backend está rodando
curl http://localhost:8000/health

# Resultado esperado:
# {"status": "ok"}
```

### Acessar Swagger UI

Abra no navegador: http://localhost:8000/docs

Você verá:
- ✅ `POST /auth/google` - Autenticação
- ✅ `GET /api/imoveis` - Listar imóveis
- ✅ `GET /api/imoveis/{id}` - Detalhes
- ✅ `POST /api/imoveis/analise` - Análise ML

### Testar Endpoint de Auth

```powershell
# Você precisará de um idToken real do Google Sign-In
# (gerado pelo frontend mobile)

$body = @{
    idToken = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ..."
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/auth/google" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

---

## 🔐 Segurança

### ✅ Implementado

- ✅ Validação de tokens OAuth2
- ✅ Verificação de expiração
- ✅ Validação de audience claim (aud)
- ✅ CORS configurado
- ✅ Headers de segurança

### 🔜 Roadmap

- [ ] Rate limiting nos endpoints
- [ ] Logging de auditoria
- [ ] Refresh token logic
- [ ] HTTPS em produção
- [ ] WAF (Web Application Firewall)

---

## 🛠️ Troubleshooting

| Problema | Solução |
|----------|---------|
| Docker não inicia | Abra Docker Desktop primeiro |
| Porta 8000 já em uso | `netstat -ano ` e mate o processo |
| Backend não responde | `docker compose logs -f backend` para ver erros |
| Google OAuth falha | Verifique `GOOGLE_WEB_CLIENT_ID` em `.env` |
| Flutter pub get falha | Usar comando Docker: `docker run --rm -v ${PWD}:/app ...` |

---

## 🚀 Próximos Passos

1. **Setup local**: Execute `docker compose up -d backend`
2. **Desenvolvimento mobile**: Use Project IDX (cloud)
3. **Testes**: Testar fluxo completo de login
4. **Deploy**: CI/CD pipeline para produção

---

## 📞 Suporte & Contribuição

- 📖 Leia a documentação em `/docs/PI IV/nova_arquitetura.md`
- 🐛 Reporte bugs em `/issues`
- 💡 Sugira features em `/discussions`

---

## 📄 Licença

Propriedade intelectual do Projeto Integrador IV - UnB.

---

**Status**: ✅ Em desenvolvimento - Arquitetura Mobile-First ativa

**Última Atualização**: Setembro 2026

**Arquiteto**: Staff Engineer, RentMaster Team
