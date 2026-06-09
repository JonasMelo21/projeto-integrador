# Bronze → Silver Workflow

Este workflow lê dados JSON brutos de `bronze/raw/` ou de uma pasta local, normaliza os campos e grava Parquet limpo em `silver/cleaned/`.

## O que ele faz

- lê arquivos JSON brutos (um específico OU todos, dependendo de `INPUT_FILE`)
- normaliza campos numéricos (`preco`, `area`, `quartos`, `suites`, `vagas`, `banheiros`)
- calcula campos derivados (`preco_por_m2`, `descricao_len`, `titulo_len`)
- mantém `descricao` inteira
- descarta URL do output Silver
- escreve Parquet particionado por `process_date`
- grava registros inválidos em `silver/rejected/`

## Modos de Operação

### Modo 1: Processa arquivo ESPECÍFICO (para Data Factory)

**Ideal para pipeline orquestrado**: Scraper roda, passa o nome do arquivo → Workflow processa APENAS esse arquivo.

```bash
# Local
cd workflows/bronze_to_silver
INPUT_FILE="imoveis_20260607_141126.json" \
LOCAL_JSON_DIR=./sample_data \
OUTPUT_PATH=./silver/cleaned \
REJECTED_PATH=./silver/rejected \
python main.py
```

```bash
# Azure
INPUT_FILE="imoveis_20260607_141126.json" \
USE_AZURE=true \
STORAGE_ACCOUNT_NAME=rentmasterstorageaccount \
CONTAINER_NAME=bronze \
python main.py
```

### Modo 2: Processa TODOS os arquivos (legado/compatibilidade)

```bash
# Local
cd workflows/bronze_to_silver
LOCAL_JSON_DIR=./sample_data OUTPUT_PATH=./silver/cleaned REJECTED_PATH=./silver/rejected python main.py
```

```bash
# Azure
USE_AZURE=true python main.py
```

## Executar em Docker

```bash
cd workflows/bronze_to_silver
docker build -t bronze-to-silver:latest .
docker run --rm \
  -e INPUT_FILE="imoveis_20260607_141126.json" \
  -e USE_AZURE=true \
  -e STORAGE_ACCOUNT_NAME=rentmasterstorageaccount \
  bronze-to-silver:latest
```

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `INPUT_FILE` | Nome do arquivo específico a processar (ex: `imoveis_20260607_141126.json`) | `` (vazio = processa todos) |
| `LOCAL_JSON_DIR` | Diretório local com arquivos JSON | `` |
| `USE_AZURE` | `true` para ler de Azure Blob Storage | `false` |
| `STORAGE_ACCOUNT_NAME` | Conta ADLS Gen2 | `rentmasterstorageaccount` |
| `CONTAINER_NAME` | Container no Blob Storage | `bronze` |
| `BLOB_PREFIX` | Prefixo dos blobs (ex: `raw/`) | `raw/` |
| `OUTPUT_PATH` | Caminho de saída Parquet | `./silver/cleaned` |
| `REJECTED_PATH` | Caminho para rejeições | `./silver/rejected` |
| `PIPELINE_VERSION` | Versão do pipeline | `1.0` |
| `LOG_LEVEL` | Nível de log | `INFO` |

## Arquitetura para Data Factory

```mermaid
Scraper (Container)
    ↓ (sucesso)
    ├─ Salva JSON em bronze/raw/imoveis_YYYYMMDD_HHMMSS.json
    └─ Output: "imoveis_YYYYMMDD_HHMMSS.json"
         ↓
    Data Factory Pipeline Activity 2: Bronze→Silver
         ↓ (passa INPUT_FILE="imoveis_YYYYMMDD_HHMMSS.json")
    Workflow (Container)
         ├─ Lê APENAS esse arquivo de bronze/raw/
         ├─ Transforma e deduplica
         └─ Salva em silver/cleaned/data.parquet (particionado por date)
```

## Campos do Output (Silver)

```json
{
  "id_hex": "ba6efcef27cd",
  "titulo": "SMPW Quadra 16 Conjunto 4, PARK WAY, BRASILIA",
  "descricao": "...",
  "imobiliaria": "Coemi Imóveis",
  "preco": 29000.0,
  "area_m2": 800.0,
  "preco_por_m2": 36.25,
  "quartos": 4,
  "suites": 4,
  "vagas": 4,
  "banheiros": null,
  "descricao_len": 145,
  "titulo_len": 45,
  "data_extracao": "2026-06-07T14:11:11.155194",
  "process_date": "2026-06-07",
  "source_file": "imoveis_20260607_141126.json",
  "ingestion_datetime": "2026-06-07T14:15:00.123456",
  "pipeline_version": "1.0"
}
```

