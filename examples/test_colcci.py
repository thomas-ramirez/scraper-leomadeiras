#!/usr/bin/env python3
"""
Exemplo de teste para Colcci
Demonstra como testar o scraper com URLs da Colcci
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import extrair_produto
import json

def test_colcci_single_product():
    """Testa extração de um produto da Colcci"""
    
    # URL de teste da Colcci
    url = "https://www.colcci.com.br/blusa-comfort-em-croche-360125377-p2450047?pp=/44.43458/&v=2450048"
    
    print("🧪 Testando extração de produto Colcci...")
    print(f"URL: {url}")
    print("-" * 50)
    
    try:
        # Extrair produto
        resultado = extrair_produto(url)
        
        # Verificar se retornou lista (múltiplos SKUs)
        if isinstance(resultado, list):
            print(f"✅ Encontrados {len(resultado)} SKUs")
            
            # Mostrar dados do primeiro SKU
            primeiro_sku = resultado[0]
            print(f"\n📋 Dados do primeiro SKU:")
            print(f"   ID SKU: {primeiro_sku['_IDSKU']}")
            print(f"   Nome SKU: {primeiro_sku['_NomeSKU']}")
            print(f"   Nome Produto: {primeiro_sku['_NomeProduto']}")
            print(f"   Preço: {primeiro_sku['_Preço']}")
            print(f"   Categoria: {primeiro_sku['_NomeCategoria']}")
            print(f"   Marca: {primeiro_sku['_Marca']}")
            
            # Mostrar todos os SKUs
            print(f"\n📦 Todos os SKUs encontrados:")
            for i, sku in enumerate(resultado, 1):
                print(f"   {i}. {sku['_IDSKU']} - {sku['_NomeSKU']}")
            
            # Verificar se tem descrição/composição
            descricao = primeiro_sku['_DescricaoProduto']
            if "POLIAMIDA" in descricao or "ELASTANO" in descricao:
                print(f"\n✅ Composição detectada: {descricao[:100]}...")
            else:
                print(f"\n⚠️ Composição não encontrada ou incompleta")
            
            # Verificar imagens
            imagens = primeiro_sku['_ImagensURLs']
            if imagens:
                print(f"\n🖼️ Imagens encontradas: {len(imagens.split(';'))} URLs")
            else:
                print(f"\n⚠️ Nenhuma imagem encontrada")
                
        else:
            print("❌ Erro: resultado não é uma lista")
            return False
            
        print(f"\n✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False

def test_colcci_multiple_products():
    """Testa extração de múltiplos produtos"""
    
    # URLs de teste
    urls = [
        "https://www.colcci.com.br/blusa-comfort-em-croche-360125377-p2450047?pp=/44.43458/&v=2450048",
        # Adicione mais URLs aqui para teste
    ]
    
    print("🧪 Testando múltiplos produtos...")
    print(f"URLs: {len(urls)}")
    print("-" * 50)
    
    total_skus = 0
    sucessos = 0
    
    for i, url in enumerate(urls, 1):
        print(f"\n📦 Produto {i}/{len(urls)}")
        try:
            resultado = extrair_produto(url)
            if isinstance(resultado, list):
                total_skus += len(resultado)
                sucessos += 1
                print(f"   ✅ {len(resultado)} SKUs extraídos")
            else:
                print(f"   ❌ Falha na extração")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print(f"\n📊 Resumo:")
    print(f"   Produtos processados: {len(urls)}")
    print(f"   Sucessos: {sucessos}")
    print(f"   Total de SKUs: {total_skus}")
    
    return sucessos == len(urls)

if __name__ == "__main__":
    print("🚀 Iniciando testes Colcci")
    print("=" * 50)
    
    # Teste 1: Produto único
    test1_ok = test_colcci_single_product()
    
    print("\n" + "=" * 50)
    
    # Teste 2: Múltiplos produtos
    test2_ok = test_colcci_multiple_products()
    
    print("\n" + "=" * 50)
    print("📋 Resultado Final:")
    print(f"   Teste único: {'✅ PASSOU' if test1_ok else '❌ FALHOU'}")
    print(f"   Teste múltiplo: {'✅ PASSOU' if test2_ok else '❌ FALHOU'}")
    
    if test1_ok and test2_ok:
        print("\n🎉 Todos os testes passaram!")
        sys.exit(0)
    else:
        print("\n⚠️ Alguns testes falharam!")
        sys.exit(1)
