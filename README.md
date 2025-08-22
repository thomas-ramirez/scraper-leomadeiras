# VTEX Product Scraper POC

Solução para extração automatizada de produtos de e-commerces e geração de planilhas compatíveis com VTEX.

## 🎯 Objetivo

Automatizar a migração de produtos de diferentes e-commerces para VTEX, extraindo dados como:
- Nome do produto
- Referência/SKU
- Preço
- Descrição e composição
- Categoria/Subcategoria
- Imagens
- Variações (tamanho, cor)

## 🏗️ Arquitetura

```
colccipoc/
├── scraper.py              # Core do scraper
├── docs/                   # Documentação
├── examples/               # Exemplos de uso
├── templates/              # Templates de configuração
├── tests/                  # Testes
├── scripts/                # Scripts auxiliares
├── data/                   # Dados e exports
│   ├── csv/                # Planilhas de entrada
│   └── exports/            # Planilhas geradas
└── requirements.txt        # Dependências
```

## 🚀 Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd colccipoc

# Instale as dependências
pip install -r requirements.txt

# Instale o Playwright (necessário para páginas dinâmicas)
python -m playwright install chromium
```

## 📖 Como Usar

### 1. Preparar Lista de URLs

Crie um arquivo CSV em `~/Downloads/produtos_link.csv`:

```csv
url
https://www.colcci.com.br/produto-1
https://www.colcci.com.br/produto-2
https://www.mercadocar.com.br/produto-3
```

### 2. Executar Scraper

```bash
python scraper.py
```

### 3. Resultado

O scraper gera:
- `data/exports/produtos_vtex.csv`: Planilha pronta para importação VTEX
- `~/Downloads/imagens_produtos/`: Imagens baixadas dos produtos

## 🔧 Configuração

### Mapeamentos VTEX

Edite os mapeamentos em `scraper.py`:

```python
maps = {
    "departamento": {
        "Roupas": "1",
        "Acessórios": "2",
        # Adicione mais conforme necessário
    },
    "categoria": {
        "Blusas": "1",
        "Calças": "2",
        # Adicione mais conforme necessário
    },
    "marca": {
        "Colcci": "1",
        "Marca X": "2",
        # Adicione mais conforme necessário
    }
}
```

## 🛠️ Extendendo para Novas Lojas

### 1. Identificar Tipo de Página

O scraper detecta automaticamente:
- **Páginas estáticas**: Usa `requests` + BeautifulSoup
- **Páginas dinâmicas** (Colcci): Usa Playwright para renderização

### 2. Adicionar Suporte a Nova Loja

#### Para Páginas Estáticas (como MercadoCar):

```python
# O scraper já suporta automaticamente via:
# - JSON-LD (application/ld+json)
# - __NEXT_DATA__ (Next.js)
# - Seletores HTML genéricos
```

#### Para Páginas Dinâmicas (como Colcci):

1. Adicione condição no `extrair_produto()`:

```python
if "sua-loja.com.br" in url:
    # Usar Playwright para renderização
    html = renderizar_html(url, wait_selectors=[...])
```

2. Implemente seletores específicos:

```python
# Exemplo: extrair tamanhos específicos da loja
if "sua-loja.com.br" in url:
    tamanho_selectors = [
        "select[name*='tamanho'] option",
        "[data-size]",
        # Adicione seletores específicos da loja
    ]
```

### 3. Testar Nova Implementação

```bash
# Teste com uma URL da nova loja
python -c "
from scraper import extrair_produto
result = extrair_produto('https://sua-loja.com.br/produto')
print(result)
"
```

## 📊 Estrutura da Planilha VTEX

A planilha gerada contém:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `_IDSKU` | SKU único do produto | `360125377_PP` |
| `_NomeSKU` | Nome do SKU | `Blusa Comfort - PP` |
| `_NomeProduto` | Nome do produto | `Blusa Comfort Em Crochê` |
| `_Preço` | Preço do produto | `429.00` |
| `_DescricaoProduto` | Descrição completa | `Composição 96% POLIAMIDA...` |
| `_NomeCategoria` | Categoria | `Blusas` |
| `_ImagensURLs` | URLs das imagens | `url1;url2;url3` |

## 🔄 Fluxo de Trabalho

1. **Análise**: Identificar estrutura da loja (estática/dinâmica)
2. **Configuração**: Ajustar mapeamentos VTEX
3. **Extração**: Executar scraper
4. **Validação**: Verificar dados extraídos
5. **Importação**: Usar planilha no VTEX

## 🧪 Testes

```bash
# Teste básico
python tests/test_scraper.py

# Teste com dados de exemplo
python examples/test_colcci.py
```

## 📝 Logs e Debug

O scraper fornece logs detalhados:

```
🔍 Debug: encontrado padrão PP P M G
✅ Planilha final salva: data/exports/produtos_vtex.csv
🖼️ Imagens em: ~/Downloads/imagens_produtos
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente suporte à nova loja
4. Adicione testes
5. Documente a implementação
6. Abra um Pull Request

## 📋 Checklist para Nova Loja

- [ ] Identificar tipo de página (estática/dinâmica)
- [ ] Implementar seletores específicos
- [ ] Testar extração de dados
- [ ] Validar estrutura VTEX
- [ ] Documentar implementação
- [ ] Adicionar testes

## 🚨 Limitações

- Algumas imagens podem retornar 404 (URLs mantidas em `_ImagensURLs`)
- Breadcrumbs podem ser limitados em algumas PDPs
- Requer Playwright para páginas dinâmicas

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação em `docs/`
2. Consulte os exemplos em `examples/`
3. Abra uma issue no GitHub

---

**Desenvolvido para facilitar migrações VTEX por Solutions Engineers**
