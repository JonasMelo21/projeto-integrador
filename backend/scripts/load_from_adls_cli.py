"""
Script Python para inserir imóveis do ADLS no SQLite
Executado após o script bash baixar os arquivos JSON
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import SessionLocal, init_db
from models import FactImovel, DimImobiliaria, DimLocal
from sqlalchemy.exc import IntegrityError


def parse_price(price_str):
    """Parse de preço com múltiplos formatos"""
    if isinstance(price_str, (int, float)):
        return float(price_str)
    if isinstance(price_str, str):
        try:
            cleaned = price_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(cleaned)
        except:
            return 0.0
    return 0.0


def parse_area(area_str):
    """Parse de área com múltiplos formatos"""
    if isinstance(area_str, (int, float)):
        return float(area_str)
    if isinstance(area_str, str):
        try:
            cleaned = area_str.replace('m²', '').replace('m2', '').replace('.', '').replace(',', '.').strip()
            return float(cleaned)
        except:
            return 0.0
    return 0.0


def parse_rooms(rooms_str):
    """Parse de número de quartos/banheiros"""
    if isinstance(rooms_str, int):
        return rooms_str
    if isinstance(rooms_str, str):
        try:
            return int(rooms_str.split()[0])
        except:
            return 0
    return 0


def extract_location(item):
    """Extrai localização do item"""
    if isinstance(item.get('imobiliaria'), dict):
        city = item['imobiliaria'].get('cidade', 'Brasília')
    else:
        city = 'Brasília'
    
    bairro = item.get('bairro', item.get('descricao', 'DF')).split(',')[-1].strip()
    return bairro, city, 'DF'


def load_json_files(temp_dir):
    """Carrega e processa arquivos JSON"""
    
    print("🔧 Inicializando banco de dados...")
    init_db()
    print("✅ Banco de dados pronto\n")
    
    json_files = list(Path(temp_dir).glob('*.json'))
    
    if not json_files:
        print("⚠️  Nenhum arquivo JSON encontrado em:", temp_dir)
        return
    
    print(f"📂 Encontrados {len(json_files)} arquivos JSON\n")
    
    db = SessionLocal()
    total_inserted = 0
    total_skipped = 0
    total_errors = 0
    
    for json_file in json_files:
        print(f"📥 Processando: {json_file.name}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Converter para lista se for dict único
            items = data if isinstance(data, list) else [data]
            
            for item in items:
                try:
                    # ID único
                    id_hex = item.get('id', f"id_{datetime.now().timestamp()}")
                    
                    # Verificar duplicata
                    existing = db.query(FactImovel).filter(FactImovel.id_hex == id_hex).first()
                    if existing:
                        print(f"  ⏭️  Imóvel já existe (ID: {id_hex})")
                        total_skipped += 1
                        continue
                    
                    # Extrair dados
                    titulo = item.get('titulo', 'Sem título')
                    url = item.get('url', '')
                    preco = parse_price(item.get('preco', 0))
                    area_m2 = parse_area(item.get('area', 0))
                    quartos = parse_rooms(item.get('quartos', 0))
                    banheiros = parse_rooms(item.get('banheiros', 0))
                    vagas = parse_rooms(item.get('vagas', 0))
                    imagem = item.get('imagem', '')
                    descricao = item.get('descricao', '')
                    
                    # Nome da imobiliária
                    if isinstance(item.get('imobiliaria'), dict):
                        imobiliaria_nome = item['imobiliaria'].get('nome', 'Indefinido')
                    else:
                        imobiliaria_nome = str(item.get('imobiliaria', 'Indefinido'))
                    
                    # Localização
                    bairro, cidade, uf = extract_location(item)
                    
                    # Criar ou buscar imobiliária
                    imobiliaria = db.query(DimImobiliaria).filter(
                        DimImobiliaria.nome_empresa == imobiliaria_nome
                    ).first()
                    
                    if not imobiliaria:
                        imobiliaria = DimImobiliaria(nome_empresa=imobiliaria_nome)
                        db.add(imobiliaria)
                        db.flush()
                    
                    # Criar ou buscar local
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
                    db.commit()
                    
                    titulo_curto = titulo[:45] if titulo else "Sem título"
                    print(f"  ✅ Inserido: {titulo_curto}... (R$ {preco:.0f}, {area_m2:.0f}m²)")
                    total_inserted += 1
                    
                except IntegrityError:
                    db.rollback()
                    total_skipped += 1
                except Exception as e:
                    db.rollback()
                    print(f"  ❌ Erro ao processar item: {str(e)}")
                    total_errors += 1
        
        except json.JSONDecodeError as e:
            print(f"  ❌ Erro ao ler JSON: {e}")
            total_errors += 1
        except Exception as e:
            print(f"  ❌ Erro geral: {e}")
            total_errors += 1
    
    db.close()
    
    # Resumo
    print(f"\n{'='*70}")
    print(f"{'RESUMO DA INSERÇÃO':^70}")
    print(f"{'='*70}")
    print(f"✅ Inseridos:   {total_inserted} imóveis")
    print(f"⏭️  Duplicados:  {total_skipped} imóveis")
    print(f"❌ Erros:       {total_errors}")
    print(f"{'='*70}\n")
    
    # Estatísticas do banco
    print_database_stats()


def print_database_stats():
    """Exibe estatísticas do banco de dados"""
    db = SessionLocal()
    
    try:
        total_imoveis = db.query(FactImovel).count()
        total_imobiliarias = db.query(DimImobiliaria).count()
        total_locais = db.query(DimLocal).count()
        
        print(f"📊 Estatísticas do banco de dados:")
        print(f"  • Total de imóveis: {total_imoveis}")
        print(f"  • Total de imobiliárias: {total_imobiliarias}")
        print(f"  • Total de locais/bairros: {total_locais}")
        
        # Top imobiliárias
        from sqlalchemy import func
        top_imobs = db.query(
            DimImobiliaria.nome_empresa,
            func.count(FactImovel.id_imovel).label('count')
        ).join(FactImovel).group_by(DimImobiliaria.id_imobiliaria).order_by(
            func.count(FactImovel.id_imovel).desc()
        ).limit(5).all()
        
        if top_imobs:
            print(f"\n  📈 Top 5 Imobiliárias:")
            for i, (nome, count) in enumerate(top_imobs, 1):
                print(f"     {i}. {nome}: {count} imóveis")
        
        # Preço médio
        avg_price = db.query(func.avg(FactImovel.preco)).scalar() or 0
        min_price = db.query(func.min(FactImovel.preco)).scalar() or 0
        max_price = db.query(func.max(FactImovel.preco)).scalar() or 0
        
        print(f"\n  💰 Análise de Preços (R$):")
        print(f"     Mínimo:  R$ {min_price:,.2f}")
        print(f"     Médio:   R$ {avg_price:,.2f}")
        print(f"     Máximo:  R$ {max_price:,.2f}")
        
    finally:
        db.close()


if __name__ == '__main__':
    temp_dir = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
    load_json_files(temp_dir)
