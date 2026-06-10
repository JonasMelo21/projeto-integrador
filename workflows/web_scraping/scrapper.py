"""Scraper de imóveis para aluguel - DFimoveis.com.br

Este módulo extrai dados de imóveis disponíveis para aluguel na página 
DF imoveis.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

# Azure Storage imports (para upload a ADLS Gen2)
try:
	from azure.storage.blob import BlobServiceClient
	from azure.identity import DefaultAzureCredential, ClientSecretCredential
	from azure.core.exceptions import AzureError, ClientAuthenticationError
	from azure.keyvault.secrets import SecretClient
	AZURE_AVAILABLE = True
except ImportError:
	AZURE_AVAILABLE = False
	SecretClient = None


# ============================================================================
# VALIDAÇÃO DE CREDENCIAIS AZURE
# ============================================================================

def validate_tenant_id(tenant_id: str) -> bool:
	"""Valida se o TENANT_ID é um UUID válido.
	
	Args:
		tenant_id: String contendo o tenant ID
	
	Returns:
		True se é um UUID válido, False caso contrário
	"""
	if not tenant_id or not isinstance(tenant_id, str):
		return False
	
	tenant_id = tenant_id.strip()
	try:
		# Tenta converter para UUID
		uuid.UUID(tenant_id)
		return True
	except (ValueError, AttributeError):
		return False


def validate_azure_credentials(tenant_id: str, client_id: str, client_secret: str, 
                               storage_account: str) -> dict:
	"""Valida credenciais do Azure e conectividade com Storage Account.
	
	Args:
		tenant_id: ID do tenant Microsoft Entra
		client_id: ID do Service Principal
		client_secret: Secret do Service Principal
		storage_account: Nome da Storage Account
	
	Returns:
		Dict com status de validação e detalhes
	"""
	result = {
		"valid": False,
		"errors": [],
		"warnings": [],
		"diagnostics": {}
	}
	
	# 1️⃣ Validar TENANT_ID
	if not validate_tenant_id(tenant_id):
		result["errors"].append(
			f"❌ TENANT_ID inválido: '{tenant_id}'\n"
			f"   Use: az account show --query tenantId"
		)
	else:
		result["diagnostics"]["tenant_id"] = "✅ UUID válido"
	
	# 2️⃣ Validar CLIENT_ID
	if not client_id or not isinstance(client_id, str) or not client_id.strip():
		result["errors"].append("❌ AZURE_CLIENT_ID não configurado")
	elif not validate_tenant_id(client_id):  # CLIENT_ID também é UUID
		result["errors"].append(f"❌ AZURE_CLIENT_ID inválido: '{client_id}'")
	else:
		result["diagnostics"]["client_id"] = "✅ UUID válido"
	
	# 3️⃣ Validar CLIENT_SECRET
	if not client_secret or not isinstance(client_secret, str) or not client_secret.strip():
		result["errors"].append("❌ AZURE_CLIENT_SECRET não configurado")
	else:
		result["diagnostics"]["client_secret"] = f"✅ Configurado ({len(client_secret)} chars)"
	
	# 4️⃣ Validar STORAGE_ACCOUNT_NAME
	if not storage_account or not isinstance(storage_account, str):
		result["errors"].append("❌ STORAGE_ACCOUNT_NAME não configurado")
	else:
		# Storage account names devem ser lowercase, 3-24 chars, alphanumeric
		if not (3 <= len(storage_account) <= 24 and storage_account.isalnum() and storage_account.islower()):
			result["warnings"].append(
				f"⚠️  STORAGE_ACCOUNT_NAME pode estar inválido: '{storage_account}'\n"
				f"   Requisitos: 3-24 caracteres, lowercase, somente números e letras"
			)
		else:
			result["diagnostics"]["storage_account"] = f"✅ Nome válido"
	
	# 5️⃣ Se houver erros, retornar aqui
	if result["errors"]:
		return result
	
	# 6️⃣ Tentar autenticar com o Service Principal (se Azure SDK disponível)
	if not AZURE_AVAILABLE:
		result["warnings"].append(
			"⚠️  Azure SDK não disponível, pulando teste de conectividade\n"
			"   Instale: pip install azure-storage-blob azure-identity"
		)
		result["valid"] = True  # Estrutura válida, mas sem SDK
		return result
	
	try:
		# Criar credencial com Service Principal
		credential = ClientSecretCredential(
			tenant_id=tenant_id,
			client_id=client_id,
			client_secret=client_secret
		)
		
		# Tentar obter token para validar credenciais
		token = credential.get_token("https://storage.azure.com/.default")
		result["diagnostics"]["authentication"] = "✅ Autenticação com Service Principal bem-sucedida"
		
		# Tentar conectar ao Blob Storage
		try:
			blob_service_client = BlobServiceClient(
				account_url=f"https://{storage_account}.blob.core.windows.net",
				credential=credential
			)
			# Tentar listar containers (teste básico de conectividade)
			containers = list(blob_service_client.list_containers())
			result["diagnostics"]["storage_connectivity"] = f"✅ Conectado ({len(containers)} containers)"
			result["valid"] = True
		except AzureError as storage_err:
			if "InvalidResourceName" in str(storage_err) or "does not exist" in str(storage_err):
				result["errors"].append(
					f"❌ Storage Account '{storage_account}' não encontrada\n"
					f"   Verifique o nome ou se está na mesma subscription"
				)
			else:
				result["errors"].append(
					f"❌ Erro ao conectar ao Storage Account:\n"
					f"   {str(storage_err)}"
				)
		
	except ClientAuthenticationError as auth_err:
		result["errors"].append(
			f"❌ Falha na autenticação do Service Principal:\n"
			f"   {str(auth_err)}\n"
			f"   Verifique AZURE_CLIENT_ID, AZURE_CLIENT_SECRET e AZURE_TENANT_ID"
		)
	except Exception as e:
		result["errors"].append(
			f"❌ Erro inesperado na validação:\n"
			f"   {str(e)}"
		)
	
	return result


def load_secrets_from_keyvault(vault_url: str) -> dict:
	"""Carrega secrets do Azure Key Vault em vez de variáveis de ambiente.
	
	Args:
		vault_url: URL do Key Vault (ex: https://seu-vault.vault.azure.net/)
	
	Returns:
		Dict com secrets: tenant_id, client_id, client_secret, storage_account
	
	Raises:
		Exception: Se não conseguir acessar o Key Vault ou algum secret não existir
	"""
	if not AZURE_AVAILABLE or SecretClient is None:
		raise RuntimeError(
			"Azure SDK não disponível. Instale: pip install azure-keyvault-secrets azure-identity"
		)
	
	try:
		# Usa Managed Identity (DefaultAzureCredential) para autenticar
		credential = DefaultAzureCredential()
		client = SecretClient(vault_url=vault_url, credential=credential)
		
		print("🔐 Carregando secrets do Key Vault...")
		print(f"   Vault: {vault_url}\n")
		
		# Carrega cada secret
		secrets = {}
		secret_names = ["AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "STORAGE_ACCOUNT_NAME"]
		
		for secret_name in secret_names:
			try:
				secret = client.get_secret(secret_name)
				secrets[secret_name.lower()] = secret.value
				# Log sem expor o valor
				print(f"   ✅ {secret_name} carregado")
			except Exception as e:
				raise RuntimeError(
					f"❌ Secret '{secret_name}' não encontrado no Key Vault:\n"
					f"   {str(e)}\n"
					f"   Certifique-se de que o secret existe no Key Vault"
				)
		
		print()
		
		return {
			"tenant_id": secrets["azure_tenant_id"],
			"client_id": secrets["azure_client_id"],
			"client_secret": secrets["azure_client_secret"],
			"storage_account": secrets["storage_account_name"],
		}
	
	except Exception as e:
		raise RuntimeError(
			f"❌ Erro ao acessar Key Vault:\n"
			f"   {str(e)}\n"
			f"   Verifique: Managed Identity, permissões do Key Vault, URL do vault"
		)


def generate_property_id(url: str) -> str:
	"""Gera ID hexadecimal único a partir da URL do imóvel.
	
	Usa SHA-256 da URL e retorna os primeiros 12 caracteres.
	Garante unicidade e identificação consistente.
	"""
	hash_object = hashlib.sha256(url.encode())
	return hash_object.hexdigest()[:12]


def extract_property_data(article_html: str) -> dict:
	"""Extrai dados de um imóvel a partir do HTML da article."""
	soup = BeautifulSoup(article_html, "html.parser")
	
	try:
		# Nome/Localização
		title_elem = soup.find("h2", class_="ellipse-text body-medium accent-color bold")
		title = title_elem.text.strip() if title_elem else "N/A"
		
		# URL do imóvel
		link_elem = soup.find("a", class_="imovel-card")
		url = link_elem.get("href", "N/A") if link_elem else "N/A"
		
		# Preço
		price_elem = soup.find("p", {"itemprop": "price"})
		price = price_elem.get("content", "N/A") if price_elem else "N/A"
		
		# Descrição
		desc_elem = soup.find("p", {"itemprop": "description"})
		description = desc_elem.text.strip()[:200] if desc_elem else "N/A"
		
		# Características (Quartos, Suítes, Vagas, Área) - Procura por divs que contenham a classe 'border-1'
		# com mais flexibilidade (não exigindo ordem específica)
		quartos = "N/A"
		suites = "N/A"
		vagas = "N/A"
		area_text = "N/A"
		
		# Procura por divs com classe contendo "border-1" (mais robusto)
		feature_divs = soup.find_all("div", class_=lambda x: x and "border-1" in x and "rounded-pill" in x)
		
		for div in feature_divs:
			text = div.text.strip()
			# Extrai área (procura por "m²")
			if "m²" in text and area_text == "N/A":
				area_text = text
			# Se não encontrou área por m², procura outros padrões
			elif quartos == "N/A" and "quarto" in text.lower():
				quartos = text
			elif suites == "N/A" and "suíte" in text.lower():
				suites = text
			elif vagas == "N/A" and ("vaga" in text.lower() or "garagem" in text.lower()):
				vagas = text
		
		# Fallback: se não encontrou por padrão, usa ordem das divs
		if quartos == "N/A" or suites == "N/A" or vagas == "N/A":
			if len(feature_divs) >= 1 and quartos == "N/A":
				quartos = feature_divs[0].text.strip()
			if len(feature_divs) >= 2 and suites == "N/A":
				suites = feature_divs[1].text.strip()
			if len(feature_divs) >= 3 and vagas == "N/A":
				vagas = feature_divs[2].text.strip()
		
		# Imagens - Coleta TODAS as imagens dentro da article (excluindo base64)
		images = []
		img_elems = soup.find_all("img")
		
		for img in img_elems:
			src = img.get("src", "")
			# Filtra apenas URLs reais (não base64 ou GIFs genéricos)
			if src and not src.startswith("data:") and "dfimoveis.com.br" in src:
				images.append(src)
		
		# Se não encontrou imagens reais, tenta qualquer img com loading="lazy"
		if not images:
			img_elem = soup.find("img", loading="lazy")
			if img_elem:
				src = img_elem.get("src", "")
				if src and not src.startswith("data:"):
					images.append(src)
		
		# Imagem principal (para compatibilidade com código anterior)
		image_url = images[0] if images else "N/A"
		images_json = images if images else ["N/A"]
		
		# Imobiliária
		company = "N/A"
		company_elem = soup.find("picture", class_="border-1")
		if company_elem:
			img = company_elem.find("img")
			company = img.get("alt", "N/A") if img else "N/A"
		
		# Gerar ID único
		id_hex = generate_property_id(url)
		
		return {
			"id_hex": id_hex,
			"titulo": title,
			"url": url,
			"preco": price,
			"descricao": description,
			"quartos": quartos,
			"suites": suites,
			"vagas": vagas,
			"area": area_text,
			"imagem": image_url,
			"imagens": images_json,
			"imobiliaria": company,
			"data_extracao": datetime.now().isoformat(),
		}
	except Exception as e:
		print(f"Erro ao extrair dados: {e}")
		return {}


def scrape_properties(url: str, timeout_ms: int = 45_000, num_pages: int = 1) -> list[dict]:
	"""Faz scraping de imóveis da página DFimoveis com suporte a paginação.
	
	Args:
		url: URL base da página (sem parâmetro ?page)
		timeout_ms: Timeout para carregamento em milissegundos
		num_pages: Número de páginas a extrair
	
	Returns:
		Lista de dicts com dados dos imóveis (sem duplicatas)
	"""
	properties = []
	seen_ids = set()  # Rastreiar IDs já processados
	
	for page_num in range(1, num_pages + 1):
		# Construir URL com parâmetro de página
		page_url = f"{url}?page={page_num}" if page_num > 1 else url
		
		print(f"\n📄 Extraindo página {page_num}/{num_pages}: {page_url}")
		
		with sync_playwright() as playwright:
			browser = playwright.chromium.launch(headless=True)
			context = browser.new_context(
				user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
			)
			page = context.new_page()

			try:
				page.goto(page_url, wait_until="domcontentloaded", timeout=timeout_ms)
				print(f"✓ Página carregada com sucesso")
				
				# Aguarda rendering do JS e carregamento de dados
				time.sleep(8)
				
				# Obtém o HTML da página
				page_content = page.content()
				soup = BeautifulSoup(page_content, "html.parser")
				
				# Encontra todos os artigos de imóveis
				articles = soup.find_all("article", {"itemtype": "https://schema.org/RealEstateListing"})
				
				if articles:
					print(f"✓ {len(articles)} imóveis encontrados nesta página")
				else:
					print("⚠ Nenhum imóvel encontrado, verificando structure...")
					# Fallback: procura por qualquer article
					articles = soup.find_all("article")
					print(f"   → Encontrados {len(articles)} articles genéricos")
				
				page_total = 0
				page_duplicates = 0
				
				for article in articles:
					article_html = str(article)
					property_data = extract_property_data(article_html)
					
					if property_data:
						prop_id = property_data["id_hex"]
						
						# Evitar duplicatas
						if prop_id not in seen_ids:
							seen_ids.add(prop_id)
							properties.append(property_data)
							page_total += 1
						else:
							page_duplicates += 1
				
				print(f"  → {page_total} novos, {page_duplicates} duplicados")
				
			except PlaywrightTimeoutError as e:
				print(f"✗ Timeout ao carregar página {page_num}: {e}")
				raise
			except Exception as e:
				print(f"✗ Erro durante scraping da página {page_num}: {e}")
				raise
			finally:
				time.sleep(2)
				context.close()
				browser.close()
	
	return properties


def save_to_csv(properties: list[dict], filename: str = "imoveis.csv") -> None:
	"""Salva dados em arquivo CSV."""
	if not properties:
		print("Nenhum imóvel para salvar")
		return
	
	output_dir = Path("/app/data") if Path("/app/data").exists() else Path("/home/jonasmelo/ProjectsAndStudies/Projeto Integrador III 2.0/data")
	output_dir.mkdir(parents=True, exist_ok=True)
	
	filepath = output_dir / filename
	
	with open(filepath, "w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=properties[0].keys())
		writer.writeheader()
		writer.writerows(properties)
	
	print(f"✓ Dados salvos em: {filepath}")


def save_to_json(properties: list[dict], filename: str = "imoveis.json") -> None:
	"""Salva dados em arquivo JSON."""
	if not properties:
		print("Nenhum imóvel para salvar")
		return
	
	output_dir = Path("/app/data") if Path("/app/data").exists() else Path("/home/jonasmelo/ProjectsAndStudies/Projeto Integrador III 2.0/data")
	output_dir.mkdir(parents=True, exist_ok=True)
	
	filepath = output_dir / filename
	
	with open(filepath, "w", encoding="utf-8") as f:
		json.dump(properties, f, ensure_ascii=False, indent=2)
	
	print(f"✓ Dados salvos em: {filepath}")


def upload_to_adls(properties: list[dict], credentials: dict = None, storage_account: str = "rentmasterstorageaccount", 
                   container: str = "bronze", folder: str = "raw", skip_on_error: bool = True) -> bool:
	"""Faz upload dos dados em JSON para Azure Data Lake Storage Gen2.
	
	Estratégia: Mantém arquivo único 'imoveis_latest.json' sobrescrito a cada run.
	Antes de sobrescrever, faz backup com timestamp para auditoria/recuperação.
	
	Args:
		properties: Lista de imóveis extraídos
		credentials: Dict com tenant_id, client_id, client_secret (se None, carrega de env vars)
		storage_account: Nome da storage account no Azure
		container: Nome do container (bronze por padrão)
		folder: Pasta dentro do container (raw por padrão)
		skip_on_error: Se True, falha silenciosa; Se False, levanta exceção
	
	Returns:
		True se upload bem-sucedido, False caso contrário
	"""
	if not AZURE_AVAILABLE:
		print("✗ Azure SDKs não disponíveis. Instale: pip install azure-storage-blob azure-identity")
		return False
	
	if not properties:
		print("Nenhum imóvel para fazer upload")
		return False
	
	try:
		print("\n☁️ Uploading to Azure Data Lake Storage Gen2...")
		print(f"   Storage: {storage_account}")
		print(f"   Container: {container}")
		print(f"   Folder: {folder}")
		
		# Se credenciais não fornecidas, carregar de env vars (compatibilidade)
		if credentials is None:
			credentials = {
				"tenant_id": os.getenv("AZURE_TENANT_ID", "").strip(),
				"client_id": os.getenv("AZURE_CLIENT_ID", "").strip(),
				"client_secret": os.getenv("AZURE_CLIENT_SECRET", "").strip(),
			}
		
		tenant_id = credentials.get("tenant_id", "").strip()
		client_id = credentials.get("client_id", "").strip()
		client_secret = credentials.get("client_secret", "").strip()
		
		# 1️⃣ Validar credenciais
		print("\n   🔐 Validando credenciais Azure...")
		validation = validate_azure_credentials(tenant_id, client_id, client_secret, storage_account)
		
		# Exibir diagnósticos
		for key, value in validation["diagnostics"].items():
			print(f"      {value}")
		
		# Se houver erros
		if validation["errors"]:
			print(f"\n   ❌ ERROS NA VALIDAÇÃO:")
			for error in validation["errors"]:
				print(f"      {error}")
			
			if not skip_on_error:
				raise RuntimeError("Credenciais inválidas - não é possível fazer upload")
			else:
				print(f"\n   ⚠️  Ignorando upload (skip_on_error=True)")
				return False
		
		# Se houver warnings
		if validation["warnings"]:
			print(f"\n   ⚠️  AVISOS:")
			for warning in validation["warnings"]:
				print(f"      {warning}")
		
		# Se não foi validado, retornar
		if not validation["valid"]:
			print(f"\n   ❌ Credenciais não validadas")
			return False
		
		# 2️⃣ Autenticar e conectar
		print("\n   🔑 Autenticando com Service Principal...")
		credential = ClientSecretCredential(
			tenant_id=tenant_id,
			client_id=client_id,
			client_secret=client_secret
		)
		
		blob_service_client = BlobServiceClient(
			account_url=f"https://{storage_account}.blob.core.windows.net",
			credential=credential
		)
		
		container_client = blob_service_client.get_container_client(container)
		print(f"   ✅ Conectado ao container '{container}'")
		
		# Timestamp para backup
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		
		# 3️⃣ BACKUP: Se imoveis_latest.json existe, fazer cópia com timestamp
		print(f"\n   📦 Gerenciando backups...")
		latest_blob_name = f"{folder}/imoveis_latest.json"
		backup_blob_name = f"{folder}/imoveis_backup_{timestamp}.json"
		
		try:
			latest_blob_client = container_client.get_blob_client(latest_blob_name)
			if latest_blob_client.exists():
				print(f"      Fazendo backup: {latest_blob_name}")
				print(f"      → {backup_blob_name}")
				# Lê conteúdo do arquivo atual
				backup_data = latest_blob_client.download_blob().readall()
				# Cria backup com timestamp
				backup_client = container_client.get_blob_client(backup_blob_name)
				backup_client.upload_blob(backup_data, overwrite=True)
				print(f"      ✓ Backup criado ({len(backup_data)} bytes)")
		except Exception as backup_err:
			print(f"      ⚠️  Aviso ao fazer backup: {backup_err} (continuando...)")
		
		# 4️⃣ UPLOAD: Sobrescreve imoveis_latest.json com novos dados
		print(f"\n   📝 Atualizando dados...")
		print(f"      Blob: {latest_blob_name}")
		json_data = json.dumps(properties, ensure_ascii=False, indent=2).encode("utf-8")
		
		# Upload para latest
		latest_blob_client = container_client.get_blob_client(latest_blob_name)
		latest_blob_client.upload_blob(json_data, overwrite=True)
		blob_properties = latest_blob_client.get_blob_properties()
		
		if blob_properties.size == 0:
			raise RuntimeError(f"Blob '{latest_blob_name}' foi criado, mas está vazio")
		
		print(f"      ✓ Upload bem-sucedido ({blob_properties.size} bytes)")
		print(f"\n   ✅ {len(properties)} imóveis enviados para:")
		print(f"      📁 {storage_account}/{container}/{latest_blob_name}")
		return True
		
	except ClientAuthenticationError as auth_err:
		print(f"\n   ❌ ERRO DE AUTENTICAÇÃO:")
		print(f"      {str(auth_err)}")
		print(f"\n      DIAGNÓSTICO:")
		print(f"      1. Verifique AZURE_TENANT_ID: use 'az account show --query tenantId'")
		print(f"      2. Verifique AZURE_CLIENT_ID e AZURE_CLIENT_SECRET")
		print(f"      3. Verifique se o Service Principal tem acesso ao container")
		return False
	except AzureError as azure_err:
		print(f"\n   ❌ ERRO DO AZURE:")
		print(f"      {str(azure_err)}")
		if "InvalidResourceName" in str(azure_err) or "does not exist" in str(azure_err):
			print(f"\n      DIAGNÓSTICO:")
			print(f"      - Storage Account '{storage_account}' pode não existir")
			print(f"      - Verifique o nome da Storage Account")
			print(f"      - Verifique se está na mesma subscription")
		return False
	except Exception as e:
		print(f"\n   ❌ ERRO INESPERADO:")
		print(f"      {type(e).__name__}: {str(e)}")
		return False


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Scraper de imóveis para aluguel - DFimoveis.com.br"
	)
	parser.add_argument(
		"url",
		default="https://www.dfimoveis.com.br/aluguel/df/todos/imoveis",
		nargs="?",
		help="URL da página (padrão: dfimoveis aluguel DF)",
	)
	parser.add_argument(
		"--timeout-ms",
		type=int,
		default=45_000,
		help="Timeout em milissegundos (padrão: 45000)",
	)
	parser.add_argument(
		"--format",
		choices=["csv", "json", "both"],
		default="both",
		help="Formato de saída (padrão: both)",
	)
	parser.add_argument(
		"--num-pages",
		type=int,
		default=1,
		help="Número de páginas a extrair (padrão: 1)",
	)
	parser.add_argument(
		"--upload-to-adls",
		action="store_true",
		help="Faz upload dos dados para Azure Data Lake Storage Gen2 (bronze/raw/)",
	)
	parser.add_argument(
		"--storage-account",
		default="rentmasterstorageaccount",
		help="Nome da storage account Azure (padrão: rentmasterstorageaccount)",
	)
	parser.add_argument(
		"--skip-on-error",
		action="store_true",
		default=True,
		help="Continuar mesmo se falhar o upload (padrão: True)",
	)
	parser.add_argument(
		"--strict",
		action="store_true",
		help="Modo strict: falhar se não conseguir fazer upload",
	)
	parser.add_argument(
		"--validate-credentials",
		action="store_true",
		help="Validar credenciais Azure sem fazer scraping",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	
	# Carregar credenciais: Key Vault (produção) ou env vars (desenvolvimento)
	credentials = {}
	key_vault_url = os.getenv("KEY_VAULT_URL", "").strip()
	
	if key_vault_url:
		# Produção: carregar do Key Vault usando Managed Identity
		try:
			credentials = load_secrets_from_keyvault(key_vault_url)
		except Exception as e:
			print(f"{str(e)}\n")
			sys.exit(1)
	else:
		# Desenvolvimento: carregar de env vars
		credentials = {
			"tenant_id": os.getenv("AZURE_TENANT_ID", "").strip(),
			"client_id": os.getenv("AZURE_CLIENT_ID", "").strip(),
			"client_secret": os.getenv("AZURE_CLIENT_SECRET", "").strip(),
			"storage_account": args.storage_account,
		}
	
	# Modo de validação de credenciais (se solicitado)
	if args.validate_credentials:
		print("\n🔐 MODO: Validação de Credenciais Azure")
		print(f"{'='*70}\n")
		
		validation = validate_azure_credentials(
			credentials["tenant_id"],
			credentials["client_id"],
			credentials["client_secret"],
			credentials["storage_account"]
		)
		
		print("\n📋 RESULTADO DA VALIDAÇÃO:")
		print(f"{'='*70}\n")
		
		print("✅ DIAGNÓSTICOS:")
		for key, value in validation["diagnostics"].items():
			print(f"   {value}")
		
		if validation["warnings"]:
			print("\n⚠️  AVISOS:")
			for warning in validation["warnings"]:
				for line in warning.split("\n"):
					print(f"   {line}")
		
		if validation["errors"]:
			print("\n❌ ERROS:")
			for error in validation["errors"]:
				for line in error.split("\n"):
					print(f"   {line}")
			sys.exit(1)
		
		print(f"\n{'='*70}")
		if validation["valid"]:
			print("✅ Credenciais válidas e testadas com sucesso!")
		else:
			print("⚠️  Credenciais podem ter problemas. Verifique os erros acima.")
		print(f"{'='*70}\n")
		return
	
	# Modo normal: scraping
	print(f"\n🔍 Iniciando scraping")
	print(f"   URL: {args.url}")
	print(f"   Páginas: {args.num_pages}")
	print(f"   Formato: {args.format}")
	if args.upload_to_adls:
		print(f"   Upload: ADLS Gen2 ({args.storage_account})")
		skip_on_error = not args.strict
		print(f"   Modo: {'Permissivo (continua se falhar)' if skip_on_error else 'Strict (falha se erro)'}")
	print()
	
	try:
		properties = scrape_properties(
			url=args.url,
			timeout_ms=args.timeout_ms,
			num_pages=args.num_pages
		)
		
		if properties:
			print(f"\n{'='*70}")
			print(f"✓ {len(properties)} imóveis ÚNICOS extraídos com sucesso!")
			print(f"{'='*70}\n")
			
			if args.format in ["csv", "both"]:
				save_to_csv(properties)
			
			if args.format in ["json", "both"]:
				save_to_json(properties)
			
			# Upload para ADLS Gen2 (se solicitado)
			if args.upload_to_adls:
				skip_on_error = not args.strict
				upload_ok = upload_to_adls(
					properties,
					credentials=credentials,
					storage_account=args.storage_account,
					skip_on_error=skip_on_error
				)
				if not upload_ok and not skip_on_error:
					raise RuntimeError("Falha no upload para o ADLS Gen2 (modo strict)")
			
			# Exibe resumo
			print("\n📊 Resumo dos primeiros imóveis:")
			for i, prop in enumerate(properties[:3], 1):
				print(f"\n{i}. {prop['titulo']} (ID: {prop['id_hex']})")
				print(f"   Preço: R$ {prop['preco']}")
				print(f"   {prop['quartos']} | {prop['suites']} | {prop['vagas']} | {prop['area']}")
				if prop.get('imagens') and prop['imagens'][0] != "N/A":
					print(f"   Imagens: {len(prop['imagens'])} arquivo(s)")
			
			print(f"\n✅ Execução finalizada com sucesso!")
		else:
			print("✗ Nenhum imóvel encontrado")
			sys.exit(1)
	
	except Exception as e:
		print(f"\n✗ Erro: {e}")
		import traceback
		traceback.print_exc()
		sys.exit(1)


if __name__ == "__main__":
	main()
