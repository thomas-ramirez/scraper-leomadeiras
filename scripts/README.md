# Scripts Utilitários

Esta pasta contém scripts auxiliares para automatizar tarefas específicas do projeto.

## 📁 Arquivos Disponíveis

### `link_github.py`
**Propósito**: Gerar CSV com links das imagens no formato VTEX
- **Entrada**: Pasta `data/exports/imagens_produtos/`
- **Saída**: `data/exports/imagens_colcci.csv`
- **Formato**: `_IDSKU, IsMain, Label, Name, url`
- **Uso**: `python3 scripts/link_github.py`

### `upload_images.py`
**Propósito**: Upload automático de imagens para repositório GitHub
- **Entrada**: Pasta `data/exports/imagens_produtos/`
- **Destino**: `https://github.com/thomas-ramirez/imagens-colcci`
- **Uso**: `python3 scripts/upload_images.py`

### `convert_csv_format.py`
**Propósito**: Converter formato do CSV de imagens
- **Entrada**: `data/exports/imagens_colcci.csv` (formato antigo)
- **Saída**: `data/exports/imagens_colcci_formatted.csv` (formato novo)
- **Uso**: `python3 scripts/convert_csv_format.py`

## 🔄 Fluxo de Trabalho

1. **Scraper**: `python3 scraper.py` (gera imagens em `imagens_produtos/`)
2. **Upload**: `python3 scripts/upload_images.py` (envia para GitHub)
3. **Links**: `python3 scripts/link_github.py` (gera CSV com URLs)

## 📊 Formato do CSV

O arquivo `imagens_colcci.csv` segue o formato:
```csv
_IDSKU,IsMain,Label,Name,url
80104817,True,primeira,primeira,https://raw.githubusercontent.com/thomas-ramirez/imagens-colcci/main/80104817_2.jpg
80104817,False,segunda,segunda,https://raw.githubusercontent.com/thomas-ramirez/imagens-colcci/main/80104817_3.jpg
```

- **IsMain**: `True` para primeira imagem, `False` para demais
- **Label/Name**: "primeira", "segunda", "terceira", etc.
- **URL**: Link direto para imagem no GitHub
