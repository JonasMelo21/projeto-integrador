"""Load JSON data from scraper into SQLite"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import SessionLocal, init_db
from models import FactImovel, DimImobiliaria, DimLocal


def extract_location(titulo: str) -> tuple[str, str]:
    """Extract bairro and cidade from titulo
    Example: "Condomínio Mini Chacáras do Lago Sul, JARDIM BOTANICO, BRASILIA"
    Returns: ("JARDIM BOTANICO", "BRASILIA")
    """
    parts = titulo.split(",")
    if len(parts) >= 3:
        bairro = parts[-2].strip()
        cidade = parts[-1].strip()
    elif len(parts) == 2:
        bairro = parts[-1].strip()
        cidade = "BRASILIA"
    else:
        bairro = "SEM BAIRRO"
        cidade = "BRASILIA"
    
    return bairro, cidade


def parse_price(price_str: str) -> float:
    """Parse price string to float
    Example: " 15.000" -> 15000.0
    """
    if not price_str or price_str == "N/A":
        return 0.0
    
    # Remove spaces and convert
    price_str = price_str.strip().replace(".", "").replace(",", ".")
    try:
        return float(price_str)
    except:
        return 0.0


def parse_area(area_str: str) -> float:
    """Parse area string to float
    Example: "340 m²" -> 340.0
    """
    if not area_str:
        return 0.0
    
    # Remove "m²" and convert
    area_str = area_str.replace("m²", "").strip()
    try:
        return float(area_str)
    except:
        return 0.0


def parse_rooms(room_str: str) -> int:
    """Parse room count from string
    Example: "5 Quartos" -> 5, "N/A" -> 0
    """
    if not room_str or room_str == "N/A":
        return 0
    
    # Extract number
    import re
    match = re.search(r'\d+', room_str)
    return int(match.group()) if match else 0


def load_json_to_sqlite(json_path: str):
    """Load JSON file and populate SQLite"""
    
    # Initialize database
    print("🔧 Initializing database schema...")
    init_db()
    
    # Read JSON
    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return
    
    print(f"📖 Reading JSON from: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Found {len(data)} properties in JSON")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Track counts
        imobiliarias_created = 0
        locais_created = 0
        imoveis_created = 0
        imoveis_skipped = 0
        
        # Process each property
        for imovel_data in data:
            id_hex = imovel_data.get("id_hex")
            
            # Check if already exists (idempotent)
            existing = db.query(FactImovel).filter(
                FactImovel.id_hex == id_hex
            ).first()
            
            if existing:
                imoveis_skipped += 1
                continue
            
            # Get or create imobiliaria
            imobiliaria_nome = imovel_data.get("imobiliaria", "UNKNOWN").strip()
            imobiliaria = db.query(DimImobiliaria).filter(
                DimImobiliaria.nome_empresa == imobiliaria_nome
            ).first()
            
            if not imobiliaria:
                imobiliaria = DimImobiliaria(nome_empresa=imobiliaria_nome)
                db.add(imobiliaria)
                db.flush()
                imobiliarias_created += 1
            
            # Get or create local
            bairro, cidade = extract_location(imovel_data.get("titulo", ""))
            local = db.query(DimLocal).filter(
                DimLocal.bairro == bairro,
                DimLocal.cidade == cidade
            ).first()
            
            if not local:
                local = DimLocal(bairro=bairro, cidade=cidade, uf="DF")
                db.add(local)
                db.flush()
                locais_created += 1
            
            # Create fact record
            imovel = FactImovel(
                id_hex=id_hex,
                id_imobiliaria_fk=imobiliaria.id_imobiliaria,
                id_local_fk=local.id_local,
                titulo=imovel_data.get("titulo"),
                url=imovel_data.get("url"),
                preco=parse_price(imovel_data.get("preco")),
                area_m2=parse_area(imovel_data.get("area")),
                quartos=parse_rooms(imovel_data.get("quartos")),
                banheiros=parse_rooms(imovel_data.get("suites")),
                vagas=parse_rooms(imovel_data.get("vagas")),
                imagem=imovel_data.get("imagem", ""),
                descricao=imovel_data.get("descricao", "")[:2000] if imovel_data.get("descricao") else None,
                data_extracao=datetime.fromisoformat(
                    imovel_data.get("data_extracao", datetime.utcnow().isoformat())
                ) if imovel_data.get("data_extracao") else datetime.utcnow()
            )
            
            db.add(imovel)
            imoveis_created += 1
        
        # Commit all changes
        db.commit()
        
        # Print summary
        print("\n✅ Load Complete!")
        print(f"   📦 Imobiliárias created: {imobiliarias_created}")
        print(f"   📍 Locais created: {locais_created}")
        print(f"   🏠 Imóveis created: {imoveis_created}")
        print(f"   ⏭️  Imóveis skipped (already exist): {imoveis_skipped}")
        
        # Final stats
        total_imoveis = db.query(FactImovel).count()
        total_imobiliarias = db.query(DimImobiliaria).count()
        total_locais = db.query(DimLocal).count()
        
        print(f"\n📊 Database Stats:")
        print(f"   Total imóveis: {total_imoveis}")
        print(f"   Total imobiliárias: {total_imobiliarias}")
        print(f"   Total locais: {total_locais}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Default: load from data/dados_imoveis.json
    json_file = "../../data/dados_imoveis.json"
    
    # Allow override via command line
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    # Convert to absolute path
    script_dir = Path(__file__).parent
    json_path = (script_dir / json_file).resolve()
    
    print(f"Loading from: {json_path}\n")
    load_json_to_sqlite(str(json_path))
