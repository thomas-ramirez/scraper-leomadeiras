#!/usr/bin/env python3
"""
Script para fazer scraping da página da Koerich e salvar o HTML
"""

import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time

def scrape_koerich_page(url):
    """
    Faz scraping da página da Koerich e retorna o HTML
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"Fazendo requisição para: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Verifica se a resposta é HTML
        if 'text/html' not in response.headers.get('content-type', ''):
            print("Aviso: A resposta não parece ser HTML")
        
        return response.text
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer requisição: {e}")
        return None

def save_html_to_file(html_content, filename=None):
    """
    Salva o conteúdo HTML em um arquivo
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"koerich_page_{timestamp}.html"
    
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

def main():
    """
    Função principal
    """
    url = "https://www.koerich.com.br/p/frigobar-midea-45-litros-mrc06b2-branco/4043300"
    
    print("Iniciando scraping da página da Koerich...")
    print(f"URL: {url}")
    print("-" * 50)
    
    # Faz o scraping
    html_content = scrape_koerich_page(url)
    
    if html_content:
        print(f"Conteúdo HTML obtido com sucesso!")
        print(f"Tamanho do HTML: {len(html_content)} caracteres")
        
        # Salva o HTML em arquivo
        filename = "koerich_frigobar_midea.html"
        filepath = save_html_to_file(html_content, filename)
        
        if filepath:
            print(f"\n✅ Sucesso! O HTML foi salvo em: {filepath}")
            
            # Mostra algumas informações sobre o conteúdo
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.find('title')
            if title:
                print(f"Título da página: {title.get_text().strip()}")
            
            # Conta elementos importantes
            images = soup.find_all('img')
            links = soup.find_all('a')
            print(f"Imagens encontradas: {len(images)}")
            print(f"Links encontrados: {len(links)}")
            
        else:
            print("❌ Erro ao salvar o arquivo HTML")
    else:
        print("❌ Falha ao obter o conteúdo HTML da página")

if __name__ == "__main__":
    main()
