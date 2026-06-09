import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


# Configuration
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "rentmasterstorageaccount")
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "bronze")
BLOB_PREFIX = os.getenv("BLOB_PREFIX", "raw/")
LOCAL_JSON_DIR = os.getenv("LOCAL_JSON_DIR", "")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "./silver/cleaned")
REJECTED_PATH = os.getenv("REJECTED_PATH", "./silver/rejected")
PIPELINE_VERSION = os.getenv("PIPELINE_VERSION", "1.0")
USE_AZURE = os.getenv("USE_AZURE", "false").lower() in ("1", "true", "yes")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
INPUT_FILE = os.getenv("INPUT_FILE", "")  # Se fornecido, processa APENAS esse arquivo (para integração com Data Factory)


# Logging
logger = logging.getLogger("bronze_to_silver")
logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
logger.addHandler(handler)


def parse_preco(preco_str: Optional[str]) -> Optional[float]:
    if preco_str is None:
        return None
    cleaned = str(preco_str).strip().replace("R$", "").replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    match = re.search(r"\d+", str(value))
    return int(match.group()) if match else None


def parse_area(area_str: Optional[str]) -> Optional[float]:
    if area_str is None:
        return None
    match = re.search(r"[\d.,]+", str(area_str))
    if not match:
        return None
    value = match.group().replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None


def parse_datetime(value: Optional[str]) -> datetime:
    if not value:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.utcnow()


def get_blob_client() -> BlobServiceClient:
    credential = DefaultAzureCredential()
    account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
    client = BlobServiceClient(account_url=account_url, credential=credential)
    logger.info(f"✅ Connected to Storage Account: {STORAGE_ACCOUNT_NAME}")
    return client


def list_azure_blobs() -> List[str]:
    client = get_blob_client()
    container_client = client.get_container_client(CONTAINER_NAME)
    return [blob.name for blob in container_client.list_blobs(name_starts_with=BLOB_PREFIX) if blob.name.endswith(".json")]


def download_blob(blob_name: str) -> Optional[str]:
    client = get_blob_client()
    blob_client = client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
    return blob_client.download_blob().readall().decode("utf-8")


def load_json_file(path: Path) -> Optional[List[Dict]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, list) else [payload]
    except Exception as exc:
        logger.error(f"❌ Failed to read {path}: {exc}")
        return None


def transform_record(raw: Dict, source_file: str) -> Optional[Dict]:
    id_hex = raw.get("id_hex")
    titulo = raw.get("titulo")
    if not id_hex or not titulo:
        return None

    preco = parse_preco(raw.get("preco"))
    area_m2 = parse_area(raw.get("area"))
    quartos = parse_int(raw.get("quartos"))
    suites = parse_int(raw.get("suites"))
    vagas = parse_int(raw.get("vagas"))
    banheiros = parse_int(raw.get("banheiros"))
    data_extracao = parse_datetime(raw.get("data_extracao"))

    if preco is None or area_m2 is None or preco <= 0 or area_m2 <= 0:
        return None

    preco_por_m2 = round(preco / area_m2, 2) if area_m2 else None
    descricao = raw.get("descricao", "")
    imobiliaria = raw.get("imobiliaria")

    return {
        "id_hex": id_hex,
        "titulo": titulo.strip(),
        "descricao": descricao,
        "imobiliaria": imobiliaria,
        "preco": preco,
        "area_m2": area_m2,
        "preco_por_m2": preco_por_m2,
        "quartos": quartos,
        "suites": suites,
        "vagas": vagas,
        "banheiros": banheiros,
        "descricao_len": len(descricao) if descricao else 0,
        "titulo_len": len(titulo),
        "data_extracao": data_extracao,
        "process_date": data_extracao.date().isoformat(),
        "source_file": source_file,
        "ingestion_datetime": datetime.utcnow(),
        "pipeline_version": PIPELINE_VERSION,
    }


def write_parquet(df: pd.DataFrame, output_path: Path) -> None:
    output_path.mkdir(parents=True, exist_ok=True)
    df.to_parquet(str(output_path / "data.parquet"), index=False, partition_cols=["process_date"], engine="pyarrow")
    logger.info(f"✅ Written Parquet to {output_path}")


def write_rejected(rejected: List[Dict], rejected_path: Path) -> None:
    rejected_path.mkdir(parents=True, exist_ok=True)
    if not rejected:
        return
    rejected_file = rejected_path / f"rejected_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with rejected_file.open("w", encoding="utf-8") as f:
        json.dump(rejected, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"✅ Written rejected records to {rejected_file}")


def main() -> None:
    output_path = Path(OUTPUT_PATH)
    rejected_path = Path(REJECTED_PATH)
    all_records: List[Dict] = []
    rejected_records: List[Dict] = []
    seen_ids = set()

    # Mode 1: Processa APENAS um arquivo específico (ideal para Data Factory pipeline)
    if INPUT_FILE:
        logger.info(f"🎯 INPUT_FILE mode: Processing only '{INPUT_FILE}'")
        
        if LOCAL_JSON_DIR:
            file_path = Path(LOCAL_JSON_DIR) / INPUT_FILE
            if not file_path.exists():
                logger.error(f"❌ File not found: {file_path}")
                return
            payload = load_json_file(file_path)
            if payload is None:
                rejected_records.append({"source_file": INPUT_FILE, "error": "read_failed"})
            else:
                for record in payload:
                    transformed = transform_record(record, INPUT_FILE)
                    if transformed is None:
                        rejected_records.append({"source_file": INPUT_FILE, "record": record})
                        continue
                    all_records.append(transformed)
                    
        elif USE_AZURE:
            blob_name = f"{BLOB_PREFIX}{INPUT_FILE}" if not INPUT_FILE.startswith(BLOB_PREFIX) else INPUT_FILE
            logger.info(f"📥 Downloading blob from Azure: {blob_name}")
            content = download_blob(blob_name)
            if content is None:
                rejected_records.append({"source_file": blob_name, "error": "download_failed"})
            else:
                try:
                    payload = json.loads(content)
                    records = payload if isinstance(payload, list) else [payload]
                    for record in records:
                        transformed = transform_record(record, blob_name)
                        if transformed is None:
                            rejected_records.append({"source_file": blob_name, "record": record})
                            continue
                        all_records.append(transformed)
                except json.JSONDecodeError:
                    rejected_records.append({"source_file": blob_name, "error": "invalid_json"})
    
    # Mode 2: Processa TODOS os arquivos (comportamento legado/default)
    elif LOCAL_JSON_DIR:
        logger.info(f"📁 Legacy mode: Processing ALL JSON files in {LOCAL_JSON_DIR}")
        source_dir = Path(LOCAL_JSON_DIR)
        json_files = sorted(source_dir.glob("*.json"))
        for path in json_files:
            payload = load_json_file(path)
            if payload is None:
                rejected_records.append({"source_file": str(path), "error": "read_failed"})
                continue
            for record in payload:
                transformed = transform_record(record, str(path.name))
                if transformed is None:
                    rejected_records.append({"source_file": str(path.name), "record": record})
                    continue
                if transformed["id_hex"] in seen_ids:
                    continue
                seen_ids.add(transformed["id_hex"])
                all_records.append(transformed)
                
    elif USE_AZURE:
        logger.info(f"📋 Legacy mode: Processing ALL JSON blobs in {CONTAINER_NAME}/{BLOB_PREFIX}")
        blob_names = list_azure_blobs()
        logger.info(f"📋 Found {len(blob_names)} JSON blobs")
        for blob_name in blob_names:
            content = download_blob(blob_name)
            if content is None:
                rejected_records.append({"source_file": blob_name, "error": "download_failed"})
                continue
            try:
                payload = json.loads(content)
            except json.JSONDecodeError:
                rejected_records.append({"source_file": blob_name, "error": "invalid_json"})
                continue
            records = payload if isinstance(payload, list) else [payload]
            for record in records:
                transformed = transform_record(record, blob_name)
                if transformed is None:
                    rejected_records.append({"source_file": blob_name, "record": record})
                    continue
                if transformed["id_hex"] in seen_ids:
                    continue
                seen_ids.add(transformed["id_hex"])
                all_records.append(transformed)
    else:
        logger.error("⚠️  No input specified. Either set INPUT_FILE, LOCAL_JSON_DIR, or enable USE_AZURE.")
        return

    if all_records:
        df = pd.DataFrame(all_records)
        write_parquet(df, output_path)
    else:
        logger.warning("⚠️  No valid records to write.")

    write_rejected(rejected_records, rejected_path)

    logger.info(f"✅ Processed {len(all_records)} records, rejected {len(rejected_records)} records.")


if __name__ == "__main__":
    main()
