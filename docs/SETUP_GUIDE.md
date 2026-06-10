# 🚀 RentMaster Scraper - Guia de Configuração

## Status: ✅ OPERACIONAL

### Último Teste: 2026-06-10
- ✅ Validação de credenciais Azure: **SUCESSO**
- ✅ Web scraping: **30 imóveis extraídos**
- ✅ Upload ADLS Gen2: **24471 bytes enviados**
- ✅ Container Docker: **PRONTO PARA PRODUÇÃO**

---

## 📋 Estrutura de Configuração

### `.env` Raiz (compartilhado)
**Localização**: `/Projeto Integrador III 2.0/.env`

```env
# Credenciais compartilhadas entre todos os módulos
AZURE_TENANT_ID=dfb66dc4-3f3c-492c-991d-727dbd1c89d4
STORAGE_ACCOUNT_NAME=rentmasterstorageaccount
```

### `.env` Web Scraping (específico)
**Localização**: `/workflows/web_scraping/.env`

```env
# Service Principal específico para scraper
AZURE_CLIENT_ID=3f678962-1db7-410e-b4c8-ff71749a6715
AZURE_CLIENT_SECRET=vnZ8Q~fZ9uEWo0L2Daq-Ee69pCq6HWp5xsVX1bbg

# Configurações de scraping
NUM_PAGES=2
FORMAT=json
TIMEOUT_MS=45000
CONTAINER_NAME=scraper
```

---

## 🔐 Validação de Credenciais

### Validar Credenciais (sem fazer scraping)

```bash
cd /Projeto\ Integrador\ III\ 2.0

# Carregar variáveis de ambos os .env
export $(cat .env | grep -v '^#' | xargs)
export $(cat workflows/web_scraping/.env | grep -v '^#' | xargs)

# Validar
docker run --rm \
  -e AZURE_TENANT_ID="$AZURE_TENANT_ID" \
  -e AZURE_CLIENT_ID="$AZURE_CLIENT_ID" \
  -e AZURE_CLIENT_SECRET="$AZURE_CLIENT_SECRET" \
  -e STORAGE_ACCOUNT_NAME="$STORAGE_ACCOUNT_NAME" \
  rentmaster-scraper:improved --validate-credentials
```

**Saída esperada:**
```
✅ DIAGNÓSTICOS:
   ✅ UUID válido
   ✅ Autenticação com Service Principal bem-sucedida
   ✅ Conectado (4 containers)
```

---

## 🐳 Rodar o Container Localmente

### Opção 1: Modo Validação Apenas (sem scraping)

```bash
docker run --rm \
  -e AZURE_TENANT_ID="$AZURE_TENANT_ID" \
  -e AZURE_CLIENT_ID="$AZURE_CLIENT_ID" \
  -e AZURE_CLIENT_SECRET="$AZURE_CLIENT_SECRET" \
  -e STORAGE_ACCOUNT_NAME="$STORAGE_ACCOUNT_NAME" \
  rentmaster-scraper:improved \
  --validate-credentials
```

### Opção 2: Modo Completo (scraping + upload)

```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  -e NUM_PAGES=1 \
  -e FORMAT=json \
  -e AZURE_TENANT_ID="$AZURE_TENANT_ID" \
  -e AZURE_CLIENT_ID="$AZURE_CLIENT_ID" \
  -e AZURE_CLIENT_SECRET="$AZURE_CLIENT_SECRET" \
  -e STORAGE_ACCOUNT_NAME="$STORAGE_ACCOUNT_NAME" \
  rentmaster-scraper:improved
```

### Opção 3: Modo Permissivo (continua mesmo se falhar upload)

```bash
docker run --rm \
  -e AZURE_TENANT_ID="$AZURE_TENANT_ID" \
  -e AZURE_CLIENT_ID="$AZURE_CLIENT_ID" \
  -e AZURE_CLIENT_SECRET="$AZURE_CLIENT_SECRET" \
  -e STORAGE_ACCOUNT_NAME="$STORAGE_ACCOUNT_NAME" \
  rentmaster-scraper:improved \
  --skip-on-error  # Continua se falhar
```

### Opção 4: Modo Strict (falha se erro no upload)

```bash
docker run --rm \
  -e AZURE_TENANT_ID="$AZURE_TENANT_ID" \
  -e AZURE_CLIENT_ID="$AZURE_CLIENT_ID" \
  -e AZURE_CLIENT_SECRET="$AZURE_CLIENT_SECRET" \
  -e STORAGE_ACCOUNT_NAME="$STORAGE_ACCOUNT_NAME" \
  rentmaster-scraper:improved \
  --strict  # Falha se erro
```

---

## 🏗️ Argumentos do Script

### Opções de Scraping

```
--num-pages N          Número de páginas a extrair (padrão: 1)
--timeout-ms MS        Timeout em milissegundos (padrão: 45000)
--format {csv,json}    Formato de saída (padrão: both)
```

### Opções de Upload

```
--upload-to-adls                 Fazer upload para Azure
--storage-account NOME           Nome da Storage Account
--skip-on-error                  Continuar se falhar upload (padrão)
--strict                         Falhar se erro no upload
```

### Opções de Diagnóstico

```
--validate-credentials           Só validar credenciais (sem scraping)
```

---

## 🔍 Logs de Diagnóstico

### Validação de Credenciais

O script agora exibe:

```
🔐 Validando credenciais Azure...
   ✅ UUID válido                              # TENANT_ID
   ✅ UUID válido                              # CLIENT_ID  
   ✅ Configurado (40 chars)                   # CLIENT_SECRET
   ✅ Nome válido                              # STORAGE_ACCOUNT_NAME
   ✅ Autenticação com Service Principal...    # Login bem-sucedido
   ✅ Conectado (4 containers)                 # Storage conectada
```

### Erros Comuns e Soluções

#### ❌ TENANT_ID inválido
```
Solução: Use: az account show --query tenantId
```

#### ❌ Autenticação do Service Principal falhou
```
Solução: 
1. Verifique AZURE_CLIENT_ID
2. Verifique AZURE_CLIENT_SECRET
3. Verifique se o Secret não expirou
```

#### ❌ Storage Account não encontrada
```
Solução:
1. Verifique o nome da Storage Account
2. Verifique se está na mesma subscription
3. Verifique RBAC do Service Principal
```

---

## 📊 Service Principals Disponíveis

| Módulo | Client ID | Propósito | Container |
|--------|-----------|----------|-----------|
| web_scraping | `3f678962-1db7-410e-b4c8-ff71749a6715` | Scraping DFimoveis | bronze |
| bronze_to_silver | `80eefc6e-1dee-4f07-9e43-540c0130f205` | Pipeline de dados | bronze → silver |
| populate_database | `80eefc6e-1dee-4f07-9e43-540c0130f205` | Popular banco de dados | bronze |

---

## 🛠️ Troubleshooting

### Verificar se credenciais estão corretas via Azure CLI

```bash
# Login com Service Principal
TENANT_ID="dfb66dc4-3f3c-492c-991d-727dbd1c89d4"
CLIENT_ID="3f678962-1db7-410e-b4c8-ff71749a6715"
CLIENT_SECRET="vnZ8Q~fZ9uEWo0L2Daq-Ee69pCq6HWp5xsVX1bbg"

az login --service-principal \
  -u $CLIENT_ID \
  -p $CLIENT_SECRET \
  --tenant $TENANT_ID
```

### Listar containers na Storage Account

```bash
az storage container list \
  --account-name rentmasterstorageaccount
```

### Verificar RBAC do Service Principal

```bash
az role assignment list --all \
  --query "[?contains(principalId, '3f678962-1db7-410e-b4c8-ff71749a6715')]"
```

---

## 📈 Melhorias Implementadas

### ✅ Validação de Credenciais
- Valida TENANT_ID é um UUID válido
- Valida CLIENT_ID é um UUID válido
- Testa autenticação com ClientSecretCredential
- Testa conectividade com Storage Account

### ✅ Logs Melhorados
- Diagnósticos detalhados de cada componente
- Mensagens de erro claras e acionáveis
- Avisos sobre possíveis problemas

### ✅ Modo de Validação Apenas
- `--validate-credentials` sem fazer scraping
- Útil para CI/CD e troubleshooting

### ✅ Modo Permissivo e Strict
- `--skip-on-error` continua mesmo se falhar upload
- `--strict` falha se erro (padrão para produção)

### ✅ Melhor Tratamento de Erros
- Exceções específicas por tipo de erro
- Sugestões de fix baseadas no erro

---

## 📝 Próximos Passos

- [ ] Configurar CI/CD para validação automática
- [ ] Adicionar métricas de scraping
- [ ] Configurar alertas de falha
- [ ] Documentar workflow completo (bronze → silver → gold)
