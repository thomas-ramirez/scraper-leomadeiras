# Imagens Colcci - VTEX Product Scraper

Repositório contendo as imagens dos produtos extraídos da Colcci para uso no VTEX.

## 📊 Estatísticas

- **Total de imagens**: 108
- **Produtos**: 78 produtos processados
- **Formato**: JPG
- **Origem**: [Colcci](https://www.colcci.com.br)

## 🗂️ Estrutura

As imagens seguem o padrão de nomenclatura:
```
{SKU}_{número}.jpg
```

Exemplos:
- `440114440_2.jpg` - Vestido Midi Ombro À Ombro (imagem 2)
- `360130329_3.jpg` - Blusa Loose Bordado (imagem 3)
- `10107805_4.jpg` - Calça Masculina (imagem 4)

## 🔗 URLs de Acesso

As imagens podem ser acessadas via:
```
https://raw.githubusercontent.com/thomas-ramirez/imagens-colcci/main/{nome_arquivo}
```

Exemplo:
```
https://raw.githubusercontent.com/thomas-ramirez/imagens-colcci/main/440114440_2.jpg
```

## 📋 Produtos Incluídos

### Feminino (54 produtos)
- Vestidos (Vestido Midi Ombro À Ombro, Vestido Linho Solto, etc.)
- Blusas (Blusa Loose Bordado, Blusa Comfort Em Crochê, etc.)
- Saias (Saia Linho Balonê, Saia Midi Com Fenda, etc.)
- Blazers (Blazer Feminino Frente Única, Blazer Alfaiataria, etc.)

### Masculino (24 produtos)
- Camisetas (Camiseta Masculina Reta, Camiseta Basic, etc.)
- Camisas (Camisa Masculina Linho Relax, Camisa Linho Box, etc.)
- Bermudas (Bermuda Masculina Alfaiataria, Bermuda Masculina Sarja, etc.)
- Calças (Calça Masculina Em Sarja Reta)
- Jaquetas (Jaqueta Masculina Jeans)

## 🛠️ Uso no VTEX

Estas imagens são utilizadas no campo `_ImagensURLs` da planilha VTEX gerada pelo scraper.

### Exemplo de uso:
```csv
_IDSKU,_ImagensURLs
440114440_PP,https://raw.githubusercontent.com/thomas-ramirez/imagens-colcci/main/440114440_2.jpg;https://raw.githubusercontent.com/thomas-ramirez/imagens-colcci/main/440114440_3.jpg
```

## 📈 Faixa de Preços

- **Mínimo**: R$ 189,00
- **Máximo**: R$ 1.277,00
- **Média**: R$ 500,00

## 🔄 Atualizações

Este repositório é atualizado automaticamente quando novos produtos são processados pelo VTEX Product Scraper.

---

**Gerado automaticamente pelo VTEX Product Scraper**
**Data**: 25/08/2025
**Total de imagens**: 108
