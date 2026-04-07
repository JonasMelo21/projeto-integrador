"""Exemplo de integração do scraper como módulo Python."""

from scrapper.scrapper import scrape_properties, save_to_csv, save_to_json


def example_1_basic_scraping():
	"""Exemplo 1: Web scraping básico com URL padrão."""
	print("\n" + "="*60)
	print("EXEMPLO 1: Web Scraping Básico")
	print("="*60)
	
	properties = scrape_properties(
		url="https://www.dfimoveis.com.br/aluguel/df/todos/imoveis"
	)
	
	print(f"\n✓ Total de imóveis extraídos: {len(properties)}")
	
	if properties:
		first_property = properties[0]
		print(f"\nPrimeiro imóvel:")
		print(f"  Título: {first_property['titulo']}")
		print(f"  Preço: R$ {first_property['preco']}")
		print(f"  Características: {first_property['quartos']}, {first_property['suites']}, {first_property['vagas']}")
		print(f"  Imobiliária: {first_property['imobiliaria']}")


def example_2_filtering_by_price():
	"""Exemplo 2: Filtragem de imóveis por faixa de preço."""
	print("\n" + "="*60)
	print("EXEMPLO 2: Filtragem por Preço")
	print("="*60)
	
	properties = scrape_properties(
		url="https://www.dfimoveis.com.br/aluguel/df/todos/imoveis"
	)
	
	# Filtrar por faixa de preço
	price_min, price_max = 10_000, 50_000
	
	filtered = [
		prop for prop in properties
		if price_min <= float(prop['preco'].replace(' ', '').replace(',', '.')) <= price_max
	]
	
	print(f"\nImóveis entre R$ {price_min:,} e R$ {price_max:,}")
	print(f"Total encontrado: {len(filtered)}")
	
	for prop in filtered[:3]:
		print(f"\n  • {prop['titulo']}")
		print(f"    Preço: R$ {prop['preco']}")
		print(f"    {prop['quartos']} - {prop['suites']}")


def example_3_export_formats():
	"""Exemplo 3: Exportação em múltiplos formatos."""
	print("\n" + "="*60)
	print("EXEMPLO 3: Exportação em CSV e JSON")
	print("="*60)
	
	properties = scrape_properties(
		url="https://www.dfimoveis.com.br/aluguel/df/todos/imoveis"
	)
	
	save_to_csv(properties, filename="imoveis_export.csv")
	save_to_json(properties, filename="imoveis_export.json")
	
	print(f"\n✓ Dados exportados com sucesso!")
	print(f"  - CSV: data/imoveis_export.csv")
	print(f"  - JSON: data/imoveis_export.json")


def example_4_statistics():
	"""Exemplo 4: Análise e estatísticas dos imóveis."""
	print("\n" + "="*60)
	print("EXEMPLO 4: Estatísticas")
	print("="*60)
	
	properties = scrape_properties(
		url="https://www.dfimoveis.com.br/aluguel/df/todos/imoveis"
	)
	
	if not properties:
		print("Nenhum imóvel encontrado")
		return
	
	# Extrair preços
	prices = []
	for prop in properties:
		try:
			price = float(prop['preco'].replace(' ', '').replace(',', '.'))
			prices.append(price)
		except:
			pass
	
	if prices:
		print(f"\n📊 Análise de Preços:")
		print(f"  Total de imóveis: {len(prices)}")
		print(f"  Preço médio: R$ {sum(prices)/len(prices):,.2f}")
		print(f"  Preço mínimo: R$ {min(prices):,.2f}")
		print(f"  Preço máximo: R$ {max(prices):,.2f}")
	
	# Imobiliárias mais mencionadas
	from collections import Counter
	companies = Counter(prop['imobiliaria'] for prop in properties)
	
	print(f"\n🏢 Top 5 Imobiliárias:")
	for company, count in companies.most_common(5):
		print(f"  • {company}: {count} imóvel(is)")


if __name__ == "__main__":
	# Para executar os exemplos:
	# python examples.py
	
	print("\n" + "="*60)
	print("EXEMPLOS DE USO DO SCRAPER DE IMÓVEIS")
	print("="*60)
	
	try:
		example_1_basic_scraping()
		example_2_filtering_by_price()
		example_3_export_formats()
		example_4_statistics()
		
		print("\n" + "="*60)
		print("✓ Todos os exemplos executados com sucesso!")
		print("="*60 + "\n")
		
	except Exception as e:
		print(f"\n✗ Erro ao executar exemplos: {e}")
