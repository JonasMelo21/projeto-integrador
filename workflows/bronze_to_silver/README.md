# Bronze → Silver Workflow

Este workflow lê dados JSON brutos de `bronze/raw/` ou de uma pasta local, normaliza os campos e grava Parquet limpo em `silver/cleaned/`.

## O que ele faz

- lê arquivos JSON brutos
- normaliza campos numéricos (`preco`, `area`, `quartos`, `suites`, `vagas`, `banheiros`)
- calcula campos derivados (`preco_por_m2`, `descricao_len`, `titulo_len`)
- mantém `descricao` inteira
- descarta URL do output Silver
- escreve Parquet particionado por `process_date`
- grava registros inválidos em `silver/rejected/`

## Executar localmente

1. Crie `workflows/bronze_to_silver/sample_data/imoveis_sample.json` ou aponte `LOCAL_JSON_DIR` para um diretório com JSONs.
2. Execute:

```bash
cd workflows/bronze_to_silver
LOCAL_JSON_DIR=./sample_data OUTPUT_PATH=./silver/cleaned REJECTED_PATH=./silver/rejected python main.py
```

## Executar em Docker

```bash
cd workflows/bronze_to_silver
"/mnt/c/Program Files/Docker/Docker/resources/bin/docker" build -t bronze-to-silver:latest .
"/mnt/c/Program Files/Docker/Docker/resources/bin/docker" run --rm -e LOCAL_JSON_DIR=./sample_data -e OUTPUT_PATH=./silver/cleaned -e REJECTED_PATH=./silver/rejected -v "$(pwd)/sample_data:/app/sample_data" -v "$(pwd)/silver:/app/silver" bronze-to-silver:latest
```

## Variáveis de ambiente

- `LOCAL_JSON_DIR` - diretório local de arquivos JSON (uso de desenvolvimento)
- `USE_AZURE` - `true` para ler de Azure Blob Storage
- `STORAGE_ACCOUNT_NAME` - conta ADLS Gen2
- `CONTAINER_NAME` - container (default `bronze`)
- `BLOB_PREFIX` - prefixo de blob (default `raw/`)
- `OUTPUT_PATH` - caminho de saída Parquet (default `./silver/cleaned`)
- `REJECTED_PATH` - caminho de rejeição (default `./silver/rejected`)
- `PIPELINE_VERSION` - versão do pipeline
