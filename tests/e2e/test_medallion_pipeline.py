"""
E2E tests para pipeline Medallion Architecture.
Valida fluxo: Scraper → ADLS Bronze → Databricks → PostgreSQL
"""
import pytest
from azure.storage.blob import BlobServiceClient
import psycopg2


@pytest.mark.integration
def test_E2E_scraper_to_postgresql():
    """
    E2E Test: Verifica fluxo completo
    1. Scraper coloca JSON em bronze/raw/
    2. Databricks processa (Bronze → Silver → Gold)
    3. PostgreSQL tem dados carregados
    """
    # Setup
    scraper_output_file = "imoveis_20260415_060240.json"
    
    # Step 1: Verifique arquivo no ADLS
    blob_client = BlobServiceClient.from_connection_string(...)
    container = blob_client.get_container_client("bronze")
    blobs = container.list_blobs(name_starts_with="raw/")
    assert any(scraper_output_file in blob.name for blob in blobs), \
        f"Scraper output {scraper_output_file} não encontrado em bronze/raw/"
    
    # Step 2: Trigger Databricks job
    # (este será um teste manual via Databricks UI por agora)
    
    # Step 3: Verifique dados em PostgreSQL
    conn = psycopg2.connect(
        host="...",
        user="pgadmin",
        password="...",
        database="rentmaster_db"
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM imoveis_gold;")
    count = cursor.fetchone()[0]
    assert count > 0, "Nenhum registro em imoveis_gold após Databricks job"
    
    cursor.execute("SELECT COUNT(*) FROM processing_metadata WHERE status='SUCCESS';")
    success_count = cursor.fetchone()[0]
    assert success_count >= 1, "Nenhum job bem-sucedido registrado"
    
    conn.close()
    print(f"✅ E2E Test Passed: {count} records in PostgreSQL")
