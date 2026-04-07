# Guia de Uso - Scraper de Imóveis DFimoveis

> **Parte da Sprint 2** (Epic 2.1 - Vitrine e Scraping Base) - Consulte [../CONTEXT.md](../CONTEXT.md) para regras gerais e [../README.md](../README.md) para visão geral.

## 📋 Visão Geral

O scraper extrai dados de imóveis para aluguel do site **DFimoveis.com.br**, coletando informações estruturadas sobre localização, preço, características e contato.

**Principais Features:**
- ✅ Paginação automática (múltiplas páginas sem duplicatas)
- ✅ ID hexadecimal único por imóvel (SHA-256, 12 chars)
- ✅ Exportação em CSV e JSON
- ✅ Resiliente a timeouts e mudanças de layout

---

## 🚀 Quick Start

### Instalação de Dependências

```bash
cd "Projeto Integrador III 2.0"
uv sync --group scraping
```

### Execução Básica

```bash
uv run scrapper/scrapper.py
```

Resultado: `data/imoveis.json` e `data/imoveis.csv`

---

## 📊 Dados Extraídos

O scraper coleta as seguintes informações para cada imóvel:

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `id_hex` | string | ID único SHA-256 (12 chars) | `7c2bf7dac4f5` |
| `titulo` | string | Localização completa | SMPW Quadra 4 Conjunto 2, PARK WAY, BRASILIA |
| `url` | string | Link direto para o imóvel | https://www.dfimoveis.com.br/imovel/... |
| `preco` | string | Valor mensal do aluguel | 26.900 |
| `descricao` | string | Descrição resumida (max 200 chars) | Encante-se com esta belíssima casa... |
| `quartos` | string | Quantidade de quartos | 3 Quartos |
| `suites` | string | Quantidade de suítes | 3 Suítes |
| `vagas` | string | Vagas de garagem | 4 Vagas |
| `area` | string | Metragem (se disponível) | N/A |
| `imagem` | string | URL da imagem principal | https://img.dfimoveis.com.br/... |
| `imobiliaria` | string | Nome da imobiliária | Neves Teixeira Imóveis |
| `data_extracao` | string | ISO timestamp da coleta | 2026-04-07T06:05:27.120767 |

---

## 🎛️ Opções de Linha de Comando

```bash
uv run scrapper/scrapper.py [URL] [OPÇÕES]
```

### Argumentos Posicionais

| Argumento | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `URL` | string | `https://www.dfimoveis.com.br/aluguel/df/todos/imoveis` | URL da página a raspar |

### Parâmetros Opcionais

```bash
--timeout-ms MS
  Timeout para carregamento da página em milissegundos
  Padrão: 45000 (45 segundos)
  Uso: --timeout-ms 60000

--format {csv,json,both}
  Formato dos dados de saída
  Padrão: both
  Valores:
    csv   → Salva apenas em CSV
    json  → Salva apenas em JSON
    both  → Salva em ambos os formatos

--num-pages N
  Número de páginas a extrair (com suporte a paginação automática)
  Padrão: 1
  Uso: --num-pages 3 (extrai páginas 1, 2 e 3)
```

---

## 💡 Exemplos de Uso

### 1. Extrair todos os dados (padrão, 1 página)
```bash
uv run scrapper/scrapper.py
```

**Saída:**
```
🔍 Iniciando scraping
   URL: https://www.dfimoveis.com.br/aluguel/df/todos/imoveis
   Páginas: 1
   Formato: json

📄 Extraindo página 1/1: https://www.dfimoveis.com.br/aluguel/df/todos/imoveis
✓ Página carregada com sucesso
✓ Imóveis carregados
✓ 30 imóveis encontrados nesta página
  → 30 novos, 0 duplicados

✓ 30 imóveis ÚNICOS extraídos com sucesso!
✓ Dados salvos em: .../data/imoveis.json
✓ Dados salvos em: .../data/imoveis.csv

📊 Resumo dos primeiros imóveis:
1. SMPW Quadra 4 Conjunto 2, PARK WAY, BRASILIA (ID: 7c2bf7dac4f5)
   Preço: R$  26.900
   3 Quartos | 3 Suítes | 4 Vagas | N/A
```

### 2. Extrair 3 páginas (com deduplicação automática)
```bash
uv run scrapper/scrapper.py --num-pages 3
```

**Comportamento:**
- Página 1: Extrai 30 imóveis
- Página 2: Se houver novos, adiciona; se duplicados, ignora
- Página 3: Idem
- **Total Único:** Apenas imóveis com `id_hex` único

### 3. Extrair apenas em JSON com timeout maior
```bash
uv run scrapper/scrapper.py --format json --timeout-ms 60000
```

### 4. Extrair de um bairro específico (Lago Sul)
```bash
uv run scrapper/scrapper.py "https://www.dfimoveis.com.br/aluguel/df/lago-sul/imoveis"
```

### 5. Extrair apenas em CSV, 2 páginas
```bash
uv run scrapper/scrapper.py --format csv --num-pages 2
```

### 6. Combinação completa
```bash
uv run scrapper/scrapper.py "https://www.dfimoveis.com.br/aluguel/df/asa-norte/imoveis" \
  --num-pages 5 \
  --format json \
  --timeout-ms 90000
```

---

## 📈 Exemplo de Dados Extraídos

### JSON
```json
{
  "id_hex": "7c2bf7dac4f5",
  "titulo": "SMPW Quadra 4 Conjunto 2, PARK WAY, BRASILIA",
  "url": "https://www.dfimoveis.com.br/imovel/casa-3-quartos-aluguel-park-way-brasilia-df-smpw-quadra-4-conjunto-2-1265544",
  "preco": " 26.900",
  "descricao": "NEVES TEIXEIRA IMÓVEIS ALUGA:\n\nEncante-se com esta belíssima casa localizada...",
  "quartos": "3 Quartos",
  "suites": "3 Suítes",
  "vagas": "4 Vagas",
  "area": "N/A",
  "imagem": "https://img.dfimoveis.com.br/fotos/1265544/521dc7a1feb3cf1ba77eaf7ec2dd612c.webp",
  "imobiliaria": "Neves Teixeira Imóveis",
  "data_extracao": "2026-04-07T06:05:27.120767"
}
```

### CSV (primeiras linhas)
```csv
id_hex,titulo,url,preco,descricao,quartos,suites,vagas,area,imagem,imobiliaria,data_extracao
7c2bf7dac4f5,"SMPW Quadra 4 Conjunto 2, PARK WAY, BRASILIA",https://www.dfimoveis.com.br/imovel/..., 26.900,"NEVES TEIXEIRA IMÓVEIS...",3 Quartos,3 Suítes,4 Vagas,N/A,https://img.dfimoveis.com.br/...,Neves Teixeira Imóveis,2026-04-07T06:05:27.120767
```

---

## 🔑 Entendendo o ID Hexadecimal

Cada imóvel recebe um `id_hex` único e **determinístico**:

- **Gerado por:** SHA-256 da URL do imóvel
- **Formato:** 12 primeiros caracteres hexadecimais
- **Benefício:** Mesma URL = Sempre o mesmo ID (permite deduplicação segura)

```python
# Exemplo de geração
url = "https://www.dfimoveis.com.br/imovel/casa-3-quartos-aluguel-park-way-..."
sha256_hash = hashlib.sha256(url.encode()).hexdigest()
id_hex = sha256_hash[:12]  # "7c2bf7dac4f5"
```

**Uso na prática:**
- Rastrear imóveis únicos em múltiplas execuções
- Evitar duplicatas automaticamente
- Integrar com banco de dados (chave primária ou índice único)

---

## 📊 Paginação e Deduplicação

O scraper suporta **múltiplas páginas com deduplicação automática**:

```bash
uv run scrapper/scrapper.py --num-pages 3
```

**Fluxo:**
1. Página 1 (`?page=1`): 30 imóveis extraídos, 0 duplicados
2. Página 2 (`?page=2`): Se houver sobreposição, ignora duplicatas
3. Página 3 (`?page=3`): Continua filtrando...

**Resultado:** Total ÚNICO de imóveis (sem repetições)

> ⚠️ **Nota:** DFimoveis pode retornar os mesmos imóveis em todas as páginas. O scraper detecta isso comparando `id_hex` e reporta no stdout.

---

## 📁 Estrutura de Saída

Os dados são salvos em `/data/`:

```
data/
├── imoveis.csv          # Formato tabular (Excel-friendly)
└── imoveis.json         # Formato JSON estruturado
```

**Carregamento dos dados:**
```python
import pandas as pd
import json

# CSV
df = pd.read_csv("data/imoveis.csv")

# JSON
with open("data/imoveis.json", "r", encoding="utf-8") as f:
    properties = json.load(f)
```

---

## ⚠️ Considerações Importantes

### Respeito ao Website
- ✅ O scraper carrega a página normalmente (sem headers falsos)
- ✅ Aguarda JS renderizar antes de extrair
- ✅ Respeita timeouts e limites de conexão

### Performance
- ⏱️ Tempo típico: 5-10 segundos por página
- 🔄 Cada página abre um novo navegador Chromium
- 💾 Aumentar `--timeout-ms` se a conexão for lenta

### Limitações
- Descrições limitadas a 200 caracteres
- Metragem (`area`) pode estar como `N/A`
- Imagens podem estar em cache ou quebradas

---

## 🔧 Troubleshooting

### Erro: "Módulo não encontrado"
```bash
# Solução
uv sync --group scraping
```

### Erro: "Timeout ao carregar página"
```bash
# Aumentar timeout
uv run scrapper/scrapper.py --timeout-ms 90000
```

### Erro: "Nenhum imóvel encontrado"
**Checklist:**
- [ ] URL é válida?
- [ ] Conexão com internet está ok?
- [ ] Website alterou sua estrutura HTML?
- [ ] Tentar com `--timeout-ms 60000`?

### Dados estão vazios (`N/A`)
- [ ] O website pode ter alterado suas classes CSS
- [ ] Inspecionar o HTML do site e atualizar os seletores

---

## 📝 Próximas Melhorias

- [ ] Suporte a filtros (preço mín/máx, bairro, etc.)
- [ ] Exportação em Parquet para Databricks
- [ ] Cache local de dados já extraídos
- [ ] Integração direto com ADLS Gen2
- [ ] Logs estruturados (JSON logging)

---

## 📄 Referências

- **Regras de Codificação:** [../CONTEXT.md](../CONTEXT.md)
- **Visão Geral do Projeto:** [../README.md](../README.md)
- **Código-fonte:** [../scrapper/scrapper.py](../scrapper/scrapper.py)

---

**Última atualização:** 2026-04-07  
**Versão:** 1.1.0 (Planejado para Sprint 2)  
**Status:** 🔄 Em Desenvolvimento (Sprint 2 - Epic 2.1)
