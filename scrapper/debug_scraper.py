"""Script para debugar estrutura HTML e encontrar seletores CSS corretos."""

import time
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def debug_property_html(url: str = "https://www.dfimoveis.com.br/aluguel/df/todos/imoveis"):
    """Faz screenshot, salva HTML bruto e analisa estrutura para debugar seletores."""
    
    print(f"\n{'='*70}")
    print(f"🔍 DEBUG SCRAPER - Analisando Estrutura HTML")
    print(f"{'='*70}")
    print(f"URL: {url}\n")
    
    output_dir = Path("scrapper/debug_output")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        try:
            print("1️⃣ Carregando página...")
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            time.sleep(8)
            print("   ✅ Página carregada\n")
            
            # Screenshot
            print("2️⃣ Salvando screenshot...")
            screenshot_path = output_dir / f"screenshot_{timestamp}.png"
            page.screenshot(path=str(screenshot_path))
            print(f"   ✅ {screenshot_path}\n")
            
            # HTML completo
            print("3️⃣ Salvando HTML bruto...")
            html_content = page.content()
            html_path = output_dir / f"full_page_{timestamp}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"   ✅ {html_path}\n")
            
            # Parse e análise
            print("4️⃣ Analisando primeira propriedade...\n")
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Procura artigos
            articles = soup.find_all("article", limit=1)
            if articles:
                article = articles[0]
                article_str = str(article)
                
                # Salva HTML da primeira article isolada
                article_path = output_dir / f"first_article_{timestamp}.html"
                with open(article_path, "w", encoding="utf-8") as f:
                    f.write(article_str)
                print(f"   ✅ Primeira <article> salva: {article_path}\n")
                
                # Análise de seletores
                print("   📍 Seletores encontrados nesta propriedade:\n")
                
                # Procura por "area" em texto
                area_patterns = []
                for elem in article.find_all():
                    if elem.string and "m²" in str(elem.string):
                        area_patterns.append({
                            "tag": elem.name,
                            "class": elem.get("class"),
                            "text": str(elem.string)[:50]
                        })
                
                if area_patterns:
                    print("   🏠 Elementos com 'm²' (área):")
                    for p in area_patterns:
                        print(f"      <{p['tag']} class='{p['class']}'> {p['text']}")
                else:
                    print("   ⚠️  Nenhum elemento com 'm²' encontrado")
                
                # Procura por imagens
                images = article.find_all("img")
                print(f"\n   📸 Imagens encontradas: {len(images)}")
                for i, img in enumerate(images[:6]):
                    src = img.get("src", "N/A")
                    alt = img.get("alt", "N/A")
                    print(f"      {i+1}. src={src[:60]}... | alt={alt}")
                
                # Procura por divs de características
                feature_divs = article.find_all("div", class_="border-1 py-0 px-2 bg-white body-small rounded-pill")
                print(f"\n   📦 Divs com características encontrados: {len(feature_divs)}")
                for i, div in enumerate(feature_divs):
                    print(f"      {i+1}. {div.text.strip()}")
                
                # Salva análise em arquivo de texto
                analysis_path = output_dir / f"analysis_{timestamp}.txt"
                with open(analysis_path, "w", encoding="utf-8") as f:
                    f.write(f"ANÁLISE DE PRIMEIRA PROPRIEDADE\n")
                    f.write(f"Timestamp: {timestamp}\n")
                    f.write(f"URL: {url}\n\n")
                    f.write(f"IMAGENS ENCONTRADAS: {len(images)}\n")
                    for i, img in enumerate(images):
                        f.write(f"  {i+1}. {img.get('src', 'N/A')}\n")
                    f.write(f"\nCARACTERÍSTICAS (divs com 'border-1...'): {len(feature_divs)}\n")
                    for i, div in enumerate(feature_divs):
                        f.write(f"  {i+1}. {div.text.strip()}\n")
                    f.write(f"\nELEMENTOS COM 'm²': {len(area_patterns)}\n")
                    for p in area_patterns:
                        f.write(f"  <{p['tag']} class='{p['class']}'> {p['text']}\n")
                
                print(f"\n   📄 Análise salva: {analysis_path}")
                
            else:
                print("   ❌ Nenhuma <article> encontrada!")
            
            print(f"\n{'='*70}")
            print(f"📁 Todos os arquivos de debug salvos em: {output_dir}")
            print(f"   - screenshot_{timestamp}.png")
            print(f"   - full_page_{timestamp}.html")
            print(f"   - first_article_{timestamp}.html")
            print(f"   - analysis_{timestamp}.txt")
            print(f"{'='*70}\n")
            
        except Exception as e:
            print(f"❌ Erro durante debug: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    debug_property_html()
