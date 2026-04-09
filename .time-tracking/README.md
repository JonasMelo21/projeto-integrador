# Time Tracking - RentMaster Project

Sistema automático de rastreamento de horas por funcionalidade/módulo usando **WakaTime**.

## 📊 Estrutura

```
.time-tracking/
├── export_wakatime.py        # Script de exportação dos dados
├── archive/                  # Histórico de dados (não versionado)
│   └── wakatime-YYYYMMDD.json
└── README.md                 # Este arquivo
```

## 🚀 Setup Rápido

### 1. Instalar dependências
```bash
uv sync --group time-tracking
```

### 2. Configurar WakaTime
```bash
# A. Instalar extensão VS Code
# Menu: Extensions → WakaTime → Install

# B. Criar conta (gratuita)
# Acesse: https://wakatime.com

# C. Obter API Key
# Settings → API Key → Copiar

# D. Adicionar ao .env
echo "WAKATIME_API_KEY=your-key-here" > ../.env
```

### 3. Pronto!
- WakaTime começa a rastrear automaticamente
- Ao fazer `git commit`, o hook exporta dados
- Dados salvos em `archive/`

## 📋 Como Usar

### Exportar dados manualmente
```bash
python export_wakatime.py

# Com opções customizadas
python export_wakatime.py --days 14 --quiet
```

### Ver relatório
```bash
python export_wakatime.py  # Com resumo

# Ou ler arquivo JSON
cat archive/wakatime-*.json | jq .
```

### Formatos de saída

**Arquivo JSON:**
```json
{
  "2026-04-08": {
    "total_seconds": 112320,
    "total_hours": 31.2,
    "projects": {
      "scraper": {
        "seconds": 102060,
        "hours": 28.35,
        "percent": 90.9
      },
      "backend": {
        "seconds": 10260,
        "hours": 2.85,
        "percent": 9.1
      }
    }
  }
}
```

## 🔄 Git Hook Automático

**Localização:** `../.git/hooks/post-commit`

**Quando executa:**
- Após cada `git commit` em branches de feature (`feature/*`, `fix/*`, `sprint*`)

**O que faz:**
```bash
# Exporta dados WakaTime automaticamente
python3 .time-tracking/export_wakatime.py --quiet
```

**Se quiser desabilitar:**
```bash
# Temporariamente
git commit -m "msg" --no-verify

# Persistentemente (remover hook)
rm ../.git/hooks/post-commit
```

## 📝 Preencher no Azure DevOps

1. **Abrir o arquivo JSON:**
   ```bash
   cat archive/wakatime-*.json | jq '.[] | .total_hours'
   ```

2. **Verificar horas por projeto:**
   ```bash
   python export_wakatime.py  # Mostra resumo formatado
   ```

3. **Preenchimento Manual:**
   - Abrir task/bug no Azure DevOps
   - Campo: "Completed Work" ou "Effort (Hours)"
   - Adicionar valor das horas trabalhadas
   - (Futuro: sincronizar automaticamente via MCP)

## 📚 Referências

- **WakaTime Docs:** https://wakatime.com/developers
- **WakaTime API:** https://wakatime.com/api (requer login)
- **Veja também:** `../CONTEXT.md` → seção "11. Time Tracking Automático"

## 🐛 Troubleshooting

### Problema: "WAKATIME_API_KEY não configurada"
**Solução:**
```bash
# Cerificar que .env existe com chave
[ -f ../.env ] && grep WAKATIME_API_KEY ../.env
# Se não existir:
echo "WAKATIME_API_KEY=your-key-here" > ../.env
```

### Problema: "Nenhum dado encontrado"
**Possíveis causas:**
1. WakaTime extensão não está ativa
2. Nenhum arquivo editado/salvo ainda (WakaTime precisa de atividade)
3. API key inválida

**Verificar:**
- VS Code: View → Output → WakaTime
- Ativar modo debug: `WAKATIME_DEBUG=true`

### Problema: Git hook não executa
**Solução:**
```bash
# Verificar se é executável
ls -la ../.git/hooks/post-commit

# Tornar executável se necessário
chmod +x ../.git/hooks/post-commit

# Testar manualmente
bash ../.git/hooks/post-commit
```

## 💡 Dicas

1. **Histórico preservado:**
   - `.time-tracking/archive/` guarda todos os dados (não vai pro git)
   - Use para análise histórica e trends

2. **Múltiplos projetos:**
   - WakaTime detecta automaticamente por pasta aberta
   - Projeto = nome da pasta de workspace do VS Code

3. **Relatórios periódicos:**
   - Execute `export_wakatime.py` uma vez por dia/semana
   - Crie script cron para automatizar:
     ```bash
     0 18 * * * cd /path/to/projeto && python .time-tracking/export_wakatime.py
     ```

4. **Integração com CI/CD (futuro):**
   - Pode sincronizar com Azure DevOps via Azure Pipelines
   - Use Azure CLI MCP para poplar campos de work items

---

**Última atualização:** 2026-04-08  
**Versão:** 1.0.0  
**Status:** ✅ Operacional
