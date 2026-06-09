# 🚀 Quick Start - Populate Database from Bronze

> **3 passos para rodar. Comece agora!**

---

## 📋 Pré-requisitos

- ✅ Python 3.11+
- ✅ `az login` (Azure CLI autenticado)
- ✅ Acesso ao storage account `rentmasterstorageaccount`

---

## 🚀 Rodar Agora (2 minutos)

### Passo 1: Instalar

```bash
pip install -r requirements.txt
```

### Passo 2: Configurar Email

```bash
export EMAIL_PASSWORD="ftug ypby hkps ourm"  # Sua App Password do Gmail
export EMAIL_TO="jonashonorato4@gmail.com"
```

### Passo 3: Executar

```bash
python main.py
```

✅ Pronto! Verifique seu email em segundos.

---

## 📊 O que acontece?

```
Azure Storage (bronze/raw/)
    ↓ [Lê JSONs]
Normaliza dados
    ↓ [Parse preco, area, quartos]
SQLite (rental.db)
    ↓ [UPSERT]
📧 Email enviado!
```

---

## 🐳 Rodar no Docker (Opcional)

```bash
# Build
docker build -t populate-db .

# Run
docker run \
  -e EMAIL_PASSWORD="ftug ypby hkps ourm" \
  -e EMAIL_TO="jonashonorato4@gmail.com" \
  -v $(pwd)/data:/data \
  populate-db
```

---

## 🎯 Output Esperado

### ✅ Sucesso
```
✅ Connected to Storage Account: rentmasterstorageaccount
📋 Found 5 JSON files
🚀 Starting Bronze to Database Pipeline
📥 Processing: imoveis_20260408.json
🎯 Inserted 150 properties
✅ Email sent to jonashonorato4@gmail.com
✅ Pipeline completed successfully!
```

### ❌ Erro
```
❌ Failed to connect to Storage: ...
🔍 Check: az login
```

---

## 🔧 Troubleshooting

### "DefaultAzureCredential not initialized"
```bash
az login
```

### "Invalid App Password"
- Gera nova em: https://myaccount.google.com/apppasswords

### "SMTP Connection refused"
```bash
# Teste conexão
python -c "import smtplib; s=smtplib.SMTP('smtp.gmail.com', 587); print('OK')"
```

---

## 📚 Documentação Completa

Ver [README.md](README.md) para:
- Estrutura de dados esperada
- Variáveis de ambiente
- Azure Container Apps deployment
- Performance & segurança

---

## 🎉 Pronto!

Qualquer dúvida, leia o [README.md](README.md) completo.
