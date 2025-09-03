import os, re, json, time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

# === Configurações ===
current_dir = os.path.dirname(os.path.abspath(__file__))
input_csv = os.path.join(current_dir, "data", "csv", "produtos_link.csv")
output_csv = os.path.join(current_dir, "data", "exports", "produtos_leo_madeiras.csv")
output_folder = os.path.join(current_dir, "data", "exports", "imagens_produtos")

# Criar pastas necessárias
os.makedirs(output_folder, exist_ok=True)

# === Sessão HTTP ===
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
})

# === Mapeamentos VTEX ===
maps = {
    "departamento": {
        "MDF": "1", "Madeiras": "2", "Ferramentas Elétricas": "3",
        "Ferramentas Manuais": "4", "Máquinas Estacionárias": "5",
        "Acessórios para Ferramentas e Máquinas": "6", "Ferragens": "7",
        "Ferramentas Pneumáticas": "8", "Fitas e Tapa Furos": "9",
        "Químicos": "10", "Perfis de Alumínio": "11", "Iluminação e Elétrica": "12",
        "Revestimentos": "13", "Divisórias": "14", "EPI": "15",
        "Embalagens": "16", "Utilidades Domésticas": "17", "Construção": "18",
        "Catálogos e Expositores": "19"
    },
    "categoria": {
        "MDF": "1", "Madeiras": "2", "Furadeira": "3", "Parafusadeira": "4",
        "Furadeira de Impacto": "5", "Martelete": "6", "Serra Circular": "7",
        "Serra Meia-Esquadria": "8", "Serra de Bancada": "9", "Serra Tico Tico": "10",
        "Serra Mármore": "11", "Plaina": "12", "Pinador": "13", "Esmerilhadeira": "14",
        "Linha Laser": "15", "Soprador Térmico": "16", "Chave de Impacto": "17",
        "Tupia": "18", "Tico Tico de Bancada": "19"
    }
}

# === Funções Utilitárias ===
def limpar(texto):
    return re.sub(r"\s+", " ", (texto or "").strip())

def get_marca_id(marca_nome):
    """Retorna ID da marca no formato 2000XXX"""
    if not marca_nome:
        return "2000001"
    
    marca_upper = marca_nome.upper().strip()
    # Mapeamento simples de marcas conhecidas
    marcas_ids = {
        "KRESS": "2000001", "BOSCH": "2000002", "MAKITA": "2000003",
        "DEWALT": "2000004", "MILWAUKEE": "2000005", "BLACK+DECKER": "2000006",
        "STANLEY": "2000007", "METABO": "2000008", "HITACHI": "2000009",
        "PANASONIC": "2000010", "RYOBI": "2000011"
    }
    
    return marcas_ids.get(marca_upper, "2000001")

def parse_preco(texto):
    """Extrai preço de texto com formato brasileiro"""
    if not texto:
        return ""
    
    # Padrões de preço
    patterns = [
        r"R\$\s*([\d\.\s]+,\d{2})",
        r"([\d\.\s]+,\d{2})",
        r"([\d]+\.\d{2})"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, texto)
        if match:
            price_str = match.group(1).strip()
            try:
                price_clean = re.sub(r'[^\d,.]', '', price_str)
                if ',' in price_clean and '.' in price_clean:
                    price_clean = price_clean.replace('.', '').replace(',', '.')
                elif ',' in price_clean:
                    price_clean = price_clean.replace(',', '.')
                
                return f"{float(price_clean):.2f}"
            except:
                continue
    return ""

def renderizar_html(url):
    """Renderiza página via Playwright"""
    if not sync_playwright:
        print("⚠️ Playwright não disponível, usando HTML estático")
        r = session.get(url, timeout=20)
        return r.text
    
    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle", timeout=15000)
        html = page.content()
        browser.close()
        p.stop()
        return html
    except Exception as e:
        print(f"⚠️ Erro com Playwright: {e}")
        r = session.get(url, timeout=20)
        return r.text

def baixar_imagem(url_img, fname):
    """Baixa imagem do produto"""
    try:
        with session.get(url_img, stream=True, timeout=30) as resp:
            resp.raise_for_status()
            with open(os.path.join(output_folder, fname), "wb") as f:
                for chunk in resp.iter_content(8192):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception as e:
        print(f"⚠️ Erro ao baixar {url_img}: {e}")
        return False

# === Função Principal ===
def extrair_produto(url):
    """Extrai dados do produto da Leo Madeiras"""
    print(f"🔍 Processando: {url}")
    
    # Renderizar página
    html = renderizar_html(url)
    soup = BeautifulSoup(html, "html.parser")
    
    # === Extrair Nome ===
    nome = ""
    for sel in [".product-name h1", "h1.product-name", "h1", ".product-title"]:
        tag = soup.select_one(sel)
        if tag and tag.get_text(strip=True):
            nome_temp = limpar(tag.get_text(strip=True))
            if (nome_temp and 
                nome_temp.lower() not in ["onde você está?", "onde voce esta?", "navegação"] and
                len(nome_temp) > 5):
                nome = nome_temp
                break
    
    if not nome:
        # Extrair da URL
        url_parts = url.rstrip("/").split("/")
        if len(url_parts) >= 2:
            nome = url_parts[-1].replace("-", " ").title()
    
    if not nome:
        nome = "Sem Nome"
    
    print(f"✅ Nome: {nome}")
    
    # === Extrair Preço ===
    preco = ""
    
    # 1. data-price
    for element in soup.select("[data-price]"):
        data_price = element.get("data-price")
        if data_price:
            try:
                preco = f"{float(str(data_price).replace(',', '.')):.2f}"
                print(f"✅ Preço via data-price: {preco}")
                break
            except:
                pass
    
    # 2. data-sku-obj
    if not preco:
        for element in soup.select("[data-sku-obj]"):
            data_sku_obj = element.get("data-sku-obj")
            if data_sku_obj:
                try:
                    import html
                    decoded = html.unescape(data_sku_obj)
                    sku_data = json.loads(decoded)
                    
                    if "price" in sku_data:
                        preco = f"{float(str(sku_data['price']).replace(',', '.')):.2f}"
                        print(f"✅ Preço via data-sku-obj: {preco}")
                        break
                    elif "best" in sku_data and "price" in sku_data["best"]:
                        preco = f"{float(str(sku_data['best']['price']).replace(',', '.')):.2f}"
                        print(f"✅ Preço via data-sku-obj.best: {preco}")
                        break
                except:
                    continue
    
    # 3. Fallback: regex no texto
    if not preco:
        preco = parse_preco(soup.get_text(" ", strip=True))
        if preco:
            print(f"✅ Preço via regex: {preco}")
    
    if not preco:
        preco = "0.00"
        print("⚠️ Preço não encontrado")
    
    # === Extrair SKU ===
    sku = ""
    url_parts = url.rstrip("/").split("/")
    if len(url_parts) >= 2:
        sku = url_parts[-2]
    
    if not sku:
        sku = "SKU_" + str(int(time.time()))
    
    # === Extrair Marca ===
    marca = "Leo Madeiras"
    nome_lower = nome.lower()
    marcas_conhecidas = ["kress", "bosch", "makita", "dewalt", "milwaukee"]
    
    for marca_conhecida in marcas_conhecidas:
        if marca_conhecida in nome_lower:
            marca = marca_conhecida.title()
            break
    
    # === Detectar Categoria/Departamento ===
    nome_lower = nome.lower()
    
    if any(palavra in nome_lower for palavra in ["furadeira", "parafusadeira", "martelete", "serra"]):
        departamento = "Ferramentas Elétricas"
        categoria = "Furadeira" if "furadeira" in nome_lower else "Parafusadeira"
    elif any(palavra in nome_lower for palavra in ["mdf", "madeira"]):
        departamento = "Madeiras"
        categoria = "MDF" if "mdf" in nome_lower else "Madeiras"
    else:
        departamento = "Ferramentas Elétricas"
        categoria = "Ferramentas Elétricas"
    
    # === Extrair Imagens ===
    imgs = []
    for img in soup.select("img"):
        src = img.get("src") or img.get("data-src")
        if src and "data:image" not in src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png']):
            imgs.append(urljoin(url, src))
    
    # Baixar imagens
    saved = []
    if imgs:
        print(f"📸 Baixando {len(imgs[:5])} imagens...")
        with tqdm(total=len(imgs[:5]), desc="🖼️ Download imagens", 
                  bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as img_pbar:
            
            for i, img_url in enumerate(imgs[:5], 1):
                fname = f"{sku}_{i}.jpg"
                img_pbar.set_description(f"📥 Baixando {fname}")
                
                if baixar_imagem(img_url, fname):
                    saved.append(fname)
                    img_pbar.set_postfix({'Status': '✅ Sucesso'})
                else:
                    img_pbar.set_postfix({'Status': '❌ Falha'})
                
                img_pbar.update(1)
    else:
        print("⚠️ Nenhuma imagem encontrada para download")
    
    # === Gerar Produto ===
    produto = {
        "_IDSKU": sku,
        "_NomeSKU": nome,
        "_AtivarSKUSePossível": "SIM",
        "_SKUAtivo": "SIM",
        "_EANSKU": "",
        "_Altura": "", "_AlturaReal": "",
        "_Largura": "", "_LarguraReal": "",
        "_Comprimento": "", "_ComprimentoReal": "",
        "_Peso": "", "_PesoReal": "",
        "_UnidadeMedida": "un",
        "_MultiplicadorUnidade": "1,000000",
        "_CodigoReferenciaSKU": sku,
        "_ValorFidelidade": "",
        "_DataPrevisaoChegada": "",
        "_CodigoFabricante": "",
        "_IDProduto": sku,
        "_NomeProduto": nome,
        "_BreveDescricaoProduto": nome[:200],
        "_ProdutoAtivo": "SIM",
        "_CodigoReferenciaProduto": sku,
        "_MostrarNoSite": "SIM",
        "_LinkTexto": url.rstrip("/").split("/")[-1],
        "_DescricaoProduto": nome,
        "_DataLancamentoProduto": datetime.today().strftime("%d/%m/%Y"),
        "_PalavrasChave": "",
        "_TituloSite": nome,
        "_DescricaoMetaTag": nome[:160],
        "_IDFornecedor": "",
        "_MostrarSemEstoque": "SIM",
        "_Kit": "",
        "_IDDepartamento": maps["departamento"].get(departamento, ""),
        "_NomeDepartamento": departamento,
        "_IDCategoria": maps["categoria"].get(categoria, ""),
        "_NomeCategoria": categoria,
        "_IDMarca": get_marca_id(marca),
        "_Marca": marca,
        "_PesoCubico": "",
        "_Preço": preco,
        "_BaseUrlImagens": f"images-leo-madeiras-{sku}",
        "_ImagensSalvas": ";".join(saved),
        "_ImagensURLs": ";".join(imgs),
    }
    
    return produto

# === Execução Principal ===
if __name__ == "__main__":
    # Ler CSV de entrada
    try:
        df_links = pd.read_csv(input_csv)
        if "url" not in df_links.columns:
            raise Exception("❌ A planilha precisa ter uma coluna chamada 'url'.")
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        exit(1)
    
    # Processar produtos
    produtos = []
    
    # Filtrar apenas URLs válidas da Leo Madeiras
    urls_validas = []
    for _, row in df_links.iterrows():
        url = str(row["url"]).strip()
        if url and "leomadeiras.com.br" in url:
            urls_validas.append(url)
    
    if not urls_validas:
        print("❌ Nenhuma URL válida da Leo Madeiras encontrada")
        exit(1)
    
    print(f"🚀 Iniciando processamento de {len(urls_validas)} produtos...")
    
    # Barra de progresso principal
    with tqdm(total=len(urls_validas), desc="🔄 Scraping produtos", 
              bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
        
        for url in urls_validas:
            try:
                # Atualizar descrição da barra
                pbar.set_description(f"🔍 Processando: {url.split('/')[-1][:30]}...")
                
                resultado = extrair_produto(url)
                if resultado:
                    produtos.append(resultado)
                    pbar.set_postfix({
                        'SKU': resultado['_IDSKU'],
                        'Preço': f"R$ {resultado['_Preço']}",
                        'Marca': resultado['_Marca']
                    })
                else:
                    pbar.set_postfix({'Erro': 'Falha na extração'})
                
                time.sleep(1)  # Cortesia
                pbar.update(1)
                
            except Exception as e:
                pbar.set_postfix({'Erro': str(e)[:20]})
                pbar.update(1)
                continue
    
    # Salvar resultados
    if produtos:
        df_final = pd.DataFrame(produtos)
        df_final.to_csv(output_csv, index=False, encoding="utf-8-sig")
        
        print(f"\n✅ Planilha salva: {output_csv}")
        print(f"🖼️ Imagens em: {output_folder}")
        print(f"📊 Total processados: {len(produtos)}")
        
        # Estatísticas
        marca_counts = df_final['_Marca'].value_counts()
        print(f"\n🏷️ Marcas encontradas:")
        for marca, count in marca_counts.items():
            print(f"   {marca}: {count} produtos")
    else:
        print("❌ Nenhum produto processado")