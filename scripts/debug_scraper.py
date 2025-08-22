import requests
from bs4 import BeautifulSoup
import json
import re

def limpar(t):
    return re.sub(r"\s+", " ", (t or "").strip())

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

# Teste com uma URL específica
url = "https://www.mercadocar.com.br/pneu-235x50-r20-104w-xl-lr1-pirelli-pneus-3385500"

print(f"🔍 Testando URL: {url}")
print("=" * 80)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

r = requests.get(url, headers=headers, timeout=15)
print(f"Status Code: {r.status_code}")
print(f"Content Length: {len(r.content)}")
print(f"First 500 chars: {r.text[:500]}")

soup = BeautifulSoup(r.content, "html.parser")

# JSON-LD
jsonld = get_jsonld(soup) or {}
print(f"📋 JSON-LD encontrado: {bool(jsonld)}")
if jsonld:
    print(f"   Brand: {jsonld.get('brand')}")

# __NEXT_DATA__
print("\n📦 __NEXT_DATA__:")
next_data_script = soup.find("script", id="__NEXT_DATA__")
if next_data_script:
    try:
        next_data = json.loads(next_data_script.string)
        print(f"   Encontrado: Sim")
        # Procurar por breadcrumb no next_data
        if "props" in next_data and "pageProps" in next_data["props"]:
            page_props = next_data["props"]["pageProps"]
            print(f"   PageProps keys: {list(page_props.keys())}")
            if "product" in page_props:
                product = page_props["product"]
                print(f"   Product keys: {list(product.keys())}")
                if "breadcrumb" in product:
                    print(f"   Breadcrumb: {product['breadcrumb']}")
                if "category" in product:
                    print(f"   Category: {product['category']}")
                if "brand" in product:
                    print(f"   Brand: {product['brand']}")
    except Exception as e:
        print(f"   Erro ao parsear: {e}")
else:
    print("   Não encontrado")

# Outros scripts com dados
print("\n📜 OUTROS SCRIPTS:")
scripts = soup.find_all("script")
for script in scripts:
    if script.string and ("breadcrumb" in script.string.lower() or "category" in script.string.lower()):
        print(f"   Script com dados: {script.string[:200]}...")

# Breadcrumb
print("\n🍞 BREADCRUMB:")
bc = soup.select("nav.breadcrumb a, .breadcrumb a, .breadcrumbs a, a.breadcrumbs-href, .breadcrumb-item a, .breadcrumb-nav a, [class*='breadcrumb'] a")
print(f"   Seletores encontrados: {len(bc)}")
for i, a in enumerate(bc):
    print(f"   {i+1}. '{a.get_text(strip=True)}'")

# Procurar por outros elementos de navegação
print("\n🔍 OUTROS ELEMENTOS DE NAVEGAÇÃO:")
nav_elements = soup.find_all(["nav", "ol", "ul"], class_=lambda x: x and "breadcrumb" in x.lower() if x else False)
for nav in nav_elements:
    print(f"   {nav.name}.{nav.get('class', [])}: {nav.get_text(strip=True)[:100]}")

# Procurar por links que possam ser breadcrumb
print("\n🔗 LINKS POSSÍVEIS:")
links = soup.find_all("a", href=True)
for link in links[:10]:  # Primeiros 10 links
    href = link.get("href", "")
    text = link.get_text(strip=True)
    if any(word in href.lower() for word in ["categoria", "departamento", "pneu", "oleo", "filtro"]):
        print(f"   '{text}' -> {href}")

# Processamento do breadcrumb
trail = [limpar(a.get_text()) for a in soup.select(
    "nav.breadcrumb a, .breadcrumb a, .breadcrumbs a, a.breadcrumbs-href"
)]
print(f"\n   Trail original: {trail}")

trail = [t for t in trail if t and t.lower() not in ("início", "inicio", "home")]
print(f"   Trail filtrado: {trail}")

nome_h1 = limpar(soup.select_one("div.product-name h1, h1").get_text()) if soup.select_one("div.product-name h1, h1") else ""
print(f"   Nome H1: '{nome_h1}'")

if trail and nome_h1 and trail[-1][:20].lower() in nome_h1[:20].lower():
    trail = trail[:-1]
    print(f"   Trail após remoção do último: {trail}")

NomeDepartamento = trail[-2] if len(trail) >= 2 else ""
NomeCategoria = trail[-1] if len(trail) >= 1 else ""
print(f"\n   📁 Departamento: '{NomeDepartamento}'")
print(f"   📂 Categoria: '{NomeCategoria}'")

# Marca
print("\n🏷️ MARCA:")
Marca = ""
if isinstance(jsonld, dict) and jsonld.get("brand"):
    b = jsonld["brand"]
    if isinstance(b, dict) and b.get("name"): 
        Marca = limpar(b["name"])
        print(f"   JSON-LD brand.name: '{Marca}'")
    elif isinstance(b, str): 
        Marca = limpar(b)
        print(f"   JSON-LD brand (string): '{Marca}'")

if not Marca:
    print("   Tentando extrair do HTML...")
    label = soup.find(string=lambda s: isinstance(s, str) and "Marca" in s)
    if label:
        print(f"   Label encontrado: '{label}'")
        cont = label.find_parent(["tr","li","p","div","dt","span"])
        if cont:
            print(f"   Container encontrado: {cont.name}")
            dd = cont.find_next_sibling("dd")
            if dd and dd.get_text(strip=True):
                Marca = limpar(dd.get_text(" ", strip=True))
                print(f"   Marca extraída (dd): '{Marca}'")
            else:
                txt = limpar(cont.get_text(" ", strip=True))
                print(f"   Texto do container: '{txt}'")
                m = re.search(r"Marca[:\-]\s*(.+)", txt, flags=re.I)
                if m: 
                    Marca = limpar(m.group(1))
                    print(f"   Marca extraída (regex): '{Marca}'")
    else:
        print("   Nenhum label 'Marca' encontrado no HTML")

print(f"\n🎯 RESULTADO FINAL:")
print(f"   Departamento: '{NomeDepartamento}'")
print(f"   Categoria: '{NomeCategoria}'")
print(f"   Marca: '{Marca}'")
