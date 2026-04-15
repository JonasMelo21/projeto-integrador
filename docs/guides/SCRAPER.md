# Módulo Scraper - Guia Completo 🔷

> **Documentação do módulo de Web Scraping responsável por extrair dados de portais imobiliários**.

Parte da **Sprint 2** (Epic 2.1 - Vitrine e Scraping Base). Consulte [../../CONTEXT.md](../../CONTEXT.md) para regras gerais.

---

## 📋 Visão Geral

O **Scraper** extrai dados de imóveis para aluguel do site **DFimoveis.com.br** de forma resiliente, gerando identificadores únicos e exportando em múltiplos formatos (JSON, CSV).

### Características Principais

- ✅ **Paginação automática** - Múltiplas páginas sem duplicatas
- ✅ **ID único hexa** - SHA-256 (12 chars) por imóvel
- ✅ **Múltiplos formatos** - JSON, CSV ou ambos
- ✅ **Resiliente** - Retries, timeouts, tratamento de erros
- ✅ **Dockerizado** - Pronto para Azure Container Instances
- ✅ **Integrado com ADF** - Pipeline `RunScraperContainer`

---

## 🚀 Quick Start

### 1️⃣ Instalar Dependências

```bash
cd "Projeto Integrador III 2.0"
uv sync --group scraping
```

### 2️⃣ Executar (Padrão)

```bash
# Uma página, saída em JSON + CSV
uv run scrapper/scrapper.py
```

**Resultado:**
```
✓ 30 imóveis extraídos com sucesso
✓ Dados salvos em: data/imoveis.json
✓ Dados salvos em: data/imoveis.csv
```

### 3️⃣ Com Opções

```bash
# 3 páginas, apenas JSON
uv run scrapper/scrapper.py --num-pages 3 --format json

# Custom URL + timeout maior
uv run scrapper/scrapper.py "https://www.dfimoveis.com.br/aluguel/df/lago-sul/imoveis" --timeout-ms 60000
```

---

## 📊 Dados Extraídos

Cada imóvel coletado contém:

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `id_hex` | string | ID único SHA-256 (12 chars) | `7c2bf7dac4f5` |
| `titulo` | string | Localização completa | SMPW Quadra 4, PARK WAY, BRASILIA |
| `url` | string | Link direto | https://www.dfimoveis.com.br/imovel/... |
| `preco` | string | Valor mensal | 26.900 |
| `descricao` | string | Resumo (max 200 chars) | Encante-se com esta belíssima... |
| `quartos` | string | Qty de quartos | 3 Quartos |
| `suites` | string | Qty de suítes | 3 Suítes |
| `vagas` | string | Vagas de garagem | 4 Vagas |
| `area` | string | Metragem | 450 m² |
| `imagem` | string | URL principal | https://img.dfimoveis.com.br/... |
| `imagens` | array | Todas as imagens | [...] |
| `imobiliaria` | string | Agência | Neves Teixeira Imóveis |
| `data_extracao` | string | ISO timestamp | 2026-04-08T21:36:38.455604 |

---

## 🎛️ Opções de Linha de Comando

```bash
uv run scrapper/scrapper.py [URL] [OPÇÕES]
```

### Argumentos Posicionais

| Argumento | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `URL` | string | `https://www.dfimoveis.com.br/aluguel/df/todos/imoveis` | URL base para scraping |

### Parâmetros Opcionais

```bash
--timeout-ms MS
  Timeout de carregamento da página (ms)
  Padrão: 45000 (45 seg)
  Uso: --timeout-ms 60000

--format {csv,json,both}
  Formato de saída
  Padrão: both
  Valores:
    csv   → Salva apenas .csv
    json  → Salva apenas .json
    both  → Ambos os formatos

--num-pages N
  Quantidade de páginas a extrair
  Padrão: 1
  Uso: --num-pages 5 (páginas 1-5 com deduplicação)
```

---

## 💡 Exemplos de Uso

### Exemplo 1: Padrão (1 página, ambos formatos)
```bash
uv run scrapper/scrapper.py
```

**Output:**
```
🔍 Iniciando scraping
   URL: https://www.dfimoveis.com.br/aluguel/df/todos/imoveis
   Páginas: 1
   Formato: json

✓ 30 imóveis únicos extraídos!
✓ Dados salvos em: .../data/imoveis.json
✓ Dados salvos em: .../data/imoveis.csv

📊 Resumo:
1. SMPW Quadra 4, PARK WAY, BRASILIA (ID: 7c2bf7dac4f5)
   R$ 26.900 | 3Q + 3S + 4V
```

### Exemplo 2: 3 páginas (deduplicação automática)
```bash
uv run scrapper/scrapper.py --num-pages 3
```

**Comportamento:**
- Página 1: Extrai 30 imóveis
- Página 2: Detecta 20 novos + 10 duplicados, adiciona 20
- Página 3: Detecta 5 novos + 25 duplicados, adiciona 5
- **Total Único:** 55 imóveis (sem duplicatas)

### Exemplo 3: Apenas JSON + timeout maior
```bash
uv run scrapper/scrapper.py --format json --timeout-ms 60000
```

### Exemplo 4: Bairro específico
```bash
uv run scrapper/scrapper.py \
  "https://www.dfimoveis.com.br/aluguel/df/lago-sul/imoveis" \
  --num-pages 2
```

### Exemplo 5: Apenas CSV
```bash
uv run scrapper/scrapper.py --format csv --num-pages 1
```

---

## 🐳 Uso em Docker

### Build da Imagem

```bash
cd scrapper/
docker build -t rentmaster-scraper:latest .
```

### Executar Localmente

```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  rentmaster-scraper:latest \
  python scrapper.py --num-pages 1
```

### Push para ACR

```bash
# Login
az acr login --name rentmasteracr

# Tag
docker tag rentmaster-scraper:latest rentmasteracr.azurecr.io/rentmaster-scraper:latest

# Push
docker push rentmasteracr.azurecr.io/rentmaster-scraper:latest
```

---

## 🔗 Integração com Azure Data Factory

O pipeline `RunScraperContainer` automatiza a execução do scraper:

```yaml
Pipeline Name: RunScraperContainer
Trigger: Agendado (diariamente)
Atividade:
  - Tipo: Container Instance
  - Imagem: rentmasteracr.azurecr.io/rentmaster-scraper:latest
  - Command: python scrapper.py --num-pages 1
  - Output: ADLS Gen2 (bronze/raw/)
```

### Teste Manual do Pipeline

Veja [../../docs/testing/CLOUD_TESTING.md](../../docs/testing/CLOUD_TESTING.md) para rodar o pipeline na nuvem com `az`.

---

## 🏗️ Arquitetura e Codificação

### Estrutura do Arquivo

```python
# scrapper.py segue padrão limpo:

import argparse
from datetime import datetime

class PropertyScraper:
    """Scraper de imóveis DFimoveis."""
    
    def __init__(self, timeout_ms: int = 45000):
        self.timeout = timeout_ms
    
    def scrape_page(self, url: str) -> list[dict]:
        """Extrai imóveis de uma página."""
        # Implementação
    
    def extract_property(self, article_html: str) -> dict:
        """Extrai dados estruturados de um artigo HTML."""
        # Implementação
    
    def save_output(self, data: list[dict], format: str) -> None:
        """Salva em JSON e/ou CSV."""
        # Implementação

if __name__ == "__main__":
    # main()
```

### Regras de Codificação

✅ **Siga o CONTEXT.md:**
- Código em **inglês** (variáveis, funções, classes)
- Documentação em **português** (comments, docstrings)
- **Type hints** obrigatórios
- Máx 20 linhas por função
- DRY (Don't Repeat Yourself)

❌ **Evite:**
- Variáveis genéricas (`x`, `temp`, `data`)
- Funções sem docstring
- Código duplicado
- Print em produção (use logging)

---

## 🔧 Desenvolvimento e Testes

### Teste Local (Rápido)

```bash
# Uma página
uv run scrapper/scrapper.py --num-pages 1 --format json

# Verificar saída
cat data/imoveis.json | head -50
```

### Debug

Arquivo `debug_scraper.py` contém logs detalhados:

```bash
uv run scrapper/debug_scraper.py
```

Gera arquivos em `debug_output/`:
- `first_article_YYYYMMDD_HHMMSS.html` - Primeiro artigo completo
- `full_page_YYYYMMDD_HHMMSS.html` - HTML da página
- `analysis_YYYYMMDD_HHMMSS.txt` - Análise de estrutura

### Validação de Dados

```python
# Verify output
import json

with open('data/imoveis.json') as f:
    data = json.load(f)

print(f"Total: {len(data['imoveis'])} imóveis")
print(f"IDs únicos: {len(set(im['id_hex'] for im in data['imoveis']))}")

# Checar primeiro imóvel
first = data['imoveis'][0]
print(f"  Título: {first['titulo']}")
print(f"  Preço: {first['preco']}")
print(f"  ID: {first['id_hex']}")
```

---

## 🚨 Troubleshooting

### Erro: "Timeout loading page"

**Causa:** Site muito lento ou bloqueado
**Solução:**

```bash
# Aumentar timeout
uv run scrapper/scrapper.py --timeout-ms 90000
```

### Erro: "0 propriedades encontradas"

**Causa:** Layout do site mudou
**Solução:**
1. Rodar script de debug:
   ```bash
   uv run scrapper/debug_scraper.py
   ```
2. Analisar `debug_output/first_article_*.html`
3. Atualizar seletores CSS se necessário
4. Commit + Push

### Erro: "JSON invalid"

**Causa:** Dados corrompidos ou encoding
**Solução:**

```python
import json

# Validar JSON
with open('data/imoveis.json', 'r', encoding='utf-8') as f:
    try:
        data = json.load(f)
        print("✓ JSON válido")
    except json.JSONDecodeError as e:
        print(f"✗ JSON inválido: {e}")
```

---

## 🔄 Próximas Sprints

### Sprint 3: Aprimoramentos
- [ ] Suporte a múltiplos portais (Imóvel Web, Vivastreet, etc.)
- [ ] Filtros avançados (preço min/max, quartos, etc.)
- [ ] Cache de resultados (não rescrape dados recentes)
- [ ] Webhooks para notificar quando novos dados chegam

### Sprint 4: IA & Análise
- [ ] Integrar com llama-index para busca semântica
- [ ] Summarize listings com LLM
- [ ] Detectar preços anômalos (ML)
- [ ] Recomendações personalizadas

---

## 📝 Submeter Melhorias

1. **Faça fork/branch:**
   ```bash
   git checkout -b feature/scraper-improvement
   ```

2. **Código limpo:**
   - Siga [CONTEXT.md](../../CONTEXT.md)
   - Teste localmente antes
   - Adicione type hints

3. **Commit semântico:**
   ```bash
   git commit -m "feat: adicionar suporte a paginação com cursor"
   ```

4. **Push & PR:**
   ```bash
   git push origin feature/scraper-improvement
   ```

---

## 📚 Referências

- [Beautiful Soup Docs](https://www.crummy.com/software/BeautifulSoup/)
- [Playwright Docs](https://playwright.dev/python/)
- [Azure Container Registry](https://learn.microsoft.com/en-us/azure/container-registry/)
- [CONTEXT.md](../../CONTEXT.md) - Regras do projeto

