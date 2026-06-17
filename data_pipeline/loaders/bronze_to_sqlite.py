"""Load JSON data from scraper into SQLite — Drop & Create + Batch Load"""
import json
import sys
import re
from pathlib import Path
from datetime import datetime

# Add project root to path (para importar backend)
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import SessionLocal, engine
from backend.models import Base, FactImovel, DimImobiliaria, DimLocal

BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"


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


def load_json_to_sqlite():
    """Drop all tables, recreate, then batch-load all JSON files from bronze."""

    # 1. Drop & Create
    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("🔧 Recreating tables...")
    Base.metadata.create_all(bind=engine)

    # 2. Leitura em lote — todos os JSON da bronze
    json_files = sorted(BRONZE_DIR.glob("*.json"))
    if not json_files:
        print(f"❌ Nenhum arquivo JSON encontrado em: {BRONZE_DIR}")
        return

    print(f"📂 {len(json_files)} arquivo(s) encontrado(s) em bronze:")
    all_data = []
    for filepath in json_files:
        print(f"   - {filepath.name}")
        with open(filepath, "r", encoding="utf-8") as f:
            all_data.extend(json.load(f))

    print(f"📊 Total de registros lidos: {len(all_data)}")
    # Deduplica por id_imovel, mantendo o mais recente (último arquivo processado)
    seen: dict = {}
    for item in all_data:
        key = item.get("id_imovel")
        if key:
            seen[key] = item
    all_data = list(seen.values())
    print(f"📊 Após deduplicação: {len(all_data)} imóveis únicos\n")

    # 3. Inserção
    db = SessionLocal()
    try:
        imobiliarias_created = 0
        locais_created = 0
        imoveis_created = 0

        for imovel_data in all_data:
            # Imobiliária
            imobiliaria_nome = (imovel_data.get("imobiliaria") or "UNKNOWN").strip()
            imobiliaria = db.query(DimImobiliaria).filter(
                DimImobiliaria.nome_empresa == imobiliaria_nome
            ).first()
            if not imobiliaria:
                imobiliaria = DimImobiliaria(nome_empresa=imobiliaria_nome)
                db.add(imobiliaria)
                db.flush()
                imobiliarias_created += 1

            # Local — usa bairro diretamente do JSON
            bairro = imovel_data.get("bairro", "Outro")
            cidade = "BRASILIA"
            local = db.query(DimLocal).filter(
                DimLocal.bairro == bairro,
                DimLocal.cidade == cidade
            ).first()
            if not local:
                local = DimLocal(bairro=bairro, cidade=cidade, uf="DF")
                db.add(local)
                db.flush()
                locais_created += 1

            # Fact — id_imovel do JSON mapeado para a coluna id_hex do model
            id_hex = imovel_data.get("id_imovel")
            if id_hex and db.query(FactImovel).filter(FactImovel.id_hex == id_hex).first():
                continue

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
                descricao=(imovel_data.get("descricao") or "")[:2000],
                data_extracao=(
                    datetime.fromisoformat(imovel_data["data_extracao"])
                    if imovel_data.get("data_extracao") else datetime.utcnow()
                ),
            )
            db.add(imovel)
            imoveis_created += 1

        db.commit()

        print("✅ Load Complete!")
        print(f"   📦 Imobiliárias criadas: {imobiliarias_created}")
        print(f"   📍 Locais criados:       {locais_created}")
        print(f"   🏠 Imóveis inseridos:    {imoveis_created}")

        print(f"\n📊 Database Stats:")
        print(f"   Total imóveis:      {db.query(FactImovel).count()}")
        print(f"   Total imobiliárias: {db.query(DimImobiliaria).count()}")
        print(f"   Total locais:       {db.query(DimLocal).count()}")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_json_to_sqlite()

