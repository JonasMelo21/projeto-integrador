"""Scraper de imóveis para aluguel - DFimoveis.com.br

Este módulo extrai dados de imóveis disponíveis para aluguel na página 
DF imoveis.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

# Azure Storage imports (para upload a ADLS Gen2)
try:
	from azure.storage.blob import BlobServiceClient
	from azure.identity import DefaultAzureCredential
	AZURE_AVAILABLE = True
except ImportError:
	AZURE_AVAILABLE = False


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


def upload_to_adls(properties: list[dict], storage_account: str = "rentmasterstorageaccount", 
                   container: str = "bronze", folder: str = "raw") -> bool:
	"""Faz upload dos dados em JSON para Azure Data Lake Storage Gen2.
	
	Args:
		properties: Lista de imóveis extraídos
		storage_account: Nome da storage account no Azure
		container: Nome do container (bronze por padrão)
		folder: Pasta dentro do container (raw por padrão)
	
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
		
		# Credenciais (usa DefaultAzureCredential: az login, env vars, ou managed identity)
		credential = DefaultAzureCredential()
		
		# Cliente do Blob Storage
		blob_service_client = BlobServiceClient(
			account_url=f"https://{storage_account}.blob.core.windows.net",
			credential=credential
		)
		
		# Cliente do container
		container_client = blob_service_client.get_container_client(container)
		
		# Nome do arquivo com timestamp
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		blob_name = f"{folder}/imoveis_{timestamp}.json"
		
		# Prepara dados JSON
		json_data = json.dumps(properties, ensure_ascii=False, indent=2).encode("utf-8")
		
		# Upload
		blob_client = container_client.get_blob_client(blob_name)
		blob_client.upload_blob(json_data, overwrite=True)
		
		print(f"   ✓ {len(properties)} imóveis enviados para:")
		print(f"   📁 {storage_account}/{container}/{blob_name}")
		return True
		
	except Exception as e:
		print(f"   ✗ Erro ao fazer upload: {e}")
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
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	
	print(f"\n🔍 Iniciando scraping")
	print(f"   URL: {args.url}")
	print(f"   Páginas: {args.num_pages}")
	print(f"   Formato: {args.format}")
	if args.upload_to_adls:
		print(f"   Upload: ADLS Gen2 ({args.storage_account})")
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
				upload_to_adls(properties, storage_account=args.storage_account)
			
			# Exibe resumo
			print("\n📊 Resumo dos primeiros imóveis:")
			for i, prop in enumerate(properties[:3], 1):
				print(f"\n{i}. {prop['titulo']} (ID: {prop['id_hex']})")
				print(f"   Preço: R$ {prop['preco']}")
				print(f"   {prop['quartos']} | {prop['suites']} | {prop['vagas']} | {prop['area']}")
				if prop.get('imagens') and prop['imagens'][0] != "N/A":
					print(f"   Imagens: {len(prop['imagens'])} arquivo(s)")
		else:
			print("✗ Nenhum imóvel encontrado")
	
	except Exception as e:
		print(f"\n✗ Erro: {e}")
		raise


if __name__ == "__main__":
	main()
