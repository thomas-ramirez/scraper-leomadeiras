# Scripts Auxiliares

Esta pasta contém scripts auxiliares para desenvolvimento e debug do VTEX Product Scraper.

## 📁 Arquivos

### `check_fields.py`
Script para verificar e validar campos extraídos dos produtos.
- Valida estrutura dos dados
- Verifica campos obrigatórios
- Gera relatórios de qualidade

### `debug_scraper.py`
Script para debug e análise do scraper.
- Testa extração de produtos individuais
- Analisa estrutura HTML das páginas
- Identifica problemas de extração

### `link_github.py`
Script para integração com GitHub.
- Criação de repositórios
- Upload de arquivos
- Configuração de workflows

## 🚀 Como Usar

```bash
# Verificar campos extraídos
python scripts/check_fields.py

# Debug de extração
python scripts/debug_scraper.py

# Configurar GitHub
python scripts/link_github.py
```

## 📝 Notas

- Estes scripts são auxiliares e não são necessários para o uso básico do scraper
- Use apenas se precisar de funcionalidades específicas de debug ou desenvolvimento
- Consulte a documentação principal em `../docs/` para uso do scraper
