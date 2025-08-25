# Scripts do VTEX Product Scraper

Scripts auxiliares para o VTEX Product Scraper.

## 📁 Arquivos

### `link_github.py`
Gera CSV com links das imagens no GitHub.
```bash
python3 scripts/link_github.py
```

### `upload_images.py`
Automatiza upload de imagens para o repositório GitHub.
```bash
python3 scripts/upload_images.py
```

### `imagens_colcci.csv`
CSV com links das imagens (108 imagens).
- Formato: `skuid,url`
- Base URL: `https://raw.githubusercontent.com/thomas-ramirez/imagens-colcci/main/`

## 🚀 Fluxo de Trabalho

1. **Executar scraper**: `python3 scraper.py`
2. **Upload imagens**: `python3 scripts/upload_images.py`
3. **Gerar links**: `python3 scripts/link_github.py`

---
**VTEX Product Scraper** - Scripts auxiliares
