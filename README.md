# 🛠️ Scraper Leo Madeiras

**Web scraper especializado para extrair dados de produtos da [Leo Madeiras](https://www.leomadeiras.com.br/)**

## 📋 Descrição

Este scraper foi desenvolvido especificamente para extrair informações de produtos da Leo Madeiras, uma das principais lojas de ferramentas e materiais de construção do Brasil. O sistema utiliza técnicas avançadas de web scraping para capturar dados completos dos produtos, incluindo preços, descrições, imagens e especificações técnicas.

## ✨ Funcionalidades

- 🔍 **Extração Inteligente de Preços**: Captura preços dinâmicos carregados via JavaScript
- 📊 **Dados Completos**: Nome, descrição, categoria, departamento, marca e especificações
- 🖼️ **Download de Imagens**: Baixa automaticamente as imagens dos produtos
- 🎯 **Foco na Leo Madeiras**: Otimizado especificamente para o site da Leo Madeiras
- 📈 **Formato VTEX**: Gera CSV compatível com sistemas VTEX
- 🚀 **Renderização JavaScript**: Usa Playwright para páginas dinâmicas

## 🎯 Produtos Suportados

### Departamentos
- **MDF** e **Madeiras**
- **Ferramentas Elétricas** (Furadeiras, Parafusadeiras, Serras)
- **Ferramentas Manuais**
- **Máquinas Estacionárias**
- **Ferragens** e **Acessórios**
- **Químicos** e **Revestimentos**
- **EPI** e **Construção**

### Marcas Principais
- **Kress** - Ferramentas elétricas profissionais
- **Bosch** - Ferramentas de alta qualidade
- **Makita** - Ferramentas profissionais
- **Dewalt** - Ferramentas robustas
- **Milwaukee** - Ferramentas industriais

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes Python)

### Passos de Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/thomas-ramirez/scraper-leomadeiras.git
cd scraper-leomadeiras
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Instale o Playwright (para renderização JavaScript):**
```bash
python -m playwright install chromium
```

## 📖 Como Usar

### 1. Configurar URLs dos Produtos

Edite o arquivo `data/csv/produtos_link.csv` e adicione as URLs dos produtos da Leo Madeiras:

```csv
url
https://www.leomadeiras.com.br/p/10525549/furadeira-parafusadeira-de-impacto-a-bateria-12v-kuc11-bivolt-kress
https://www.leomadeiras.com.br/p/outro-produto
```

### 2. Executar o Scraper

```bash
python scraper.py
```

### 3. Resultados

O scraper irá:
- ✅ Processar cada URL da lista
- ✅ Extrair dados completos dos produtos
- ✅ Baixar imagens para `data/exports/imagens_produtos/`
- ✅ Gerar CSV em `data/exports/produtos_leo_madeiras.csv`

## 🔧 Como Funciona

### Extração de Preços (Prioridade)

1. **`data-price`**: Atributo HTML com preço direto
2. **`data-sku-obj`**: JSON com dados do produto (incluindo preço)
3. **Templates Handlebars**: Padrões de preço em templates
4. **Elementos HTML**: Classes `.price`, `.product-price`
5. **JSON-LD**: Dados estruturados da página
6. **Regex**: Busca por padrões de preço no texto

### Exemplo de Funcionamento

```python
# O scraper encontra este atributo na página:
<div data-price="749.90">R$ 749,90</div>

# E extrai o preço:
✅ Preço encontrado via data-price: 749.90
💰 Preço final extraído: R$ 749.90
```

## 📊 Estrutura do CSV Gerado

O arquivo `produtos_leo_madeiras.csv` contém:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `_IDSKU` | Código único do produto | `10525549` |
| `_NomeSKU` | Nome completo do produto | `Furadeira Parafusadeira...` |
| `_Preço` | Preço do produto | `749.90` |
| `_IDDepartamento` | ID do departamento VTEX | `3` |
| `_NomeDepartamento` | Nome do departamento | `Ferramentas Elétricas` |
| `_IDCategoria` | ID da categoria VTEX | `4` |
| `_NomeCategoria` | Nome da categoria | `Parafusadeira` |
| `_Marca` | Marca do produto | `Kress` |
| `_ImagensSalvas` | Arquivos de imagem baixados | `10525549_1.jpg;10525549_2.jpg` |
| `_ImagensURLs` | URLs das imagens originais | `https://images.cws.digital/...` |

## 🎨 Personalização

### Adicionar Novas Categorias

Edite o arquivo `scraper.py` na seção de mapeamentos:

```python
maps = {
    "departamento": {
        "Nova Categoria": "20",
        # ... outras categorias
    },
    "categoria": {
        "Nova Subcategoria": "20",
        # ... outras subcategorias
    }
}
```

### Adicionar Novas Marcas

O sistema detecta automaticamente marcas baseado no nome do produto, mas você pode personalizar:

```python
marcas_conhecidas = [
    "kress", "bosch", "makita", "dewalt", "milwaukee",
    "sua-marca-aqui"  # Adicione novas marcas
]
```

## 🐛 Solução de Problemas

### Erro: "Playwright não está disponível"
```bash
pip install playwright
python -m playwright install chromium
```

### Erro: "Nenhum preço encontrado"
- Verifique se a URL é da Leo Madeiras
- A página pode estar com JavaScript desabilitado
- Tente executar novamente

### Imagens não baixam
- Verifique a conexão com a internet
- As URLs podem ter expirado
- Verifique permissões da pasta `data/exports/imagens_produtos/`

## 📁 Estrutura do Projeto

```
scraper-leomadeiras/
├── scraper.py              # Script principal
├── requirements.txt         # Dependências Python
├── README.md               # Esta documentação
├── data/
│   ├── csv/
│   │   └── produtos_link.csv    # URLs dos produtos
│   └── exports/
│       ├── produtos_leo_madeiras.csv    # Resultado final
│       └── imagens_produtos/    # Imagens baixadas
├── scripts/                # Scripts auxiliares
└── templates/              # Templates de exemplo
```

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

- **Leo Madeiras** - Pela disponibilização dos produtos
- **Playwright** - Pela ferramenta de automação web
- **BeautifulSoup** - Pelo parser HTML robusto
- **Pandas** - Pela manipulação de dados

## 📞 Suporte

Se você encontrar algum problema ou tiver dúvidas:

1. **Issues**: Abra uma issue no GitHub
2. **Documentação**: Verifique esta documentação
3. **Exemplos**: Analise os arquivos de exemplo

---

**Desenvolvido com ❤️ para facilitar a extração de dados da Leo Madeiras**

*Última atualização: Setembro 2025*
