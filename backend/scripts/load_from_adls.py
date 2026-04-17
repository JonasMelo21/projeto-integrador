"""
Script para popular SQLite com dados do ADLS (Azure Data Lake Storage)

Uso:
    python scripts/load_from_adls.py  # Carrega dados do ADLS
    
O script espera que você tenha configurado:
    - AZURE_STORAGE_ACCOUNT: Nome da conta de storage
    - AZURE_STORAGE_KEY: Chave de acesso
    - ADLS_CONTAINER: Nome do container (ex: 'bronze')
    - ADLS_PATH: Caminho no ADLS (ex: 'raw/')
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar o diretório pai ao path para importar os módulos do backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure.storage.filedatalake import DataLakeServiceClient
from database import SessionLocal
from models import FactImovel, DimImobiliaria, DimLocal
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from database import init_db

# Carregar variáveis do arquivo .env.adls
env_path = Path(__file__).parent / ".env.adls"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Carregando configurações de: {env_path}")
else:
    print(f"⚠️  Arquivo {env_path} não encontrado, usando variáveis de ambiente")

# Inicializar banco de dados
print("🔧 Criando tabelas se não existirem...")
init_db()
print("✅ Banco de dados inicializado")

# Configuração ADLS
STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT", "seu_storage_account")
STORAGE_KEY = os.getenv("AZURE_STORAGE_KEY", "sua_chave")
CONTAINER = os.getenv("ADLS_CONTAINER", "bronze")
PATH = os.getenv("ADLS_PATH", "raw/")

def get_adls_client():
    """Inicializa cliente ADLS"""
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={STORAGE_ACCOUNT};AccountKey={STORAGE_KEY};EndpointSuffix=core.windows.net"
    return DataLakeServiceClient.from_connection_string(connection_string)

def list_json_files():
    """Lista arquivos JSON no ADLS"""
    try:
        client = get_adls_client()
        file_system = client.get_file_system_client(CONTAINER)
        
        files = []
        for path in file_system.get_paths(PATH):
            if path.name.endswith('.json'):
                files.append(path.name)
        
        return files
    except Exception as e:
        print(f"❌ Erro ao listar arquivos do ADLS: {e}")
        return []

def download_json_file(file_path):
    """Baixa arquivo JSON do ADLS"""
    try:
        client = get_adls_client()
        file_system = client.get_file_system_client(CONTAINER)
        file_client = file_system.get_file_client(file_path)
        
        data = file_client.download_file().readall()
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        print(f"❌ Erro ao baixar {file_path}: {e}")
        return None

def extract_location(item):
    """Extrai localização do item"""
    if isinstance(item.get('imobiliaria'), dict):
        city = item['imobiliaria'].get('cidade', 'Brasília')
    else:
        city = 'Brasília'
    
    bairro = item.get('bairro', item.get('descricao', 'DF')).split(',')[-1].strip()
    return bairro, city, 'DF'

def parse_price(price_str):
    """Parse preço"""
    if isinstance(price_str, (int, float)):
        return float(price_str)
    if isinstance(price_str, str):
        try:
            return float(price_str.replace('R$', '').replace('.', '').replace(',', '.').strip())
        except:
            return 0.0
    return 0.0

def parse_area(area_str):
    """Parse área"""
    if isinstance(area_str, (int, float)):
        return float(area_str)
    if isinstance(area_str, str):
        try:
            return float(area_str.replace('m²', '').replace('.', '').replace(',', '.').strip())
        except:
            return 0.0
    return 0.0

def parse_rooms(rooms_str):
    """Parse número de quartos"""
    if isinstance(rooms_str, int):
        return rooms_str
    if isinstance(rooms_str, str):
        try:
            return int(rooms_str.split()[0])
        except:
            return 0
    return 0

def load_from_adls():
    """Carrega dados do ADLS para SQLite"""
    print(f"🔍 Buscando arquivos JSON no ADLS...")
    print(f"   Storage: {STORAGE_ACCOUNT}")
    print(f"   Container: {CONTAINER}")
    print(f"   Path: {PATH}")
    
    files = list_json_files()
    if not files:
        print("❌ Nenhum arquivo JSON encontrado no ADLS")
        return
    
    print(f"✅ Encontrados {len(files)} arquivos")
    
    db = SessionLocal()
    total_loaded = 0
    
    for file_path in files:
        print(f"\n📥 Carregando {file_path}...")
        
        data = download_json_file(file_path)
        if not data:
            continue
        
        # Converter para lista se for dict com lista dentro
        items = data if isinstance(data, list) else [data]
        
        for item in items:
            try:
                # Extrair dados
                id_hex = item.get('id', f"id_{datetime.now().timestamp()}")
                titulo = item.get('titulo', 'Sem título')
                url = item.get('url', '')
                preco = parse_price(item.get('preco', 0))
                area_m2 = parse_area(item.get('area', 0))
                quartos = parse_rooms(item.get('quartos', 0))
                banheiros = parse_rooms(item.get('banheiros', 0))
                vagas = parse_rooms(item.get('vagas', 0))
                imagem = item.get('imagem', '')
                descricao = item.get('descricao', '')
                imobiliaria_nome = item.get('imobiliaria', 'Indefinido')
                bairro, cidade, uf = extract_location(item)
                
                # Verificar se já existe
                existing = db.query(FactImovel).filter(FactImovel.id_hex == id_hex).first()
                if existing:
                    print(f"  ⏭️  {titulo} (já existe)")
                    continue
                
                # Criar ou buscar dimensões
                imobiliaria = db.query(DimImobiliaria).filter(
                    DimImobiliaria.nome_empresa == imobiliaria_nome
                ).first()
                if not imobiliaria:
                    imobiliaria = DimImobiliaria(nome_empresa=imobiliaria_nome)
                    db.add(imobiliaria)
                    db.flush()
                
                local = db.query(DimLocal).filter(
                    DimLocal.bairro == bairro,
                    DimLocal.cidade == cidade
                ).first()
                if not local:
                    local = DimLocal(bairro=bairro, cidade=cidade, uf=uf)
                    db.add(local)
                    db.flush()
                
                # Criar imóvel
                imovel = FactImovel(
                    id_hex=id_hex,
                    titulo=titulo,
                    url=url,
                    preco=preco,
                    area_m2=area_m2,
                    quartos=quartos,
                    banheiros=banheiros,
                    vagas=vagas,
                    imagem=imagem,
                    descricao=descricao,
                    id_imobiliaria_fk=imobiliaria.id_imobiliaria,
                    id_local_fk=local.id_local,
                    data_extracao=datetime.now()
                )
                db.add(imovel)
                total_loaded += 1
                print(f"  ✅ {titulo} (R$ {preco})")
                
            except IntegrityError as e:
                db.rollback()
                print(f"  ⚠️  Duplicado: {titulo}")
            except Exception as e:
                db.rollback()
                print(f"  ❌ Erro: {e}")
        
        db.commit()
    
    print(f"\n{'='*60}")
    print(f"✅ Total carregado: {total_loaded} imóveis")
    print(f"📊 Resumo do banco:")
    
    total = db.query(FactImovel).count()
    imobiliarias = db.query(DimImobiliaria).count()
    locais = db.query(DimLocal).count()
    
    print(f"   - Imóveis: {total}")
    print(f"   - Imobiliárias: {imobiliarias}")
    print(f"   - Locais: {locais}")
    
    db.close()

if __name__ == "__main__":
    load_from_adls()
