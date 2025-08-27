# 🏪 Scraper Koerich

Um scraper inteligente para capturar produtos da [Koerich](https://www.koerich.com.br), especializado em eletrodomésticos com extração de imagens em alta qualidade.

## ✨ Características

- 🎯 **Foco em Eletrodomésticos**: Otimizado para produtos da Koerich
- 📸 **Imagens em Alta Qualidade**: Captura imagens originais sem redimensionamento
- 🤖 **Suporte a JavaScript**: Usa Playwright para conteúdo dinâmico
- 📊 **Exportação VTEX**: Formato compatível com plataformas e-commerce
- 🔍 **Detecção Inteligente**: Categorização automática de produtos
- 🏷️ **Mapeamento VTEX**: IDs específicos para departamentos, categorias e marcas

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/thomas-ramirez/scraper-koerich.git
cd scraper-koerich

# Instale as dependências
pip install -r requirements.txt

# Instale o Playwright (opcional, para conteúdo dinâmico)
playwright install chromium
```

## 📋 Dependências

- `requests>=2.31.0` - Requisições HTTP
- `beautifulsoup4>=4.12.0` - Parseamento HTML
- `pandas>=2.0.0` - Manipulação de dados
- `lxml>=4.9.0` - Parser XML/HTML
- `playwright>=1.40.0` - Automação de navegador
- `urllib3>=2.0.0` - Cliente HTTP
- `PyGithub>=2.0.0` - API do GitHub

## 🎯 Como Usar

### 1. Preparar URLs dos Produtos

Crie um arquivo CSV em `data/csv/produtos_link.csv` com as URLs dos produtos:

```csv
url
https://www.koerich.com.br/p/frigobar-midea-45-litros-mrc06b2-branco/4043300
https://www.koerich.com.br/p/freezer-horizontal-midea-295-litros-rcfa32-branco/4155100
```

### 2. Executar o Scraper

```bash
python3 scraper.py
```

### 3. Resultados

Os resultados serão salvos em:
- **CSV**: `data/exports/produtos_vtex.csv`
- **Imagens**: `data/exports/imagens_produtos/`

## 📊 Estrutura de Dados

### Mapeamentos VTEX

#### Departamentos
- `Eletrodomésticos` (ID: 1)
- `Eletroportáteis` (ID: 2)
- `Ar Condicionado` (ID: 3)
- `Aquecimento` (ID: 4)
- `Ventilação` (ID: 5)
- `Refrigeração` (ID: 6)
- `Lavagem` (ID: 7)
- `Cozinha` (ID: 8)
- `Limpeza` (ID: 9)
- `Pequenos Eletrodomésticos` (ID: 10)

#### Categorias
- `Frigobar` (ID: 1)
- `Freezer` (ID: 2)
- `Refrigerador` (ID: 3)
- `Ar Condicionado` (ID: 4)
- `Ventilador` (ID: 5)
- `Aquecedor` (ID: 6)
- `Máquina de Lavar` (ID: 7)
- `Secadora` (ID: 8)
- `Fogão` (ID: 9)
- `Microondas` (ID: 10)
- `Liquidificador` (ID: 11)
- `Mixer` (ID: 12)
- `Processador` (ID: 13)
- `Aspirador` (ID: 14)
- `Ferro de Passar` (ID: 15)

#### Marcas
- `Midea` (ID: 1)
- `Electrolux` (ID: 2)
- `Brastemp` (ID: 3)
- `Consul` (ID: 4)
- `Panasonic` (ID: 5)
- `Samsung` (ID: 6)
- `LG` (ID: 7)
- `Philco` (ID: 8)
- `GE` (ID: 9)
- `Whirlpool` (ID: 10)

## 🔧 Funcionalidades Avançadas

### Detecção Automática de Produtos

O scraper detecta automaticamente:
- **Departamento**: Baseado no tipo de produto (frigobar → Refrigeração)
- **Categoria**: Específica do eletrodoméstico
- **Marca**: Detectada no nome do produto
- **Preço**: Extraído da página
- **Descrição**: Seções "Sobre o Produto" e "Especificações"

### Captura de Imagens em Alta Qualidade

- ✅ Remove parâmetros de redimensionamento
- ✅ Parseia srcset para maior resolução
- ✅ Extrai URLs originais da API da Koerich
- ✅ Verifica qualidade antes do download
- ✅ Suporte a múltiplos formatos (JPG, PNG, WebP)

### Exemplo de Resultado

```csv
_IDSKU,_NomeSKU,_Preço,_IDDepartamento,_NomeDepartamento,_IDCategoria,_NomeCategoria,_IDMarca,_Marca
4155100,Freezer Horizontal Midea 295 Litros RCFA32 - Branco,2299.00,6,Refrigeração,2,Freezer,1,MIDEA
```

## 📁 Estrutura do Projeto

```
scraper-koerich/
├── scraper.py              # Script principal
├── requirements.txt        # Dependências
├── README.md              # Documentação
├── data/
│   ├── csv/
│   │   └── produtos_link.csv    # URLs dos produtos
│   └── exports/
│       ├── produtos_vtex.csv    # Resultados
│       └── imagens_produtos/    # Imagens baixadas
├── scripts/
│   ├── scrape_koerich_page.py   # Scraper específico
│   └── scrape_koerich_playwright.py  # Versão com Playwright
├── docs/
│   ├── ESTRUTURA_TECNICA.md     # Documentação técnica
│   └── GUIA_RAPIDO.md           # Guia rápido
└── templates/
    └── produtos_link_example.csv # Exemplo de CSV
```

## 🛠️ Scripts Disponíveis

### `scraper.py` (Principal)
- Scraper completo com todas as funcionalidades
- Suporte a múltiplos produtos
- Exportação VTEX

### `scripts/scrape_koerich_page.py`
- Scraper específico para uma página
- Salva HTML da página
- Análise de conteúdo

### `scripts/scrape_koerich_playwright.py`
- Versão com Playwright para conteúdo dinâmico
- Renderização JavaScript
- Captura de conteúdo assíncrono

## 🔍 Exemplo de Uso

```python
# Executar scraper completo
python3 scraper.py

# Executar scraper específico
python3 scripts/scrape_koerich_page.py

# Executar com Playwright
python3 scripts/scrape_koerich_playwright.py
```

## 📈 Melhorias Implementadas

### Qualidade de Imagens
- **Antes**: 744B - 21KB (thumbnails)
- **Depois**: 32KB - 54KB (alta qualidade)

### URLs de Imagens
- **Antes**: `https://...&width=95&height=95`
- **Depois**: `https://.../products/4155100.01.jpg`

### Detecção Inteligente
- Categorização automática por tipo de produto
- Detecção de marca no nome
- Extração de especificações técnicas

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Thomas Ramirez**
- GitHub: [@thomas-ramirez](https://github.com/thomas-ramirez)
- Projeto: [scraper-koerich](https://github.com/thomas-ramirez/scraper-koerich)

## 🙏 Agradecimentos

- [Koerich](https://www.koerich.com.br) - Fornecedor dos produtos
- [Playwright](https://playwright.dev) - Automação de navegador
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - Parseamento HTML
- [Pandas](https://pandas.pydata.org) - Manipulação de dados

---

⭐ **Se este projeto te ajudou, considere dar uma estrela!**
