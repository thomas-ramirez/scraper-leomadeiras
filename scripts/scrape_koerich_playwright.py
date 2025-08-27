#!/usr/bin/env python3
"""
Script para fazer scraping da página da Koerich usando Playwright
Útil para capturar conteúdo dinâmico (JavaScript)
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

async def scrape_koerich_with_playwright(url):
    """
    Faz scraping da página da Koerich usando Playwright
    """
    async with async_playwright() as p:
        # Inicia o navegador
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Configura o user agent
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        try:
            print(f"Navegando para: {url}")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Aguarda um pouco para garantir que o conteúdo dinâmico seja carregado
            await page.wait_for_timeout(3000)
            
            # Obtém o HTML da página
            html_content = await page.content()
            
            # Obtém informações adicionais
            title = await page.title()
            
            await browser.close()
            return html_content, title
            
        except Exception as e:
            print(f"Erro durante o scraping: {e}")
            await browser.close()
            return None, None

def save_html_to_file(html_content, filename=None, title=None):
    """
    Salva o conteúdo HTML em um arquivo
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"koerich_page_playwright_{timestamp}.html"
    
    # Cria o diretório data/exports se não existir
    output_dir = "data/exports"
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML salvo com sucesso em: {filepath}")
        return filepath
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
        return None

async def main():
    """
    Função principal
    """
    url = "https://www.koerich.com.br/p/frigobar-midea-45-litros-mrc06b2-branco/4043300"
    
    print("Iniciando scraping da página da Koerich com Playwright...")
    print(f"URL: {url}")
    print("-" * 50)
    
    # Faz o scraping
    html_content, title = await scrape_koerich_with_playwright(url)
    
    if html_content:
        print(f"Conteúdo HTML obtido com sucesso!")
        print(f"Tamanho do HTML: {len(html_content)} caracteres")
        
        if title:
            print(f"Título da página: {title}")
        
        # Salva o HTML em arquivo
        filename = "koerich_frigobar_midea_playwright.html"
        filepath = save_html_to_file(html_content, filename, title)
        
        if filepath:
            print(f"\n✅ Sucesso! O HTML foi salvo em: {filepath}")
        else:
            print("❌ Erro ao salvar o arquivo HTML")
    else:
        print("❌ Falha ao obter o conteúdo HTML da página")

if __name__ == "__main__":
    asyncio.run(main())
