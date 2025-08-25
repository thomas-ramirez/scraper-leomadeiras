# Guia Rápido - VTEX Product Scraper

## 🎯 Ajustes Realizados

### ✅ Problemas Corrigidos

1. **Mapeamentos VTEX Atualizados**
   - Departamentos: Feminino, Masculino, Acessórios, Calçados, etc.
   - Categorias: Vestidos, Blusas, Calças, Saias, Blazers, etc.
   - Marcas: Colcci, Colcci Jeans, Colcci Sport, etc.

2. **Detecção Automática de Gênero**
   - Produtos com "masculina/masculino" → Departamento Masculino
   - Demais produtos Colcci → Departamento Feminino
   - Detecção baseada no nome do produto

3. **Categorização Inteligente**
   - Detecção automática por tipo de produto
   - Vestidos → Categoria "Vestidos"
   - Blusas → Categoria "Blusas"
   - Calças → Categoria "Calças"
   - etc.

4. **Marca Padrão**
   - Todos os produtos Colcci → Marca "Colcci"

## 🚀 Como Usar

### 1. Preparar Lista de URLs
```csv
url
https://www.colcci.com.br/vestido-midi-ombro-a-ombro-440114440-p2451751
https://www.colcci.com.br/blusa-loose-bordado-360130329-p2450474
```

### 2. Executar Scraper
```bash
python3 scraper.py
```

### 3. Resultado
- **Planilha**: `data/exports/produtos_vtex.csv`
- **Imagens**: `data/exports/imagens_produtos/`

## 📊 Exemplo de Saída

| Campo | Exemplo |
|-------|---------|
| `_IDSKU` | `440114440_PP` |
| `_NomeProduto` | `Vestido Midi Ombro À Ombro` |
| `_NomeDepartamento` | `Feminino` |
| `_NomeCategoria` | `Vestidos` |
| `_Marca` | `Colcci` |
| `_Preço` | `467.00` |

## 🔧 Configuração

### Mapeamentos VTEX (IDs)
```python
maps = {
    "departamento": {
        "Feminino": "1",
        "Masculino": "2", 
        "Acessórios": "3",
        # ...
    },
    "categoria": {
        "Vestidos": "1",
        "Blusas": "2",
        "Calças": "3",
        # ...
    },
    "marca": {
        "Colcci": "1",
        "Colcci Jeans": "2",
        # ...
    }
}
```

## 📈 Estatísticas Atuais

- **Total de produtos**: 78
- **Departamentos**: Feminino (54), Masculino (24)
- **Faixa de preços**: R$ 189,00 - R$ 1.277,00
- **Marca**: 100% Colcci

## 🛠️ Funcionalidades

### ✅ Implementado
- [x] Detecção automática de gênero
- [x] Categorização por tipo de produto
- [x] Extração de múltiplos tamanhos (PP, P, M, G)
- [x] Download de imagens
- [x] Geração de planilha VTEX
- [x] Suporte a páginas dinâmicas (Playwright)

### 🔄 Próximos Passos
- [ ] Sistema de cache
- [ ] Validação de dados
- [ ] Tratamento de erros robusto
- [ ] Interface web

## 🚨 Limitações Conhecidas

1. **Imagens 404**: Algumas URLs de imagem retornam 404
2. **Breadcrumbs limitados**: Nem todas as páginas têm breadcrumbs completos
3. **Dependência Playwright**: Necessário para páginas dinâmicas

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação em `docs/`
2. Consulte os exemplos em `examples/`
3. Abra uma issue no GitHub

---

**Desenvolvido para facilitar migrações VTEX por Solutions Engineers**
