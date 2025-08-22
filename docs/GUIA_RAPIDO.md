# Guia Rápido - VTEX Product Scraper

## 🚀 Começando em 5 Minutos

### 1. Setup Inicial
```bash
# Clone e instale
git clone <repository-url>
cd colccipoc
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. Teste Rápido
```bash
# Teste com Colcci
python examples/test_colcci.py
```

### 3. Uso Básico
```bash
# 1. Crie a planilha de links
cp templates/produtos_link_example.csv ~/Downloads/produtos_link.csv

# 2. Edite com suas URLs
# 3. Execute o scraper
python scraper.py

# 4. Resultado em data/exports/produtos_vtex.csv
```

## 🛠️ Adicionando Nova Loja

### Passo 1: Análise (2 min)
```bash
# Teste se é página estática ou dinâmica
curl -s "https://loja.com/produto" | grep -E "(__NEXT_DATA__|application/ld\+json)"
```

### Passo 2: Implementação (5 min)

#### Para Páginas Estáticas
```python
# O scraper já funciona automaticamente!
# Apenas ajuste os mapeamentos VTEX se necessário
```

#### Para Páginas Dinâmicas
```python
# Adicione no scraper.py:
if "sua-loja.com.br" in url:
    html = renderizar_html(url, wait_selectors=[
        "h1", "[class*='price']", "[class*='tamanho']"
    ])
```

### Passo 3: Teste (1 min)
```python
# Teste rápido
from scraper import extrair_produto
result = extrair_produto("https://sua-loja.com.br/produto")
print(f"SKUs encontrados: {len(result)}")
```

## 📊 Estrutura VTEX

### Campos Essenciais
- `_IDSKU`: SKU único (ex: `360125377_PP`)
- `_NomeProduto`: Nome do produto
- `_Preço`: Preço (ex: `429.00`)
- `_IDProduto`: ID do produto (mesmo para todos SKUs)

### Relacionamento
```
Produto (ID: 360125377)
├── SKU PP (ID: 360125377_PP)
├── SKU P  (ID: 360125377_P)
├── SKU M  (ID: 360125377_M)
└── SKU G  (ID: 360125377_G)
```

## 🔧 Configuração VTEX

### Mapeamentos
```python
# Em scraper.py, ajuste:
maps = {
    "departamento": {
        "Roupas": "1",
        "Acessórios": "2",
    },
    "categoria": {
        "Blusas": "1",
        "Calças": "2",
    },
    "marca": {
        "Colcci": "1",
        "Sua Marca": "2",
    }
}
```

## 🧪 Debug

### Logs Úteis
```
🔍 Debug: encontrado padrão PP P M G
✅ Planilha final salva: data/exports/produtos_vtex.csv
⚠️ Erro ao baixar imagem: 404
```

### Problemas Comuns

#### Tamanhos não detectados
```python
# Verifique o regex no scraper.py
r"Tamanho[:\s]*PP\s+PP\s+P\s+M\s+G"
```

#### Imagens 404
```python
# URLs mantidas em _ImagensURLs
# Use para upload VTEX alternativo
```

## 📋 Checklist Nova Loja

- [ ] Teste se é estática ou dinâmica
- [ ] Implemente seletores específicos (se necessário)
- [ ] Teste extração básica
- [ ] Valide estrutura VTEX
- [ ] Documente implementação

## 🚀 Próximos Passos

1. **Teste com sua loja**
2. **Ajuste mapeamentos VTEX**
3. **Execute em lote**
4. **Importe no VTEX**

## 📁 Estrutura do Projeto

```
colccipoc/
├── scraper.py              # Core do scraper
├── data/
│   ├── csv/                # Planilhas de entrada
│   └── exports/            # Planilhas geradas
├── scripts/                # Scripts auxiliares
├── docs/                   # Documentação
├── examples/               # Exemplos
└── templates/              # Templates
```

---

**Precisa de ajuda? Consulte a documentação completa em `docs/`**
