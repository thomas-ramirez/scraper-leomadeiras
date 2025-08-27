# Scripts do Projeto Koerich

Este diretório contém os scripts essenciais para o funcionamento do scraper Koerich.

## 📁 Scripts Disponíveis

### 🚀 `scraper_sem_imagens.py`
**Script principal para atualizar o CSV de produtos**

- **Função**: Extrai dados dos produtos do Koerich sem baixar imagens
- **Entrada**: `data/csv/produtos_link.csv` (URLs dos produtos)
- **Saída**: `data/exports/produtos_vtex.csv` (CSV formatado para VTEX)
- **Recursos**:
  - Barra de progresso em tempo real
  - Extração correta de departamento e categoria
  - Renderização com Playwright para conteúdo dinâmico
  - Mapeamento automático de IDs

**Uso:**
```bash
python3 scripts/scraper_sem_imagens.py
```

### 📊 `generate_image_csv_updated.py`
**Gera CSV de imagens com mapeamento de SKUIDs**

- **Função**: Cria CSV com URLs das imagens para VTEX
- **Entrada**: Pasta `data/exports/imagens_produtos/`
- **Saída**: `data/exports/imagens_koerich.csv`
- **Recursos**:
  - Mapeamento de SKUIDs com letras para números
  - URLs do GitHub para as imagens
  - Formato compatível com VTEX

**Uso:**
```bash
python3 scripts/generate_image_csv_updated.py
```

### 📤 `upload_images_git.py`
**Upload de imagens via Git (Recomendado)**

- **Função**: Envia imagens para o repositório GitHub
- **Entrada**: Pasta `data/exports/imagens_produtos/`
- **Destino**: `https://github.com/thomas-ramirez/imagens-koerich`
- **Recursos**:
  - Upload via comandos Git
  - Não requer token de API
  - Mais simples e confiável

**Uso:**
```bash
python3 scripts/upload_images_git.py
```

### 🔑 `upload_images_to_github.py`
**Upload de imagens via API GitHub (Alternativo)**

- **Função**: Envia imagens usando a API do GitHub
- **Entrada**: Pasta `data/exports/imagens_produtos/`
- **Destino**: `https://github.com/thomas-ramirez/imagens-koerich`
- **Requisitos**:
  - Token de acesso GitHub
  - Configuração de autenticação
- **Recursos**:
  - Upload via API oficial
  - Mais controle sobre o processo

**Uso:**
```bash
python3 scripts/upload_images_to_github.py
```

## 🔄 Fluxo de Trabalho

### 1. Atualizar Produtos
```bash
python3 scripts/scraper_sem_imagens.py
```

### 2. Upload de Imagens (se necessário)
```bash
python3 scripts/upload_images_git.py
```

### 3. Gerar CSV de Imagens
```bash
python3 scripts/generate_image_csv_updated.py
```

## 📋 Dependências

Certifique-se de ter instalado:
```bash
pip3 install requests beautifulsoup4 pandas lxml playwright tqdm
```

## 🎯 Scripts Removidos

Os seguintes scripts foram removidos por serem desnecessários:
- `test_progress.py` - Script de teste da barra de progresso
- `test_breadcrumb_extraction.py` - Script de teste de extração
- `test_koerich_breadcrumb.py` - Script de teste específico
- `scrape_koerich_playwright.py` - Script de teste do Playwright
- `scrape_koerich_page.py` - Script de teste básico
- `generate_image_csv.py` - Versão antiga do gerador de CSV

## 📝 Notas

- O script principal é `scraper_sem_imagens.py`
- Use `upload_images_git.py` para upload de imagens (mais simples)
- O `generate_image_csv_updated.py` é necessário apenas após upload de imagens
- Todos os scripts estão otimizados e limpos
