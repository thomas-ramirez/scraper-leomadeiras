# Estrutura Técnica - VTEX Product Scraper

## 🏗️ Arquitetura Geral

O scraper foi projetado para ser **modular** e **extensível**, permitindo que Solutions Engineers adicionem suporte a novas lojas facilmente.

### Componentes Principais

```
scraper.py
├── Configuração (maps, UA, paths)
├── Utilitários (limpar, parse_preco, etc.)
├── Renderização (Playwright para páginas dinâmicas)
├── Extração (extrair_produto)
└── Loop Principal (processamento em lote)
```

## 🔧 Detalhamento dos Componentes

### 1. Configuração e Setup

```python
# Mapeamentos VTEX
maps = {
    "departamento": {...},
    "categoria": {...},
    "marca": {...}
}

# User Agent e sessão HTTP
UA = {...}
session = requests.Session()
```

### 2. Sistema de Renderização

#### Páginas Estáticas
- **Tecnologia**: `requests` + `BeautifulSoup`
- **Uso**: Para lojas que entregam HTML completo no servidor
- **Exemplo**: MercadoCar, maioria dos e-commerces

#### Páginas Dinâmicas
- **Tecnologia**: `Playwright` (Chromium headless)
- **Uso**: Para lojas que renderizam conteúdo via JavaScript
- **Exemplo**: Colcci, lojas SPA/React

```python
def renderizar_html(url, wait_selectors=None, timeout_ms=15000):
    """Renderiza página via Chromium headless"""
    # Aguarda seletores específicos
    # Retorna HTML renderizado
```

### 3. Pipeline de Extração

#### Fluxo de Dados
```
URL → Renderização → BeautifulSoup → Extração → VTEX CSV
```

#### Estratégias de Extração (em ordem de prioridade)

1. **JSON-LD** (`application/ld+json`)
   - Padrão web semântico
   - Dados estruturados confiáveis
   - Prioridade máxima

2. **__NEXT_DATA__** (Next.js)
   - Dados internos de aplicações Next.js
   - Informações completas do produto

3. **HTML Fallbacks**
   - Seletores CSS genéricos
   - Regex para preços, referências
   - Breadcrumbs para categorias

4. **Seletores Específicos por Loja**
   - Implementação customizada
   - Exemplo: Colcci (tamanhos, composição)

### 4. Detecção de Variações

#### Sistema de Tamanhos
```python
# Seletores genéricos
tamanho_selectors = [
    "select[name*='tamanho'] option",
    "select[name*='size'] option",
    "[data-tamanho]",
    "[data-size]"
]

# Regex para padrões específicos
r"Tamanho[:\s]*PP\s+PP\s+P\s+M\s+G"
```

#### Geração de SKUs
```python
# Para cada tamanho encontrado
sku_tamanho = f"{sku}_{tamanho}"  # 360125377_PP
nome_tamanho = f"{nome} - {tamanho}"  # Blusa - PP
```

## 🛠️ Como Estender para Nova Loja

### Passo 1: Análise da Estrutura

#### Verificar Tipo de Página
```bash
# Teste rápido
curl -s "https://loja.com/produto" | grep -E "(__NEXT_DATA__|application/ld\+json)"
```

#### Identificar Padrões
- **JSON-LD**: `<script type="application/ld+json">`
- **Next.js**: `<script id="__NEXT_DATA__">`
- **Dinâmico**: Scripts `wd-*`, `browsingContext`

### Passo 2: Implementação

#### Para Páginas Estáticas
```python
# O scraper já suporta automaticamente
# Apenas ajuste os mapeamentos VTEX se necessário
```

#### Para Páginas Dinâmicas
```python
# 1. Adicionar condição de renderização
if "sua-loja.com.br" in url:
    html = renderizar_html(url, wait_selectors=[
        "h1", "[class*='price']", "[class*='tamanho']"
    ])

# 2. Implementar seletores específicos
if "sua-loja.com.br" in url:
    # Seletores de tamanho específicos
    tamanho_selectors = [
        "select[name*='tamanho'] option",
        "[data-size]",
        # Adicione seletores da loja
    ]
    
    # Seletores de composição específicos
    composicao_selectors = [
        "[class*='composicao']",
        "[class*='composition']",
        # Adicione seletores da loja
    ]
```

### Passo 3: Teste e Validação

```python
# Teste unitário
def test_nova_loja():
    url = "https://sua-loja.com.br/produto"
    resultado = extrair_produto(url)
    
    assert resultado[0]["_NomeProduto"] != ""
    assert resultado[0]["_Preço"] != ""
    assert len(resultado) > 0  # Múltiplos SKUs se houver
```

## 📊 Estrutura de Dados VTEX

### Campos Obrigatórios
- `_IDSKU`: Identificador único do SKU
- `_NomeProduto`: Nome do produto
- `_Preço`: Preço do produto
- `_IDProduto`: ID do produto (mesmo para todos os SKUs)

### Campos Importantes
- `_DescricaoProduto`: Descrição completa
- `_NomeCategoria`: Categoria do produto
- `_ImagensURLs`: URLs das imagens
- `_CodigoReferenciaProduto`: Referência do produto

### Relacionamentos
```
Produto (ID: 360125377)
├── SKU PP (ID: 360125377_PP)
├── SKU P  (ID: 360125377_P)
├── SKU M  (ID: 360125377_M)
└── SKU G  (ID: 360125377_G)
```

## 🔍 Debug e Troubleshooting

### Logs Disponíveis
```python
# Debug de tamanhos
print(f"🔍 Debug tamanhos encontrados: {tamanhos_disponiveis}")

# Debug de contexto
print(f"🔍 Debug contexto tamanho: {tamanho_context.group(0)}")

# Erros de imagem
print(f"⚠️ Erro ao baixar imagem {url_img}: {e}")
```

### Problemas Comuns

#### 1. Tamanhos Não Detectados
```python
# Verificar regex
tamanho_match = re.search(r"Tamanho[:\s]*PP\s+PP\s+P\s+M\s+G", full_text, re.I)
```

#### 2. Imagens 404
```python
# URLs mantidas em _ImagensURLs para uso alternativo
# Tentar trocar extensão: .webp → .jpg
```

#### 3. Breadcrumb Limitado
```python
# Implementar fallback por nome do produto
# Ou interceptar XHR para dados completos
```

## 🚀 Otimizações Futuras

### 1. Interceptação de XHR
```python
# Capturar endpoints JSON em tempo real
page.on("response", lambda response: 
    if "product" in response.url: 
        dados = response.json()
)
```

### 2. Cache de Dados
```python
# Evitar re-scraping de produtos já processados
cache_file = "cache_produtos.json"
```

### 3. Paralelização
```python
# Processar múltiplas URLs simultaneamente
from concurrent.futures import ThreadPoolExecutor
```

### 4. Validação de Dados
```python
# Validar estrutura antes de gerar CSV
def validar_produto(produto):
    campos_obrigatorios = ["_NomeProduto", "_Preço", "_IDSKU"]
    return all(produto.get(campo) for campo in campos_obrigatorios)
```

## 📋 Checklist de Implementação

### Para Nova Loja
- [ ] Identificar tipo de página (estática/dinâmica)
- [ ] Implementar seletores específicos
- [ ] Testar extração de dados básicos
- [ ] Implementar detecção de variações
- [ ] Validar estrutura VTEX
- [ ] Adicionar logs de debug
- [ ] Documentar implementação
- [ ] Criar testes

### Para Otimização
- [ ] Implementar cache
- [ ] Adicionar validação
- [ ] Otimizar performance
- [ ] Melhorar tratamento de erros
- [ ] Adicionar métricas

---

**Esta documentação deve ser atualizada conforme o projeto evolui**
