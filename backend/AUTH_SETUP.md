# Configuração da Autenticação Google - Backend RentMaster

## Visão Geral

Este documento descreve como configurar o endpoint de autenticação Google no FastAPI backend do RentMaster.

## Instalação de Dependências

### Via `uv` (Recomendado)

```bash
cd backend
uv pip install google-auth google-auth-httplib2 google-auth-oauthlib
```

### Via `pip` (Alternativa)

```bash
cd backend
pip install google-auth google-auth-httplib2 google-auth-oauthlib
```

## Configuração do Ambiente

Crie um arquivo `.env` na pasta `backend/`:

```env
GOOGLE_WEB_CLIENT_ID=YOUR_WEB_CLIENT_ID.apps.googleusercontent.com
BACKEND_URL=http://localhost:8000
MOBILE_URL=http://localhost:3000
```

**Onde obter `GOOGLE_WEB_CLIENT_ID`:**

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione o existente
3. Ative a API "Google Identity" e "Google+API"
4. Vá para "Credentials" → "Create Credentials" → "OAuth Client ID"
5. Selecione "Web Application"
6. Authorized JavaScript Origins: `http://localhost:8000`
7. Authorized redirect URIs: `http://localhost:8000/auth/callback` (se necessário)
8. Copie o `Client ID` gerado

## Estrutura de Rotas

### Endpoint: `POST /auth/google`

**URL:** `http://localhost:8000/auth/google`

**Request Body:**
```json
{
  "idToken": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ..."
}
```

**Response (Sucesso - 200):**
```json
{
  "success": true,
  "message": "Authentication successful",
  "user": {
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://lh3.googleusercontent.com/...",
    "authenticatedAt": "2025-09-05T10:30:00.000000"
  },
  "sessionToken": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (Erro):**
```json
{
  "detail": "Invalid token: signature verification failed"
}
```

## Fluxo de Validação

1. **Frontend envia `idToken`** gerado pelo Google Sign-In
2. **Backend chama `id_token.verify_oauth2_token()`**
   - Valida assinatura criptográfica
   - Verifica expiração
   - Recupera chaves públicas do Google
3. **Backend verifica `aud` (audience)**
   - Garante que `aud` == `GOOGLE_WEB_CLIENT_ID`
4. **Backend extrai claims:**
   - `email`: Email do usuário
   - `name`: Nome completo
   - `picture`: URL da foto de perfil
5. **Backend retorna mock session token**
   - Pronto para futura integração com banco de dados

## Testando Local

### 1. Iniciar o Backend

```bash
cd backend
uv run python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Você verá:
```
✅ Database ready with X imóveis
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 2. Testar Endpoint com cURL

```bash
# Você precisa de um idToken real do Google Sign-In
curl -X POST http://localhost:8000/auth/google \
  -H "Content-Type: application/json" \
  -d '{"idToken":"YOUR_REAL_ID_TOKEN"}'
```

### 3. Testar com Swagger UI (Recomendado)

Acesse: http://localhost:8000/docs

- Localize o endpoint `POST /auth/google`
- Clique em "Try it out"
- Copie um `idToken` real do frontend
- Envie o request

## Integração Futura com Banco de Dados

Atualmente, o endpoint retorna um mock `sessionToken`. Para integração com SQLite:

**Próximo passo (em `backend/routes/auth.py` ~ linha 60):**

```python
# TODO: Implementar modelo User em models.py
from backend.models import User
from backend.database import SessionLocal

# Dentro de authenticate_google():
db = SessionLocal()
user = db.query(User).filter(User.email == email).first()
if not user:
    user = User(email=email, name=name, picture=picture)
    db.add(user)
    db.commit()
    db.refresh(user)

# Criar session_token real e salvar em banco
session_token = str(uuid.uuid4())
# db.add(Session(token=session_token, user_id=user.id))
# db.commit()
```

## Dependências Instaladas

| Pacote | Versão | Propósito |
|--------|--------|----------|
| `google-auth` | ≥2.25.0 | Validação de tokens JWT |
| `google-auth-httplib2` | ≥0.2.0 | HTTP client para Google Auth |
| `google-auth-oauthlib` | ≥1.2.0 | OAuth 2.0 utilities |

## Troubleshooting

### Erro: "Invalid token: signature verification failed"
- O `idToken` expirou (válido por ~1 hora)
- O `GOOGLE_WEB_CLIENT_ID` está incorreto
- Solução: Regenere o `idToken` no frontend

### Erro: "Token audience does not match"
- O `GOOGLE_WEB_CLIENT_ID` no `.env` não corresponde ao do Google Console
- Solução: Copie exatamente do Google Cloud Console

### Erro: "ModuleNotFoundError: No module named 'google'"
- Dependências não instaladas
- Solução: `uv pip install google-auth` ou `pip install google-auth`

### CORS Errors
- O CORS já está configurado em `main.py` com `allow_origins=["*"]`
- Se precisar, restrinja para apenas seu frontend:
  ```python
  allow_origins=["http://localhost:3000", "https://seu-app.com"]
  ```

## Segurança

⚠️ **Checklist de Segurança:**

- [ ] `GOOGLE_WEB_CLIENT_ID` está em `.env` (não em git)
- [ ] HTTPS ativado em produção
- [ ] CORS restringido para domínios conhecidos
- [ ] Rate limiting implementado no `/auth/google`
- [ ] Logs de autenticação e auditorias habilitados
- [ ] idToken validado antes de qualquer operação

## Referências

- [Google Auth Library for Python](https://google-auth.readthedocs.io/)
- [OAuth 2.0 ID Token Verification](https://developers.google.com/identity/gsi/web/guides/verify-google-id-token)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**Status:** ✅ Implementação base completa | ⏳ Integração DB pendente
