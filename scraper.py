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
    # Playwright é opcional; usado para páginas dinâmicas (ex.: Colcci)
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

downloads_path = str(Path.home() / "Downloads")
current_dir = os.path.dirname(os.path.abspath(__file__))  # Pasta atual do script

input_csv = os.path.join(current_dir, "data", "csv", "produtos_link.csv")
output_csv = os.path.join(current_dir, "data", "exports", "produtos_vtex.csv")
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
        "Feminino": "1",
        "Masculino": "2", 
        "Acessórios": "3",
        "Calçados": "4",
        "Bolsas": "5",
        "Bijuterias": "6",
        "Perfumes": "7",
        "Esportes": "8",
        "Praia": "9",
        "Festa": "10",
        # Adicione mais conforme necessário
    },
    "categoria": {
        "Vestidos": "1",
        "Blusas": "2",
        "Calças": "3",
        "Saias": "4",
        "Blazers": "5",
        "Camisetas": "6",
        "Camisas": "7",
        "Bermudas": "8",
        "Jaquetas": "9",
        "Regatas": "10",
        "Shorts": "11",
        "Macacões": "12",
        "Tops": "13",
        "Cardigãs": "14",
        "Casacos": "15",
        # Adicione mais conforme necessário
    },
    "marca": {
        "Colcci": "1",
        "Colcci Jeans": "2",
        "Colcci Sport": "3",
        "Colcci Beach": "4",
        "Colcci Festa": "5",
        "Colcci Acessórios": "6",
        # Adicione mais conforme necessário
    }
}

# === Utils ===
def limpar(t):
    return re.sub(r"\s+", " ", (t or "").strip())

def parse_preco(texto):
    # 1ª ocorrência de R$ xxx,xx
    m = re.search(r"R\$\s*([\d\.\s]+,\d{2})", texto)
    if not m:
        return ""
    br = m.group(1).replace(".", "").replace(" ", "").replace(",", ".")
    try:
        return f"{float(br):.2f}"
    except:
        return ""

def get_next_data(soup):
    tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
    if not tag:
        return None
    try:
        return json.loads(tag.string)
    except:
        return None

def get_jsonld(soup):
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
    # retorna a 1ª URL do srcset
    # ex: "https://a.jpg 1x, https://b.jpg 2x" -> "https://a.jpg"
    if not srcset:
        return ""
    first = srcset.split(",")[0].strip().split(" ")[0].strip()
    return first

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
    
    # Gerar baseUrl no formato: images-{leadPOC}-{sku}-{nome}
    base_url = f"images-leadPOC-{sku}-{nome_limpo}"
    return base_url

def baixar_imagem(url_img, fname):
    try:
        with session.get(url_img, stream=True, timeout=20) as resp:
            resp.raise_for_status()
            with open(os.path.join(output_folder, fname), "wb") as f:
                for chunk in resp.iter_content(8192):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception as e:
        print(f"⚠️ Erro ao baixar imagem {url_img}: {e}")
        return False

# === Core ===
def extrair_produto(url):
    # Colcci entrega conteúdo via JS; usar Playwright para renderizar
    if "colcci.com.br" in url:
        try:
            html = renderizar_html(
                url,
                wait_selectors=[
                    "h1", 
                    "[class*='breadcrumb'] a",
                    "[class*='price'], [class*='preco'], [class*='valor']",
                ],
                timeout_ms=20000,
            )
        except Exception:
            # fallback: tentar HTML não renderizado
            r = session.get(url, timeout=20)
            r.raise_for_status()
            html = r.text
        soup = BeautifulSoup(html, "html.parser")
    else:
        r = session.get(url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")

    # --- JSON-LD (prioritário para nome/descrição/preço/imagens) ---
    jsonld = get_jsonld(soup) or {}
    nome = limpar(jsonld.get("name")) if jsonld else ""
    descricao = limpar(jsonld.get("description")) if jsonld else ""
    preco = ""
    imgs = []

    # Imagens do JSON-LD (string ou lista)
    if isinstance(jsonld, dict) and jsonld.get("image"):
        if isinstance(jsonld["image"], list):
            for img in jsonld["image"]:
                if isinstance(img, str):
                    imgs.append(img)
        elif isinstance(jsonld["image"], str):
            imgs.append(jsonld["image"])

    # --- __NEXT_DATA__ (Next.js) para imagens de alta e campos internos ---
    nd = get_next_data(soup)
    if nd:
        def find_images(obj):
            found = []
            if isinstance(obj, dict):
                # chaves comuns em projetos Next/VTEX
                if "imageUrl" in obj and isinstance(obj["imageUrl"], str):
                    found.append(obj["imageUrl"])
                if "images" in obj and isinstance(obj["images"], list):
                    for it in obj["images"]:
                        if isinstance(it, dict) and "imageUrl" in it and isinstance(it["imageUrl"], str):
                            found.append(it["imageUrl"])
                for v in obj.values():
                    found.extend(find_images(v))
            elif isinstance(obj, list):
                for v in obj:
                    found.extend(find_images(v))
            return found

        next_images = find_images(nd)
        imgs += next_images

        # Nome (fallback a partir do Next)
        if not nome:
            try:
                prod = nd["props"]["pageProps"]["product"]
                for key in ("productName", "name", "title"):
                    if prod.get(key):
                        nome = limpar(prod[key])
                        break
            except Exception:
                pass

    # --- HTML Fallbacks (MercadoCar) ---
    # Nome do produto
    if not nome:
        for sel in ["div.product-name h1", "h1"]:
            tag = soup.select_one(sel)
            if tag and tag.get_text(strip=True):
                nome = limpar(tag.get_text(strip=True))
                break
        if not nome:
            nome = "Sem Nome"

    # Preço: JSON-LD (offers.price) -> regex HTML
    if not preco and isinstance(jsonld, dict):
        offers = jsonld.get("offers") or {}
        if isinstance(offers, dict) and offers.get("price"):
            try:
                preco = f"{float(str(offers['price']).replace(',', '.')):.2f}"
            except:
                pass
    if not preco:
        preco = parse_preco(soup.get_text(" ", strip=True))

    # Descrição: classes típicas MercadoCar + fallback por texto âncora
    if not descricao:
        for sel in [".full-description", ".product-description", ".descriptions-text", ".productDetails", ".descricao"]:
            tag = soup.select_one(sel)
            if tag and tag.get_text(strip=True):
                descricao = limpar(tag.get_text(" ", strip=True))
                break
        if not descricao:
            t = soup.find(string=lambda s: s and "Aplicável ao(s) veículo(s)" in s)
            if t:
                container = t.find_parent(["div", "section", "article"])
                if container:
                    descricao = limpar(container.get_text(" ", strip=True))
    # Fallback adicional (Colcci): procurar blocos com título "Composição" ou "Descrição"
    if "colcci.com.br" in url and not descricao:
        # procurar por cabeçalhos ou labels
        possiveis = []
        for lab in ("Composição", "Composicao", "Descrição", "Descricao", "Detalhes"):
            node = soup.find(string=lambda s: isinstance(s, str) and lab.lower() in s.lower())
            if node:
                cont = node.find_parent(["div", "section", "article", "li", "p", "dt", "h2", "h3"]) or node.parent
                if cont:
                    possiveis.append(limpar(cont.get_text(" ", strip=True)))
        if possiveis:
            # escolher o mais longo
            descricao = max(possiveis, key=len)

        # --- Breadcrumb Schema.org -> Departamento/Categoria ---
    NomeDepartamento = ""
    NomeCategoria = ""
    
    # Buscar breadcrumb estruturado (schema.org)
    breadcrumb_list = soup.find("ul", {"itemtype": "http://schema.org/BreadcrumbList"})
    if breadcrumb_list:
        breadcrumb_items = breadcrumb_list.find_all("li", {"itemprop": "itemListElement"})
        

        
        # Extrair nomes dos breadcrumbs
        breadcrumb_names = []
        for i, item in enumerate(breadcrumb_items):
            # Primeiro, verificar se tem <strong> (nome do produto)
            strong_tag = item.find("strong")
            if strong_tag:
                name = limpar(strong_tag.get_text())
                breadcrumb_names.append(name)
            else:
                # Buscar o nome dentro do item
                name_span = item.find("span", {"itemprop": "name"})
                if name_span:
                    name = limpar(name_span.get_text())
                    breadcrumb_names.append(name)
                else:
                    # Fallback: buscar em link ou texto direto
                    link = item.find("a")
                    if link:
                        name = limpar(link.get_text())
                        breadcrumb_names.append(name)
                    else:
                        # Texto direto no li
                        text = limpar(item.get_text())
                        if text and text.lower() not in ("você está em:", "you are in:"):
                            breadcrumb_names.append(text)
        
        # Filtrar breadcrumbs válidos (remover "Página Inicial", "Início", etc.)
        breadcrumb_names = [name for name in breadcrumb_names if name and name.lower() not in ("início", "inicio", "home", "página inicial")]
        
        # Atribuir departamento e categoria
        if len(breadcrumb_names) >= 2:
            NomeDepartamento = breadcrumb_names[-2]  # Penúltimo item
            NomeCategoria = breadcrumb_names[-1]     # Último item
        elif len(breadcrumb_names) == 1:
            NomeCategoria = breadcrumb_names[0]
            


    
            # Fallback: breadcrumb genérico se schema.org não encontrado
        if not NomeDepartamento and not NomeCategoria:
            trail = [limpar(a.get_text()) for a in soup.select(
                "nav.breadcrumb a, .breadcrumb a, .breadcrumbs a, a.breadcrumbs-href, .breadcrumb-item a, .breadcrumb-nav a, [class*='breadcrumb'] a"
            )]
            trail = [t for t in trail if t and t.lower() not in ("início", "inicio", "home")]

            nome_h1 = limpar(soup.select_one("div.product-name h1, h1").get_text()) if soup.select_one("div.product-name h1, h1") else ""
            if trail and nome_h1 and trail[-1][:20].lower() in nome_h1[:20].lower():
                trail = trail[:-1]

            # Para Colcci, se encontrou "Roupas" no breadcrumb, usar como departamento
            if trail and "roupas" in trail[-1].lower():
                NomeDepartamento = "Feminino"  # Colcci é focado em moda feminina
                NomeCategoria = "Vestidos"  # Categoria padrão para vestidos
            else:
                NomeDepartamento = trail[-2] if len(trail) >= 2 else ""
                NomeCategoria = trail[-1] if len(trail) >= 1 else ""

    # --- Extrair variações de tamanho (Colcci) ---
    tamanhos_disponiveis = []
    if "colcci.com.br" in url:
        # Procurar por seletores de tamanho na página
        tamanho_selectors = [
            "select[name*='tamanho'] option",
            "select[name*='size'] option", 
            "[class*='tamanho'] option",
            "[class*='size'] option",
            "input[name*='tamanho'][type='radio']",
            "input[name*='size'][type='radio']",
            "[data-tamanho]",
            "[data-size]"
        ]
        
        for selector in tamanho_selectors:
            options = soup.select(selector)
            if options:
                for opt in options:
                    tamanho = opt.get_text(strip=True) or opt.get("value", "")
                    if tamanho and tamanho.lower() not in ("selecione", "select", "tamanho", "size", "-"):
                        tamanhos_disponiveis.append(tamanho)
                break
        
        # Fallback: extrair do texto da página
        if not tamanhos_disponiveis:
            full_text = soup.get_text(" ", strip=True)
            
            # Debug: mostrar trecho do texto onde procurar tamanhos
            tamanho_context = re.search(r"Tamanho[:\s]*[^.]*", full_text, re.I)
            if tamanho_context:
                print(f"🔍 Debug contexto tamanho: {tamanho_context.group(0)}")
            
            # Padrão específico para "PP P M G" (com PP duplicado no texto)
            pp_p_m_g_match = re.search(r"Tamanho[:\s]*PP\s+PP\s+P\s+M\s+G", full_text, re.I)
            if pp_p_m_g_match:
                tamanhos_disponiveis = ["PP", "P", "M", "G"]
                print(f"🔍 Debug: encontrado padrão PP P M G")
            else:
                # Fallback: padrão genérico
                tamanho_match = re.search(r"(?:Tamanho[:\s]*)?((?:PP?|P|M|G|GG?|X?S|X?L|XX?L|\d{2,3})(?:\s+(?:PP?|P|M|G|GG?|X?S|X?L|XX?L|\d{2,3}))*)", full_text, re.I)
                if tamanho_match:
                    tamanhos_str = tamanho_match.group(1)
                    tamanhos_disponiveis = [t.strip() for t in re.split(r'\s+', tamanhos_str) if t.strip()]
                    print(f"🔍 Debug tamanhos encontrados: {tamanhos_disponiveis}")
    
    # Se não encontrou tamanhos, usar tamanho padrão
    if not tamanhos_disponiveis:
        tamanhos_disponiveis = ["ÚNICO"]

    # Fallback: extrair categoria/departamento do nome do produto
    if not NomeDepartamento or not NomeCategoria:
        nome_lower = nome.lower()
        
        # Para Colcci, sempre usar Feminino como departamento padrão
        if "colcci.com.br" in url:
            NomeDepartamento = "Feminino"
        else:
            # Detectar departamento (Feminino/Masculino)
            if any(palavra in nome_lower for palavra in ["feminino", "feminina", "mulher", "mulheres"]):
                NomeDepartamento = "Feminino"
            elif any(palavra in nome_lower for palavra in ["masculino", "masculina", "homem", "homens"]):
                NomeDepartamento = "Masculino"
            else:
                # Tentar detectar pelo tipo de produto
                if any(palavra in nome_lower for palavra in ["vestido", "blusa", "saia", "blazer", "cardigã", "macacão"]):
                    NomeDepartamento = "Feminino"
                elif any(palavra in nome_lower for palavra in ["camisa", "camiseta", "bermuda", "calça", "jaqueta"]):
                    NomeDepartamento = "Masculino"
                else:
                    NomeDepartamento = "Feminino"  # Default para Colcci
        
        # Detectar categoria específica
        if "vestido" in nome_lower:
            NomeCategoria = "Vestidos"
        elif "blusa" in nome_lower:
            NomeCategoria = "Blusas"
        elif "calça" in nome_lower or "calca" in nome_lower:
            NomeCategoria = "Calças"
        elif "saia" in nome_lower:
            NomeCategoria = "Saias"
        elif "blazer" in nome_lower:
            NomeCategoria = "Blazers"
        elif "camiseta" in nome_lower:
            NomeCategoria = "Camisetas"
        elif "camisa" in nome_lower:
            NomeCategoria = "Camisas"
        elif "bermuda" in nome_lower:
            NomeCategoria = "Bermudas"
        elif "jaqueta" in nome_lower:
            NomeCategoria = "Jaquetas"
        elif "regata" in nome_lower:
            NomeCategoria = "Regatas"
        elif "short" in nome_lower:
            NomeCategoria = "Shorts"
        elif "macacão" in nome_lower or "macacao" in nome_lower:
            NomeCategoria = "Macacões"
        elif "top" in nome_lower:
            NomeCategoria = "Tops"
        elif "cardigã" in nome_lower or "cardiga" in nome_lower:
            NomeCategoria = "Cardigãs"
        elif "casaco" in nome_lower:
            NomeCategoria = "Casacos"
        else:
            NomeCategoria = "Vestidos"  # Default para Colcci

    # SKU: reúne candidatos -> escolhe o 1º não vazio
    sku_candidates = []
    if isinstance(jsonld, dict) and jsonld.get("sku"):
        sku_candidates.append(str(jsonld["sku"]))
    if nd:
        try:
            prod_nd = nd["props"]["pageProps"]["product"]
            for key in ("itemId", "sku", "id", "productId"):
                v = prod_nd.get(key)
                if v:
                    sku_candidates.append(str(v))
        except Exception:
            pass
    meta_sku = soup.find("meta", {"itemprop": "sku"})
    if meta_sku and meta_sku.get("content"):
        sku_candidates.append(meta_sku["content"].strip())
    # último recurso: slug
    sku_candidates.append(url.rstrip("/").split("/")[-1])
    # Fallback adicional (Colcci): extrair por rótulo "Ref." ou "Referência"
    try:
        full_txt = soup.get_text(" ", strip=True)
        mref = re.search(r"(?:Ref\.?|Refer[eê]ncia)[:\s]+([A-Z0-9\-\.\/]+)", full_txt, flags=re.I)
        if mref:
            sku_candidates.insert(0, mref.group(1))
    except Exception:
        pass
    sku = next((x for x in sku_candidates if x), "")

    # --- Marca (JSON-LD -> HTML -> Nome do produto) ---
    Marca = ""
    if isinstance(jsonld, dict) and jsonld.get("brand"):
        b = jsonld["brand"]
        if isinstance(b, dict) and b.get("name"): 
            Marca = limpar(b["name"])
        elif isinstance(b, str): 
            Marca = limpar(b)

    if not Marca:
        label = soup.find(string=lambda s: isinstance(s, str) and "Marca" in s)
        if label:
            cont = label.find_parent(["tr","li","p","div","dt","span"])
            if cont:
                dd = cont.find_next_sibling("dd")
                if dd and dd.get_text(strip=True):
                    Marca = limpar(dd.get_text(" ", strip=True))
                else:
                    txt = limpar(cont.get_text(" ", strip=True))
                    m = re.search(r"Marca[:\-]\s*(.+)", txt, flags=re.I)
                    if m: 
                        Marca = limpar(m.group(1))

    # Fallback: extrair marca do nome do produto
    if not Marca:
        nome_lower = nome.lower()
        marcas_conhecidas = [
            "colcci", "colcci jeans", "colcci sport", "colcci beach", 
            "colcci festa", "colcci acessórios", "colcci acessorios"
        ]
        
        for marca in marcas_conhecidas:
            if marca in nome_lower:
                Marca = marca.title()
                break
        
        # Se não encontrou marca específica, usar Colcci como padrão
        if not Marca:
            Marca = "Colcci"

    # --- IDs VTEX via mapeamento local ---
    # Para Colcci, detectar se é produto masculino ou feminino
    if "colcci.com.br" in url:
        nome_lower = nome.lower()
        if any(palavra in nome_lower for palavra in ["masculina", "masculino", "homem", "homens"]):
            NomeDepartamento = "Masculino"
        else:
            NomeDepartamento = "Feminino"
    
    _IDDepartamento = maps["departamento"].get(NomeDepartamento, "")
    _IDCategoria = maps["categoria"].get(NomeCategoria, "")
    _IDMarca = maps["marca"].get(Marca, "")

    # Imagens: se vazio, captura de <img> e <source srcset> (típico em carrosséis)
    if not imgs:
        # <img>
        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src") or parse_srcset(img.get("srcset"))
            if src and "data:image" not in src and "blank" not in src.lower():
                imgs.append(src)
        # <source srcset>
        for source in soup.select("source"):
            srcset = source.get("srcset")
            url_first = parse_srcset(srcset)
            if url_first and "data:image" not in url_first:
                imgs.append(url_first)
    else:
        # Mesmo assim, vamos tentar buscar no HTML para ter mais opções
        html_imgs = []
        # <img>
        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src") or parse_srcset(img.get("srcset"))
            if src and "data:image" not in src and "blank" not in src.lower():
                html_imgs.append(src)
        # <source srcset>
        for source in soup.select("source"):
            srcset = source.get("srcset")
            url_first = parse_srcset(srcset)
            if url_first and "data:image" not in url_first:
                html_imgs.append(url_first)
        
        # Adicionar imagens do HTML se não estiverem na lista
        for img in html_imgs:
            if img not in imgs:
                imgs.append(img)

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

    # Gerar múltiplas linhas para cada tamanho (SKU)
    produtos = []
    for tamanho in tamanhos_disponiveis:
        # SKU único para cada tamanho
        sku_tamanho = f"{sku}_{tamanho}" if tamanho != "ÚNICO" else sku
        nome_tamanho = f"{nome} - {tamanho}" if tamanho != "ÚNICO" else nome
        
        produtos.append({
            "_IDSKU": sku_tamanho,
            "_NomeSKU": nome_tamanho,
            "_AtivarSKUSePossível": "SIM",
            "_SKUAtivo": "SIM",
            "_EANSKU": "",
            "_Altura": "", "_AlturaReal": "",
            "_Largura": "", "_LarguraReal": "",
            "_Comprimento": "", "_ComprimentoReal": "",
            "_Peso": "", "_PesoReal": "",
            "_UnidadeMedida": "un",
            "_MultiplicadorUnidade": "1,000000",
            "_CodigoReferenciaSKU": sku_tamanho,
            "_ValorFidelidade": "",
            "_DataPrevisaoChegada": "",
            "_CodigoFabricante": "",
            "_IDProduto": sku,  # ID do produto é o SKU base (sem tamanho)
            "_NomeProduto": nome,  # Nome do produto sem tamanho
            "_BreveDescricaoProduto": (descricao or "")[:200],
            "_ProdutoAtivo": "SIM",
            "_CodigoReferenciaProduto": sku,  # Referência do produto é o SKU base
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
            "_BaseUrlImagens": base_url_produto,  # URL base para imagens do produto
            "_ImagensSalvas": ";".join(saved),
            "_ImagensURLs": ";".join(imgs),  # útil para POST sku file sem baixar
        })
    
    return produtos

# === Loop principal ===
produtos = []
for _, row in df_links.iterrows():
    url = str(row["url"]).strip()
    if not url:
        continue
    try:
        resultado = extrair_produto(url)
        # resultado pode ser uma lista (múltiplos SKUs) ou um dict (SKU único)
        if isinstance(resultado, list):
            produtos.extend(resultado)
        else:
            produtos.append(resultado)
        time.sleep(0.5)  # cortesia para evitar 429
    except Exception as e:
        print(f"❌ Erro ao processar {url}: {e}")

pd.DataFrame(produtos).to_csv(output_csv, index=False, encoding="utf-8-sig")
print(f"\n✅ Planilha final salva: {output_csv}")
print(f"🖼️ Imagens em: {output_folder}")