import os, re, json, time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from pathlib import Path
from requests.adapters import HTTPAdapter, Retry
from contextlib import contextmanager

try:
    # Playwright é opcional; usado para páginas dinâmicas (Leo Madeiras)
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

downloads_path = str(Path.home() / "Downloads")
current_dir = os.path.dirname(os.path.abspath(__file__))  # Pasta atual do script

input_csv = os.path.join(current_dir, "data", "csv", "produtos_link.csv")
output_csv = os.path.join(current_dir, "data", "exports", "produtos_leo_madeiras.csv")
output_folder = os.path.join(current_dir, "data", "exports", "imagens_produtos")

df_links = pd.read_csv(input_csv)
if "url" not in df_links.columns:
    raise Exception("❌ A planilha precisa ter uma coluna chamada 'url'.")

os.makedirs(output_folder, exist_ok=True)

# === Sessão HTTP robusta ===
UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}
session = requests.Session()
session.headers.update(UA)
session.mount(
    "https://",
    HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])),
)

# === Mapeamentos VTEX (IDs) ===
maps = {
    "departamento": {
        "MDF": "1",
        "Madeiras": "2", 
        "Ferramentas Elétricas": "3",
        "Ferramentas Manuais": "4",
        "Máquinas Estacionárias": "5",
        "Acessórios para Ferramentas e Máquinas": "6",
        "Ferragens": "7",
        "Ferramentas Pneumáticas": "8",
        "Fitas e Tapa Furos": "9",
        "Químicos": "10",
        "Perfis de Alumínio": "11",
        "Iluminação e Elétrica": "12",
        "Revestimentos": "13",
        "Divisórias": "14",
        "EPI": "15",
        "Embalagens": "16",
        "Utilidades Domésticas": "17",
        "Construção": "18",
        "Catálogos e Expositores": "19"
    },
    "categoria": {
        "MDF": "1",
        "Madeiras": "2",
        "Furadeira": "3",
        "Parafusadeira": "4",
        "Furadeira de Impacto": "5",
        "Martelete": "6",
        "Serra Circular": "7",
        "Serra Meia-Esquadria": "8",
        "Serra de Bancada": "9",
        "Serra Tico Tico": "10",
        "Serra Mármore": "11",
        "Plaina": "12",
        "Pinador": "13",
        "Esmerilhadeira": "14",
        "Linha Laser": "15",
        "Soprador Térmico": "16",
        "Chave de Impacto": "17",
        "Tupia": "18",
        "Tico Tico de Bancada": "19"
    }
}

# Dicionário para mapeamento dinâmico de marcas
marca_mapping = {}
marca_counter = 1

# === Utils ===
def limpar(t):
    return re.sub(r"\s+", " ", (t or "").strip())

def get_marca_id(marca_nome):
    """Retorna o ID da marca no formato 2000XXX"""
    global marca_mapping, marca_counter
    
    if not marca_nome:
        return "2000001"  # Default
    
    marca_upper = marca_nome.upper().strip()
    
    if marca_upper not in marca_mapping:
        marca_mapping[marca_upper] = f"2000{marca_counter:03d}"
        marca_counter += 1
    
    return marca_mapping[marca_upper]

def parse_preco(texto):
    """Extrai preço de texto com diferentes formatos brasileiros"""
    if not texto:
        return ""
    
    # Padrões de preço brasileiros
    patterns = [
        # R$ 1.234,56 ou R$ 1234,56
        r"R\$\s*([\d\.\s]+,\d{2})",
        # R$ 1234.56 (formato internacional)
        r"R\$\s*([\d\.]+,\d{2})",
        # R$ 1234,56 (sem pontos)
        r"R\$\s*([\d]+,\d{2})",
        # Apenas números com vírgula: 1234,56
        r"([\d\.\s]+,\d{2})",
        # Apenas números com ponto: 1234.56
        r"([\d]+\.\d{2})",
        # Formato: 1.234,56 (sem R$)
        r"([\d\.\s]+,\d{2})",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, texto)
        if match:
            price_str = match.group(1).strip()
            
            try:
                # Limpar espaços e caracteres especiais
                price_clean = re.sub(r'[^\d,.]', '', price_str)
                
                # Converter para float baseado no formato
                if ',' in price_clean and '.' in price_clean:
                    # Formato: 1.234,56 -> 1234.56
                    price_clean = price_clean.replace('.', '').replace(',', '.')
                elif ',' in price_clean:
                    # Formato: 1234,56 -> 1234.56
                    price_clean = price_clean.replace(',', '.')
                # Se só tem ponto, já está no formato correto
                
                price_float = float(price_clean)
                return f"{price_float:.2f}"
                
            except (ValueError, TypeError):
                continue
    
    return ""

def get_jsonld(soup):
    """Extrai dados JSON-LD da página"""
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string)
            seq = data if isinstance(data, list) else [data]
            for it in seq:
                if isinstance(it, dict) and it.get("@type") in ("Product", "Offer", "AggregateOffer"):
                    return it
        except:
            continue
    return None

def parse_srcset(srcset):
    """Retorna a URL com maior resolução do srcset"""
    if not srcset:
        return ""
    
    parts = srcset.split(",")
    best_url = ""
    best_density = 0
    
    for part in parts:
        part = part.strip()
        if ' ' in part:
            url_part, density_part = part.rsplit(' ', 1)
            try:
                # Remove 'x' e converte para float
                density = float(density_part.replace('x', '').replace('w', ''))
                if density > best_density:
                    best_density = density
                    best_url = url_part.strip()
            except:
                # Se não conseguir parsear, usa a primeira URL
                if not best_url:
                    best_url = url_part.strip()
    
    return best_url if best_url else parts[0].strip().split(" ")[0].strip()

@contextmanager
def _playwright_context():
    if not sync_playwright:
        raise RuntimeError("Playwright não está disponível. Instale com: pip install playwright e python -m playwright install chromium")
    p = sync_playwright().start()
    try:
        yield p
    finally:
        p.stop()

def renderizar_html(url, wait_selectors=None, timeout_ms=15000):
    """Renderiza página via Chromium headless e retorna HTML.
    wait_selectors: lista de seletores CSS a esperar (qualquer um).
    """
    wait_selectors = wait_selectors or []
    with _playwright_context() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(timeout_ms)
            page.goto(url, wait_until="domcontentloaded")
            # tentar aguardar rede ociosa e algum seletor de conteúdo
            try:
                page.wait_for_load_state("networkidle", timeout=timeout_ms)
            except Exception:
                pass
            for sel in wait_selectors:
                try:
                    page.wait_for_selector(sel, state="attached", timeout=4000)
                    break
                except Exception:
                    continue
            return page.content()
        finally:
            browser.close()

def gerar_base_url_produto(sku, nome):
    """Gera baseUrl único para cada produto baseado no SKU e nome"""
    # Limpar nome para URL segura
    nome_limpo = re.sub(r'[^a-zA-Z0-9\s-]', '', nome).strip()
    nome_limpo = re.sub(r'\s+', '-', nome_limpo).lower()
    
    # Gerar baseUrl no formato: images-leadPOC-{sku}-{nome}
    base_url = f"images-leadPOC-{sku}-{nome_limpo}"
    return base_url

def baixar_imagem(url_img, fname):
    """Baixa imagem do produto"""
    try:
        # Adicionar headers para tentar obter imagem em melhor qualidade
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'identity',
            'Referer': 'https://www.leomadeiras.com.br/',
        }
        
        with session.get(url_img, headers=headers, stream=True, timeout=30) as resp:
            resp.raise_for_status()
            
            # Verificar se é realmente uma imagem
            content_type = resp.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"⚠️ URL não é uma imagem: {content_type}")
                return False
            
            # Verificar tamanho da imagem
            content_length = resp.headers.get('content-length')
            if content_length:
                size_kb = int(content_length) / 1024
                if size_kb < 1:  # Menos de 1KB, provavelmente thumbnail
                    print(f"⚠️ Imagem muito pequena ({size_kb:.1f}KB), pode ser thumbnail")
            
            with open(os.path.join(output_folder, fname), "wb") as f:
                for chunk in resp.iter_content(8192):
                    if chunk:
                        f.write(chunk)
        
        # Verificar se o arquivo foi criado e tem tamanho mínimo
        file_path = os.path.join(output_folder, fname)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size < 1024:  # Menos de 1KB
                print(f"⚠️ Arquivo muito pequeno ({file_size} bytes): {fname}")
                return False
        
        return True
    except Exception as e:
        print(f"⚠️ Erro ao baixar imagem {url_img}: {e}")
        return False

def extract_leo_madeiras_price(soup, url):
    """Extrai preço especificamente para páginas da Leo Madeiras"""
    preco = ""
    
    # 1. Procurar por atributos data-* que contenham dados do produto
    data_selectors = [
        "[data-sku-obj]",
        "[data-price]",
        "[data-originprice]"
    ]
    
    for selector in data_selectors:
        elements = soup.select(selector)
        for element in elements:
            # data-sku-obj (Leo Madeiras)
            if selector == "[data-sku-obj]":
                data_sku_obj = element.get("data-sku-obj")
                if data_sku_obj:
                    try:
                        import html
                        decoded = html.unescape(data_sku_obj)
                        sku_data = json.loads(decoded)
                        
                        # Procurar por preço em diferentes campos
                        if "price" in sku_data:
                            preco = f"{float(str(sku_data['price']).replace(',', '.')):.2f}"
                            print(f"✅ Preço encontrado via data-sku-obj.price: {preco}")
                            return preco
                        elif "best" in sku_data and "price" in sku_data["best"]:
                            preco = f"{float(str(sku_data['best']['price']).replace(',', '.')):.2f}"
                            print(f"✅ Preço encontrado via data-sku-obj.best.price: {preco}")
                            return preco
                    except Exception as e:
                        print(f"⚠️ Erro ao parsear data-sku-obj: {e}")
                        continue
            
            # data-price
            elif selector == "[data-price]":
                data_price = element.get("data-price")
                if data_price:
                    try:
                        preco = f"{float(str(data_price).replace(',', '.')):.2f}"
                        print(f"✅ Preço encontrado via data-price: {preco}")
                        return preco
                    except:
                        pass
    
    # 2. Procurar por templates Handlebars que contenham preços
    handlebars_templates = soup.find_all("script", type="text/x-handlebars-template")
    for template in handlebars_templates:
        if template.string:
            template_text = template.string
            
            # Procurar por padrões de preço em templates Handlebars
            price_patterns = [
                r'\{\{formatNumber\s+sku\.best\.price\}\}',
                r'\{\{sku\.best\.price\}\}',
                r'\{\{formatNumber\s+sku\.price\}\}',
                r'\{\{sku\.price\}\}'
            ]
            
            for pattern in price_patterns:
                if re.search(pattern, template_text):
                    print(f"✅ Template Handlebars com preço encontrado: {pattern}")
                    # Se encontrou template, pode indicar que o preço é carregado dinamicamente
    
    # 3. Procurar por elementos que possam conter preço renderizado
    price_elements = soup.select(".price, .product-price, .current-price, [class*='price']")
    for element in price_elements:
        price_text = element.get_text(strip=True)
        if price_text:
            # Remover texto extra e manter apenas números
            price_clean = re.sub(r'[^\d,.]', '', price_text)
            if price_clean:
                try:
                    # Converter para float
                    if ',' in price_clean and '.' in price_clean:
                        # Formato: 1.234,56
                        price_clean = price_clean.replace('.', '').replace(',', '.')
                    elif ',' in price_clean:
                        # Formato: 1234,56
                        price_clean = price_clean.replace(',', '.')
                    
                    preco = f"{float(price_clean):.2f}"
                    print(f"✅ Preço encontrado via elementos de preço: {preco}")
                    return preco
                except:
                    continue
    
    return preco

# === Core ===
def extrair_produto(url):
    """Extrai dados do produto da Leo Madeiras"""
    
    # Verificar se é uma URL da Leo Madeiras
    if "leomadeiras.com.br" not in url:
        print(f"⚠️ URL não é da Leo Madeiras: {url}")
        return None
    
    print(f"🔍 Processando produto da Leo Madeiras: {url}")
    
    # Usar Playwright para renderizar JavaScript (Leo Madeiras carrega preços dinamicamente)
    try:
        html = renderizar_html(
            url,
            wait_selectors=[
                "h1", 
                ".product-name",
                ".product-price",
                ".price",
                "[data-price]",
                "[data-sku-obj]",
                ".product-images"
            ],
            timeout_ms=30000,
        )
        print(f"✅ Página renderizada via JavaScript para {url}")
    except Exception as e:
        print(f"⚠️ Erro com Playwright para {url}: {e}")
        # fallback: tentar HTML não renderizado
        r = session.get(url, timeout=20)
        r.raise_for_status()
        html = r.text
    
    soup = BeautifulSoup(html, "html.parser")

    # --- Extrair dados básicos ---
    jsonld = get_jsonld(soup) or {}
    nome = limpar(jsonld.get("name")) if jsonld else ""
    descricao = limpar(jsonld.get("description")) if jsonld else ""
    preco = ""
    imgs = []

    # --- Nome do produto ---
    if not nome:
        for sel in [".product-name h1", "h1.product-name", "h1", ".product-title"]:
            tag = soup.select_one(sel)
            if tag and tag.get_text(strip=True):
                nome = limpar(tag.get_text(strip=True))
                break
        if not nome:
            nome = "Sem Nome"

    # --- PREÇO (prioridade para Leo Madeiras) ---
    # 1. Função específica para Leo Madeiras
    preco = extract_leo_madeiras_price(soup, url)
    
    # 2. Fallback: JSON-LD
    if not preco and isinstance(jsonld, dict):
        offers = jsonld.get("offers") or {}
        if isinstance(offers, dict) and offers.get("price"):
            try:
                preco = f"{float(str(offers['price']).replace(',', '.')):.2f}"
                print(f"✅ Preço encontrado via JSON-LD offers.price: {preco}")
            except:
                pass
        elif isinstance(offers, list) and len(offers) > 0:
            for offer in offers:
                if isinstance(offer, dict) and offer.get("price"):
                    try:
                        preco = f"{float(str(offer['price']).replace(',', '.')):.2f}"
                        print(f"✅ Preço encontrado via JSON-LD offers[].price: {preco}")
                        break
                    except:
                        continue

    # 3. Fallback: regex no texto da página
    if not preco:
        preco = parse_preco(soup.get_text(" ", strip=True))
        if preco:
            print(f"✅ Preço encontrado via regex no texto: {preco}")

    # Verificar se encontrou preço
    if preco:
        print(f"💰 Preço final extraído: R$ {preco}")
    else:
        print(f"⚠️ Nenhum preço encontrado para {url}")

    # --- Descrição ---
    if not descricao:
        for sel in [".product-description", ".description", ".product-details", ".product-info", ".about-product"]:
            tag = soup.select_one(sel)
            if tag and tag.get_text(strip=True):
                descricao = limpar(tag.get_text(strip=True))
                break

    # --- Categoria e Departamento ---
    NomeDepartamento = ""
    NomeCategoria = ""
    
    # Procurar por breadcrumbs da Leo Madeiras
    breadcrumb_selectors = [
        ".breadcrumb a",
        "nav.breadcrumb a", 
        ".breadcrumbs a",
        "[class*='breadcrumb'] a"
    ]
    
    for selector in breadcrumb_selectors:
        breadcrumb_links = soup.select(selector)
        if breadcrumb_links:
            breadcrumb_names = []
            for link in breadcrumb_links:
                text = limpar(link.get_text())
                if text and text.lower() not in ("início", "inicio", "home", "página inicial"):
                    breadcrumb_names.append(text)
            
            if len(breadcrumb_names) >= 2:
                NomeDepartamento = breadcrumb_names[-2]  # Penúltimo item
                NomeCategoria = breadcrumb_names[-1]     # Último item
            elif len(breadcrumb_names) == 1:
                NomeCategoria = breadcrumb_names[0]
            break

    # Fallback: detectar baseado no nome do produto
    if not NomeDepartamento or not NomeCategoria:
        nome_lower = nome.lower()
        
        # Detectar departamento
        if any(palavra in nome_lower for palavra in ["furadeira", "parafusadeira", "martelete", "serra", "plaina", "esmerilhadeira"]):
            NomeDepartamento = "Ferramentas Elétricas"
        elif any(palavra in nome_lower for palavra in ["mdf", "madeira", "compensado", "painel"]):
            NomeDepartamento = "Madeiras"
        elif any(palavra in nome_lower for palavra in ["ferragem", "dobradiça", "puxador"]):
            NomeDepartamento = "Ferragens"
        else:
            NomeDepartamento = "Ferramentas Elétricas"  # Default
        
        # Detectar categoria específica
        if "furadeira" in nome_lower:
            NomeCategoria = "Furadeira"
        elif "parafusadeira" in nome_lower:
            NomeCategoria = "Parafusadeira"
        elif "serra" in nome_lower:
            NomeCategoria = "Serra Circular"
        elif "mdf" in nome_lower:
            NomeCategoria = "MDF"
        else:
            NomeCategoria = "Ferramentas Elétricas"  # Default

    # --- SKU ---
    sku = ""
    
    # Tentar extrair SKU da URL
    if "leomadeiras.com.br" in url:
        # URL da Leo Madeiras: /p/{sku}/{nome-produto}
        url_parts = url.rstrip("/").split("/")
        if len(url_parts) >= 2:
            sku = url_parts[-2]  # Penúltimo item da URL
    
    # Fallback: meta tag
    if not sku:
        meta_sku = soup.find("meta", {"itemprop": "sku"})
        if meta_sku and meta_sku.get("content"):
            sku = meta_sku["content"].strip()
    
    # Fallback: slug da URL
    if not sku:
        sku = url.rstrip("/").split("/")[-1]

    # --- Marca ---
    Marca = ""
    
    # Procurar por marca em especificações
    specs_section = soup.select_one(".specifications, .product-specifications")
    if specs_section:
        specs_text = specs_section.get_text(strip=True)
        marca_match = re.search(r"Marca[:\-]\s*([^\n\r]+)", specs_text, re.IGNORECASE)
        if marca_match:
            Marca = limpar(marca_match.group(1))
    
    # Fallback: extrair marca do nome do produto
    if not Marca:
        nome_lower = nome.lower()
        marcas_conhecidas = [
            "kress", "bosch", "makita", "dewalt", "milwaukee", "black+decker",
            "stanley", "metabo", "hitachi", "panasonic", "ryobi"
        ]
        
        for marca in marcas_conhecidas:
            if marca in nome_lower:
                Marca = marca.title()
                break
        
        # Se não encontrou marca específica, usar "Leo Madeiras" como padrão
        if not Marca:
            Marca = "Leo Madeiras"

    # --- IDs VTEX ---
    _IDDepartamento = maps["departamento"].get(NomeDepartamento, "")
    _IDCategoria = maps["categoria"].get(NomeCategoria, "")
    _IDMarca = get_marca_id(Marca)

    # --- Imagens ---
    # Procurar por imagens do produto
    for img in soup.select("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or parse_srcset(img.get("srcset"))
        if src and "data:image" not in src and "blank" not in src.lower():
            # Filtrar imagens que parecem ser do produto
            if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                # Remover parâmetros de redimensionamento
                clean_src = src.split('&')[0] if '&' in src else src
                imgs.append(clean_src)

    # <source srcset> para imagens responsivas
    for source in soup.select("source"):
        srcset = source.get("srcset")
        url_first = parse_srcset(srcset)
        if url_first and "data:image" not in url_first:
            imgs.append(url_first)

    # Dedup mantendo ordem + normaliza para URL absoluta
    seen, ordered = set(), []
    for u in imgs:
        u_abs = urljoin(url, u)
        if u_abs not in seen:
            seen.add(u_abs)
            ordered.append(u_abs)
    
    # Filtrar apenas imagens do produto (que contenham o SKU)
    imgs_produto = []
    for img in ordered:
        if sku in img or any(sku_part in img for sku_part in sku.split('-')[:2]):
            imgs_produto.append(img)
    
    # Se não encontrou imagens específicas do produto, usar as primeiras 5
    if not imgs_produto:
        imgs_produto = ordered[:5]
    
    imgs = imgs_produto[:5]

    # Gerar baseUrl único para este produto
    base_url_produto = gerar_base_url_produto(sku, nome)
    
    # Baixa até 5 imagens
    saved = []
    for i, u in enumerate(imgs, 1):
        fname = f"{sku}_{i}.jpg"
        if baixar_imagem(u, fname):
            saved.append(fname)

    # Gerar linha do produto
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
        "_BreveDescricaoProduto": (descricao or "")[:200],
        "_ProdutoAtivo": "SIM",
        "_CodigoReferenciaProduto": sku,
        "_MostrarNoSite": "SIM",
        "_LinkTexto": url.rstrip("/").split("/")[-1],
        "_DescricaoProduto": descricao or "",
        "_DataLancamentoProduto": datetime.today().strftime("%d/%m/%Y"),
        "_PalavrasChave": "",
        "_TituloSite": nome,
        "_DescricaoMetaTag": (descricao or "")[:160],
        "_IDFornecedor": "",
        "_MostrarSemEstoque": "SIM",
        "_Kit": "",
        "_IDDepartamento": _IDDepartamento,
        "_NomeDepartamento": NomeDepartamento,
        "_IDCategoria": _IDCategoria,
        "_NomeCategoria": NomeCategoria,
        "_IDMarca": _IDMarca,
        "_Marca": Marca,
        "_PesoCubico": "",
        "_Preço": preco,
        "_BaseUrlImagens": base_url_produto,
        "_ImagensSalvas": ";".join(saved),
        "_ImagensURLs": ";".join(imgs),
    }
    
    return produto

# === Loop principal ===
produtos = []
for _, row in df_links.iterrows():
    url = str(row["url"]).strip()
    if not url:
        continue
    
    # Verificar se é URL da Leo Madeiras
    if "leomadeiras.com.br" not in url:
        print(f"⚠️ Pulando URL que não é da Leo Madeiras: {url}")
        continue
    
    try:
        resultado = extrair_produto(url)
        if resultado:
            produtos.append(resultado)
        time.sleep(1)  # cortesia para evitar sobrecarga
    except Exception as e:
        print(f"❌ Erro ao processar {url}: {e}")

# Salvar CSV
if produtos:
    df_final = pd.DataFrame(produtos)
    df_final.to_csv(output_csv, index=False, encoding="utf-8-sig")
    
    # Mostrar estatísticas
    print(f"\n✅ Planilha final salva: {output_csv}")
    print(f"🖼️ Imagens em: {output_folder}")
    print(f"📊 Total de produtos processados: {len(produtos)}")
    
    # Estatísticas de marcas
    marca_counts = df_final['_Marca'].value_counts()
    print(f"\n🏷️ Marcas encontradas:")
    for marca, count in marca_counts.items():
        marca_id = get_marca_id(marca)
        print(f"   {marca} (ID: {marca_id}): {count} produtos")
    
    print(f"\n📋 Mapeamento completo de marcas:")
    for marca, marca_id in sorted(marca_mapping.items()):
        count = marca_counts.get(marca, 0)
        print(f"   {marca} → {marca_id} ({count} produtos)")
else:
    print("❌ Nenhum produto foi processado com sucesso")