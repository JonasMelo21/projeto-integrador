"""Script para testar acesso ao Azure Data Lake Storage Gen2 (ADLS Gen2)."""

from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import sys


def test_adls_connection():
    """Testa conexão com ADLS Gen2."""
    
    storage_account = "rentmasterstorageaccount"
    container_name = "bronze"
    
    print(f"\n{'='*60}")
    print(f"🔗 Testando conexão com ADLS Gen2")
    print(f"{'='*60}")
    
    try:
        # Tenta usar credentials (az login ativo)
        print("\n1️⃣ Obtendo credenciais...")
        credential = DefaultAzureCredential()
        print("   ✅ Kredenciais obtidas (az login)")
        
    except Exception as e:
        print(f"   ❌ Erro ao obter credenciais: {e}")
        sys.exit(1)
    
    try:
        # Conecta ao Storage Account
        print("\n2️⃣ Conectando ao Storage Account...")
        client = BlobServiceClient(
            account_url=f"https://{storage_account}.blob.core.windows.net",
            credential=credential
        )
        print(f"   ✅ Conectado ao '{storage_account}'")
        
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        sys.exit(1)
    
    try:
        # Testa acesso ao container
        print(f"\n3️⃣ Acessando container '{container_name}'...")
        container_client = client.get_container_client(container_name)
        props = container_client.get_container_properties()
        print(f"   ✅ Container accessible: {props.name}")
        
    except Exception as e:
        print(f"   ❌ Erro ao acessar container: {e}")
        sys.exit(1)
    
    try:
        # Lista blobs no container (até 5)
        print(f"\n4️⃣ Listando arquivos em '{container_name}/'...")
        blobs = container_client.list_blobs()
        blob_list = list(blobs)[:5]
        
        if blob_list:
            print(f"   ✅ Encontrados {len(blob_list)} blobs:")
            for blob in blob_list:
                print(f"      - {blob.name}")
        else:
            print(f"   ℹ️  Container vazio (ok pra primeira vez)")
        
    except Exception as e:
        print(f"   ❌ Erro ao listar blobs: {e}")
        sys.exit(1)
    
    try:
        # Testa upload de teste
        print(f"\n5️⃣ Testando upload de arquivo ('raw/test.txt')...")
        blob_client = container_client.get_blob_client("raw/test.txt")
        blob_client.upload_blob(b"test", overwrite=True)
        print(f"   ✅ Upload bem-sucedido!")
        
        # Limpa arquivo de teste
        blob_client.delete_blob()
        print(f"   ✅ Limpeza concluída")
        
    except Exception as e:
        print(f"   ❌ Erro no teste de upload: {e}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"✅ TUDO OK! Você pode usar ADLS Gen2.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    test_adls_connection()
