#!/usr/bin/env python3
"""
RentMaster Medallion Architecture - E2E Pipeline Setup
Configura Databricks + PostgreSQL + executa notebooks
"""

import subprocess
import json
import sys
import time
import os

# Configuration
RESOURCE_GROUP = "rg_rent_master_dev"
SUBSCRIPTION = "c8bb64c0-25e3-4b8e-a99e-262dcdeb7c0b"
POSTGRES_PASSWORD = "Rentmaster@2026!"

def run_command(cmd, description=""):
    """Execute Azure CLI command"""
    print(f"\n{'='*60}")
    if description:
        print(f"▶ {description}")
    print(f"   Command: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"❌ ERROR:\n{result.stderr}")
            return None
        print(f"✓ Success")
        return result.stdout
    except subprocess.TimeoutExpired:
        print("❌ Command timeout")
        return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  🚀 RentMaster Medallion E2E Setup - PRAGMATIC MODE 🔥       ║
    ║     Databricks + PostgreSQL + Execution                       ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Verificar Azure CLI
    print("\n[STEP 1] Validating Azure CLI...")
    result = run_command(
        'az account show --query "name" -o tsv',
        "Check Azure subscription"
    )
    if not result:
        print("❌ Not authenticated. Run: az login")
        sys.exit(1)
    print(f"✓ Logged in: {result.strip()}")
    
    # Step 2: Verificar PostgreSQL
    print("\n[STEP 2] Checking PostgreSQL...")
    result = run_command(
        f'az postgres flexible-server list -g {RESOURCE_GROUP} --query "[0].name" -o tsv',
        "List PostgreSQL servers"
    )
    
    if not result or not result.strip():
        print("⚠ PostgreSQL não encontrado. Criando...")
        postgres_name = f"rentmaster-postgres-{int(time.time())}"
        
        run_command(
            f'az postgres flexible-server create '
            f'--name {postgres_name} '
            f'--resource-group {RESOURCE_GROUP} '
            f'--admin-user pgadmin '
            f'--admin-password "{POSTGRES_PASSWORD}" '
            f'--sku-name Standard_B2s '
            f'--tier Burstable '
            f'--storage-size 32 '
            f'--version 15 '
            f'--yes',
            f"Create PostgreSQL Flexible Server: {postgres_name}"
        )
        
        postgres_host = run_command(
            f'az postgres flexible-server show '
            f'--name {postgres_name} '
            f'--resource-group {RESOURCE_GROUP} '
            f'--query "fullyQualifiedDomainName" -o tsv',
            "Get PostgreSQL hostname"
        ).strip()
    else:
        postgres_name = result.strip()
        postgres_host = run_command(
            f'az postgres flexible-server show '
            f'--name {postgres_name} '
            f'--resource-group {RESOURCE_GROUP} '
            f'--query "fullyQualifiedDomainName" -o tsv',
            "Get PostgreSQL hostname"
        ).strip()
    
    print(f"✓ PostgreSQL: {postgres_host}")
    
    # Step 3: Create firewall rule
    print("\n[STEP 3] Configuring PostgreSQL firewall...")
    run_command(
        f'az postgres flexible-server firewall-rule create '
        f'--name AllowAll '
        f'--server-name {postgres_name} '
        f'--resource-group {RESOURCE_GROUP} '
        f'--start-ip-address 0.0.0.0 '
        f'--end-ip-address 255.255.255.255',
        "Allow all IPs (for testing)"
    )
    
    # Step 4: Create database
    print("\n[STEP 4] Creating rentmaster_db database...")
    run_command(
        f'PGPASSWORD="{POSTGRES_PASSWORD}" psql '
        f'-h {postgres_host} -U pgadmin -c "CREATE DATABASE rentmaster_db;"',
        "Create database"
    )
    
    # Step 5: Load schema
    print("\n[STEP 5] Loading PostgreSQL schema...")
    schema_path = '/home/jonasmelo/projectsandstudies/Projeto Integrador III 2.0/infrastructure/sql/schema.sql'
    if os.path.exists(schema_path):
        run_command(
            f'PGPASSWORD="{POSTGRES_PASSWORD}" psql '
            f'-h {postgres_host} '
            f'-U pgadmin '
            f'-d rentmaster_db '
            f'< "{schema_path}"',
            "Load PostgreSQL schema (tables, indexes, views)"
        )
        print("✓ Schema loaded")
    else:
        print(f"⚠ Schema file not found: {schema_path}")
    
    # Step 6: Check ADLS data
    print("\n[STEP 6] Checking ADLS bronze/raw/ data...")
    result = run_command(
        'az storage blob list '
        '--container-name bronze '
        '--account-name rentmasterstorageaccount '
        '--prefix raw/ '
        '--auth-mode login '
        '--query "[].name" -o tsv',
        "List JSON files in bronze/raw"
    )
    
    if result:
        files = result.strip().split('\n')
        print(f"✓ Found {len(files)} JSON files:")
        for f in files[:3]:
            print(f"   - {f}")
        if len(files) > 3:
            print(f"   ... and {len(files)-3} more")
    else:
        print("⚠ No files found in bronze/raw/")
    
    # Step 7: Instructions for Databricks
    print(f"""
    {'='*60}
    ✅ PostgreSQL Infrastructure Ready!
    {'='*60}
    
    📍 PostgreSQL Details:
       Host: {postgres_host}
       User: pgadmin
       Password: {POSTGRES_PASSWORD}
       Database: rentmaster_db
    
    📋 Next Steps (via Databricks UI):
    
       1. Create Databricks Cluster:
          - Name: medallion-cluster
          - Runtime: 13.3 LTS (Scala 2.12, Spark 3.4.1)
          - Node Type: Standard_D4s_v5
          - Min Workers: 1, Max Workers: 4
    
       2. Upload Notebooks:
          - /medallion/01_bronze_layer.py
          - /medallion/02_silver_layer.py
          - /medallion/03_gold_layer.py
    
       3. In 03_gold_layer, set PostgreSQL credentials:
          postgres_host = "{postgres_host}"
          postgres_user = "pgadmin"
          postgres_password = "{POSTGRES_PASSWORD}"
          postgres_db = "rentmaster_db"
    
       4. Run notebooks in sequence:
          Notebook 1 → Notebook 2 → Notebook 3
    
       5. Verify data in PostgreSQL:
          psql -h {postgres_host} -U pgadmin -d rentmaster_db
          SELECT COUNT(*) FROM imoveis_gold;
    
    {'='*60}
    """)

if __name__ == "__main__":
    main()
