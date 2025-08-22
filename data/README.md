# Dados e Exports

Esta pasta contém todos os dados e arquivos gerados pelo VTEX Product Scraper.

## 📁 Estrutura

### `csv/`
Planilhas de entrada e dados de referência.
- `produtos_link.csv`: Lista de URLs para processamento
- `imagens_mercadocar.csv`: Dados de exemplo do MercadoCar

### `exports/`
Planilhas geradas pelo scraper.
- `produtos_vtex.csv`: Planilha final pronta para importação VTEX

### `Runner - nova POC1.postman_collection.json`
Collection do Postman para testes de API.

## 📊 Arquivos de Dados

### Planilhas de Entrada
- **Formato**: CSV
- **Localização**: `csv/`
- **Uso**: URLs dos produtos para extração

### Planilhas de Saída
- **Formato**: CSV
- **Localização**: `exports/`
- **Uso**: Importação direta no VTEX

## 🔄 Fluxo de Dados

```
1. URLs em csv/produtos_link.csv
2. Processamento pelo scraper.py
3. Resultado em exports/produtos_vtex.csv
4. Importação no VTEX
```

## 📝 Notas

- Os arquivos em `exports/` são gerados automaticamente
- Mantenha backups das planilhas importantes
- Use `csv/` para armazenar dados de referência
- O scraper lê de `~/Downloads/produtos_link.csv` e escreve em `exports/`
