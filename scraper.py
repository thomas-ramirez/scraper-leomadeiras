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

# === Sessão HTTP Otimizada ===
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.leomadeiras.com.br/"
})

# Configurações de performance para conexões HTTP
from requests.adapters import HTTPAdapter
session.mount('http://', HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=1
))
session.mount('https://', HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=1
))

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

# Variáveis globais para reutilizar browser
_playwright_instance = None
_browser = None
_context = None

def get_playwright_instance():
    """Retorna instância reutilizável do Playwright"""
    global _playwright_instance, _browser, _context
    
    if _playwright_instance is None and sync_playwright is not None:
        _playwright_instance = sync_playwright().start()
        _browser = _playwright_instance.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        )
        _context = _browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
    
    return _playwright_instance, _browser, _context

def cleanup_playwright():
    """Limpa recursos do Playwright"""
    global _playwright_instance, _browser, _context
    
    if _context:
        _context.close()
    if _browser:
        _browser.close()
    if _playwright_instance:
        _playwright_instance.stop()
    
    _playwright_instance = None
    _browser = None
    _context = None

def renderizar_html(url):
    """Renderiza página via Playwright com otimizações"""
    if not sync_playwright:
        print("⚠️ Playwright não disponível, usando HTML estático")
        r = session.get(url, timeout=10)
        return r.text
    
    try:
        _, _, context = get_playwright_instance()
        if context is None:
            raise Exception("Context não disponível")
            
        page = context.new_page()
        
        # Otimizações de performance
        page.set_default_timeout(15000)  # Aumentado para 15s para páginas complexas
        page.set_default_navigation_timeout(15000)
        
        # NÃO desabilitar JavaScript - precisamos dele para carregar as imagens
        page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf,eot}", lambda route: route.abort())
        # page.route("**/*.{css,js}", lambda route: route.abort())  # Comentado para permitir JS
        
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded", timeout=10000)  # Aumentado para 10s
        
        # Aguardar um pouco mais para JavaScript carregar as imagens
        page.wait_for_timeout(2000)
        
        html = page.content()
        page.close()
        return html
        
    except Exception as e:
        print(f"⚠️ Erro com Playwright: {e}")
        r = session.get(url, timeout=10)
        return r.text

def baixar_imagem(url_img, fname):
    """Baixa imagem do produto com otimizações"""
    try:
        with session.get(url_img, stream=True, timeout=15) as resp:  # Reduzido de 30s para 15s
            resp.raise_for_status()
            with open(os.path.join(output_folder, fname), "wb") as f:
                for chunk in resp.iter_content(16384):  # Aumentado de 8KB para 16KB
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
    
    # === Extrair Descrição ===
    descricao = ""
    
    # 1. Tentar extrair da seção de descrição do produto
    descricao_selectors = [
        ".product-description",
        ".product-details",
        ".description",
        ".produto-descricao",
        ".descricao-produto",
        "[data-description]",
        ".product-info .description",
        ".product-content .description"
    ]
    
    for selector in descricao_selectors:
        desc_tag = soup.select_one(selector)
        if desc_tag:
            desc_text = desc_tag.get_text(" ", strip=True)
            if desc_text and len(desc_text) > 50:  # Descrição deve ter pelo menos 50 caracteres
                descricao = limpar(desc_text)
                print(f"✅ Descrição encontrada via selector: {selector}")
                break
    
    # 2. Tentar extrair de elementos com texto descritivo
    if not descricao:
        for tag in soup.find_all(["p", "div", "span"]):
            if tag.get_text(strip=True):
                text = tag.get_text(strip=True)
                # Verificar se parece uma descrição de produto
                if (len(text) > 100 and 
                    any(keyword in text.lower() for keyword in ["aplicações", "benefícios", "características", "especificações", "detalhes", "informações"])):
                    descricao = limpar(text)
                    print(f"✅ Descrição encontrada via texto descritivo")
                    break
    
    # 3. Fallback: usar nome do produto
    if not descricao:
        descricao = nome
        print(f"⚠️ Descrição não encontrada, usando nome do produto")
    
    print(f"📝 Descrição extraída: {descricao[:100]}...")
    
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
                    if isinstance(data_sku_obj, str):
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
    
    # Buscar especificamente por imagens de produtos nos elementos com zoom
    # Prioridade 1: Imagens dentro de divs com data-zoom-image (mais confiável)
    for zoom_div in soup.select("div[data-zoom-image]"):
        zoom_img_url = zoom_div.get("data-zoom-image")
        if zoom_img_url and isinstance(zoom_img_url, str) and "cws.digital" in zoom_img_url:
            # Verificar se é uma imagem válida
            if any(ext in zoom_img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                imgs.append(zoom_img_url)
                print(f"✅ Imagem encontrada via data-zoom-image: {zoom_img_url}")
    
    # Prioridade 2: Imagens dentro de divs com classe "zoom" ou similares
    for zoom_div in soup.select("div.zoom, div[class*='zoom'], div[class*='image']"):
        for img in zoom_div.select("img"):
            src = img.get("src") or img.get("data-src")
            if src and isinstance(src, str) and "cws.digital" in src:
                if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    if src not in imgs:  # Evitar duplicatas
                        imgs.append(src)
                        print(f"✅ Imagem encontrada via div zoom: {src}")
    
    # Prioridade 3: Imagens com classe "zoomImg" (imagens de zoom dos produtos)
    for img in soup.select("img.zoomImg"):
        src = img.get("src") or img.get("data-src")
        if src and isinstance(src, str) and "cws.digital" in src:
            if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                if src not in imgs:  # Evitar duplicatas
                    imgs.append(src)
                    print(f"✅ Imagem encontrada via classe zoomImg: {src}")
    
    # Prioridade 4: Imagens com classe "original" (geralmente são as principais)
    for img in soup.select("img.original"):
        src = img.get("src") or img.get("data-src")
        if src and isinstance(src, str) and "cws.digital" in src:
            if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                if src not in imgs:  # Evitar duplicatas
                    imgs.append(src)
                    print(f"✅ Imagem encontrada via classe original: {src}")
    
    # Prioridade 4: Buscar por imagens específicas de produtos (mais rigoroso)
    if not imgs:
        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src")
            if not src or "data:image" in src:
                continue
                
            if isinstance(src, str):
                src_lower = src.lower()
                
                # Verificar extensão de imagem
                if not any(ext in src_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    continue
                
                # Verificar se é uma imagem de produto (deve conter "/produtos/" e ser do domínio correto)
                if ("/produtos/" in src_lower and 
                    "cws.digital" in src_lower and
                    not any(exclude in src_lower for exclude in ["/multimidia/", "/fornecedores/", "instagram", "facebook", "linkedln"])):
                    
                    if src not in imgs:  # Evitar duplicatas
                        imgs.append(src)
                        print(f"✅ Imagem encontrada via padrão produto: {src}")
                        if len(imgs) >= 5:  # Limite de 5 imagens
                            break
    
    # Prioridade 5: Buscar por imagens que contenham o SKU específico (último recurso)
    if not imgs:
        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src")
            if not src or "data:image" in src:
                continue
                
            if isinstance(src, str):
                src_lower = src.lower()
                
                # Verificar extensão de imagem
                if not any(ext in src_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    continue
                
                # Verificar se contém SKU específico
                if sku in src_lower:
                    if src not in imgs:  # Evitar duplicatas
                        imgs.append(src)
                        print(f"✅ Imagem encontrada via SKU: {src}")
                        if len(imgs) >= 5:  # Limite de 5 imagens
                            break
    
    # Prioridade 6: Buscar por imagens que seguem o padrão dos produtos que funcionam
    if not imgs:
        print(f"🔍 Buscando por imagens com padrão de produto...")
        
        # Buscar por qualquer imagem que contenha "/produtos/" e seja do domínio correto
        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src")
            if not src or "data:image" in src:
                continue
                
            if isinstance(src, str):
                src_lower = src.lower()
                
                # Verificar extensão de imagem
                if not any(ext in src_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    continue
                
                # Verificar se é uma imagem de produto (deve conter "/produtos/" e ser do domínio correto)
                if ("/produtos/" in src_lower and 
                    "cws.digital" in src_lower and
                    not any(exclude in src_lower for exclude in ["/multimidia/", "/fornecedores/", "instagram", "facebook", "linkedln", "youtube", "pinterest", "tiktok"])):
                    
                    if src not in imgs:  # Evitar duplicatas
                        imgs.append(src)
                        print(f"✅ Imagem encontrada via padrão produto: {src}")
                        if len(imgs) >= 5:  # Limite de 5 imagens
                            break
    
    # Remover duplicatas e limitar a 5 imagens
    imgs = list(dict.fromkeys(imgs))[:5]  # dict.fromkeys preserva ordem e remove duplicatas
    
    print(f"📸 Encontradas {len(imgs)} imagens do produto (SKU: {sku})")
    
    # Baixar imagens
    saved = []
    if imgs:
        print(f"📸 Baixando {len(imgs)} imagens...")
        with tqdm(total=len(imgs), desc="🖼️ Download imagens", 
                  bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as img_pbar:
            
            for i, img_url in enumerate(imgs, 1):
                fname = f"{sku}_{i}.jpg"
                img_pbar.set_description(f"📥 Baixando {fname}")
                
                # As URLs já são completas, não precisamos de urljoin
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
        "_BreveDescricaoProduto": descricao[:200] if descricao else nome[:200],
        "_ProdutoAtivo": "SIM",
        "_CodigoReferenciaProduto": sku,
        "_MostrarNoSite": "SIM",
        "_LinkTexto": url.rstrip("/").split("/")[-1],
        "_DescricaoProduto": descricao if descricao else nome,
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
    
    # Limpar recursos do Playwright
    cleanup_playwright()