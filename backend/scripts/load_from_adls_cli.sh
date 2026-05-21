#!/bin/bash

################################################################################
# Script: load_from_adls_cli.sh
# Descrição: Usa Azure CLI para baixar arquivos JSON do ADLS (bronze/raw)
#            e insere os imóveis no banco de dados SQLite
#
# Uso: ./load_from_adls_cli.sh
################################################################################

set -e  # Parar em erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# 1. CARREGANDO CONFIGURAÇÕES
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
ENV_FILE="$SCRIPT_DIR/.env.adls"

echo -e "${BLUE}📂 Diretório do script: $SCRIPT_DIR${NC}"
echo -e "${BLUE}📂 Raiz do projeto: $PROJECT_ROOT${NC}"

if [[ ! -f "$ENV_FILE" ]]; then
    echo -e "${RED}❌ Arquivo $ENV_FILE não encontrado!${NC}"
    exit 1
fi

# Carregar variáveis do ambiente
export $(grep -v '^#' "$ENV_FILE" | xargs)

echo -e "${GREEN}✅ Configurações carregadas de: $ENV_FILE${NC}"
echo -e "${BLUE}   Storage Account: $AZURE_STORAGE_ACCOUNT${NC}"
echo -e "${BLUE}   Container: $ADLS_CONTAINER${NC}"
echo -e "${BLUE}   Path: $ADLS_PATH${NC}"

# ============================================================================
# 2. CRIAR DIRETÓRIO TEMPORÁRIO
# ============================================================================

TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT  # Limpar ao sair

echo -e "${BLUE}📁 Diretório temporário: $TEMP_DIR${NC}"

# ============================================================================
# 3. AUTENTICAR NO AZURE CLI (se necessário)
# ============================================================================

echo -e "\n${YELLOW}🔐 Verificando autenticação do Azure CLI...${NC}"

if ! az account show &>/dev/null; then
    echo -e "${YELLOW}⚠️  Não autenticado. Fazendo login...${NC}"
    az login
else
    CURRENT_USER=$(az account show --query user.name -o tsv)
    echo -e "${GREEN}✅ Autenticado como: $CURRENT_USER${NC}"
fi

# ============================================================================
# 4. LISTAR ARQUIVOS JSON DO ADLS
# ============================================================================

echo -e "\n${YELLOW}🔍 Buscando arquivos JSON no ADLS...${NC}"

# Usar Azure CLI para listar blobs (com limpeza de line endings)
BLOBS=$(az storage blob list \
    --account-name "$AZURE_STORAGE_ACCOUNT" \
    --account-key "$AZURE_STORAGE_KEY" \
    --container-name "$ADLS_CONTAINER" \
    --prefix "$ADLS_PATH" \
    --query "[?ends_with(name, '.json')].name" \
    -o tsv | tr -d '\r')

if [[ -z "$BLOBS" ]]; then
    echo -e "${RED}❌ Nenhum arquivo JSON encontrado no caminho: $ADLS_CONTAINER/$ADLS_PATH${NC}"
    exit 1
fi

# Contar arquivos
FILE_COUNT=$(echo "$BLOBS" | grep -c "." || true)
echo -e "${GREEN}✅ Encontrados $FILE_COUNT arquivos JSON${NC}"

# ============================================================================
# 5. BAIXAR ARQUIVOS JSON
# ============================================================================

echo -e "\n${YELLOW}📥 Baixando arquivos do ADLS...${NC}"

for blob in $BLOBS; do
    filename=$(basename "$blob")
    echo -e "${BLUE}   → Baixando: $filename${NC}"
    
    az storage blob download \
        --account-name "$AZURE_STORAGE_ACCOUNT" \
        --account-key "$AZURE_STORAGE_KEY" \
        --container-name "$ADLS_CONTAINER" \
        --name "$blob" \
        --file "$TEMP_DIR/$filename" \
        --no-progress
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}     ✅ Download concluído${NC}"
    else
        echo -e "${RED}     ❌ Erro ao baixar${NC}"
    fi
done

# ============================================================================
# 6. EXIBIR ARQUIVOS BAIXADOS
# ============================================================================

echo -e "\n${YELLOW}📋 Arquivos baixados:${NC}"
ls -lh "$TEMP_DIR"

# ============================================================================
# 7. EXECUTAR SCRIPT PYTHON PARA INSERIR NO SQLITE
# ============================================================================

echo -e "\n${YELLOW}💾 Inserindo dados no SQLite...${NC}"

cd "$SCRIPT_DIR/.."

python3 scripts/load_from_adls_cli.py "$TEMP_DIR"

# ============================================================================
# 8. EXIBIR RESULTADO FINAL
# ============================================================================

echo -e "\n${GREEN}✨ Processo concluído!${NC}"
echo -e "${GREEN}🎉 Imóveis do ADLS foram inseridos com sucesso no SQLite!${NC}\n"
