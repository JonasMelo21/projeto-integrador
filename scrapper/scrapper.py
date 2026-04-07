"""Scraper mínimo para validar navegação com Playwright.

Este módulo abre uma página no Chromium e fecha em seguida.
Use este arquivo como ponto de partida para o scraper de imóveis.
"""

from __future__ import annotations

import argparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def open_page_and_close(url: str, timeout_ms: int = 45_000) -> None:
	"""Abre a URL informada no Chromium e fecha o navegador com segurança."""
	with sync_playwright() as playwright:
		browser = playwright.chromium.launch(headless=True)
		context = browser.new_context()
		page = context.new_page()

		try:
			page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
			print(f"Page opened successfully: {url}")
		except PlaywrightTimeoutError:
			print(f"Timeout while opening page: {url}")
			raise
		finally:
			context.close()
			browser.close()


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Abre uma página com Playwright (Chromium) e fecha em seguida."
	)
	parser.add_argument("url", help="URL da página que será aberta")
	parser.add_argument(
		"--timeout-ms",
		type=int,
		default=45_000,
		help="Timeout em milissegundos para carregamento da página (padrão: 45000)",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	open_page_and_close(url=args.url, timeout_ms=args.timeout_ms)


if __name__ == "__main__":
	main()
