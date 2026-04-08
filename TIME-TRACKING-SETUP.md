# 🚀 SETUP RÁPIDO - Time Tracking

## Pré-requisitos
- ✅ VS Code com extensão WakaTime instalada
- ✅ Conta WakaTime criada (gratuita)
- ✅ API Key do WakaTime em mãos

## 5 Passos para Começar

### 1️⃣ Adicione sua API Key no `.env`
```bash
# Abra arquivo .env neste diretório
nano .env

# Procure por WAKATIME_API_KEY=paste-your-api-key...
# Substituir por sua chave real:
WAKATIME_API_KEY=waka_5a1b2c3d4e5f6g7h8i9j0k1l2m3n
```

### 2️⃣ Instale dependências
```bash
cd /home/jonasmelo/ProjectsAndStudies/Projeto\ Integrador\ III\ 2.0
uv sync --group time-tracking
```

### 3️⃣ Teste a configuração
```bash
python .time-tracking/test_wakatime.py
```

Esperado:
```
✅ API Key configurada: waka_5a1...4e
✅ Conectado como: Jonas Melo
✅ Tudo configurado!
```

### 4️⃣ Comece a trabalhar!
- Abra pasta do projeto no VS Code
- Comece a editar arquivos normalmente
- WakaTime rastreia automaticamente (você verá icon no canto inferior)

### 5️⃣ Faça commits regularmente
```bash
git commit -m "feat: implementa nova feature"
# ← Git hook executa automaticamente
# ← Dados exportados para .time-tracking/archive/
```

## Ver Dados Rastreados

### Opção A: Exportar manualmente
```bash
python .time-tracking/export_wakatime.py
```

Exemplo de saída:
```
📊 Exportando últimos 7 dias do WakaTime...
  ✓ 2026-04-08: 31.25h
  ✓ 2026-04-07: 8.50h

======================================================================
📈 RESUMO DE HORAS POR PROJETO
======================================================================

Projeto                        Horas      Dias
--------------------------------------------------
scraper                         28.50         2
backend                          5.75         2
frontend                         3.50         1
--------------------------------------------------
TOTAL                           39.75h
```

### Opção B: Ver arquivo JSON
```bash
# Último arquivo gerado
cat .time-tracking/archive/wakatime-*.json | jq .

# Ou com Python
python -m json.tool .time-tracking/archive/wakatime-*.json
```

## Preencher no Azure DevOps

1. **Obtenha o total:**
   ```bash
   python .time-tracking/export_wakatime.py | grep "TOTAL"
   # TOTAL                           31.67h
   ```

2. **Abra a task no Azure DevOps**
3. **Preencha o campo "Completed Work" ou "Effort (Hours)"**
4. **Salve**

(Futuro: sincronização automática via MCP)

## Troubleshooting

### "WAKATIME_API_KEY não configurada"
```bash
# Verificar se .env existem
cat .env | grep WAKATIME

# Se vazio, editar .env
nano .env
# Adicionar: WAKATIME_API_KEY=sua-chave
```

### "Nenhum dado encontrado"
1. Verifique se VS Code extension está ativa
2. Edite algum arquivo para WakaTime detectar
3. Aguarde ~30 segundos

### Git hook não executa
```bash
# Verificar se executável
ls -la .git/hooks/post-commit

# Tornar executável se necessário
chmod +x .git/hooks/post-commit

# Testar manualmente
bash .git/hooks/post-commit
```

## 📚 Arquivos Importantes

| Arquivo | Propósito |
|---------|-----------|
| `.env` | Configurações locais (seu API key) |
| `.time-tracking/export_wakatime.py` | Script de exportação |
| `.time-tracking/test_wakatime.py` | Script de teste/verificação |
| `.time-tracking/README.md` | Documentação completa |
| `.git/hooks/post-commit` | Git hook automático |
| `CONTEXT.md` | Regra de time tracking (seção 11) |

## 💡 Dicas Pro

### Automatizar export diário
```bash
# Adicionar ao cron (executar diariamente às 18h)
(crontab -l 2>/dev/null; echo "0 18 * * * cd /path/to/projeto && python .time-tracking/export_wakatime.py") | crontab -
```

### Criar relatório semanal
```bash
#!/bin/bash
# save-as: generate-weekly-report.sh

cd /path/to/projeto
python .time-tracking/export_wakatime.py > /tmp/weekly-report.txt
echo "📊 Relatório salvo em /tmp/weekly-report.txt"
```

### Integração com Azure DevOps (futuro)
Quando MCP estiver configurado:
```bash
# Script que sincroniza horas automaticamente
python .time-tracking/sync_to_devops.py --task-id 123 --hours 28.5
```

---

**Pronto! Agora você tem time tracking automático integrado ao seu workflow.** ✨

Qualquer dúvida, consulte:
- `.time-tracking/README.md` - Documentação técnica completa
- `CONTEXT.md` - Seção "11. Time Tracking Automático"
