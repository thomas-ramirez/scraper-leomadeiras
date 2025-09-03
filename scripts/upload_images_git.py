#!/usr/bin/env python3
"""
Script para criar CSV de imagens e fazer upload para o repositório da Leo Madeiras
"""

import os
import subprocess
import shutil
import pandas as pd
from pathlib import Path

def criar_csv_imagens():
    """
    Cria CSV com as imagens encontradas no formato especificado
    """
    images_folder = Path.cwd() / 'data' / 'exports' / 'imagens_produtos'
    
    if not images_folder.exists():
        print("❌ Pasta de imagens não encontrada. Execute o scraper primeiro!")
        return None
    
    # Buscar todas as imagens
    image_files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print("❌ Nenhuma imagem encontrada para processar. Execute o scraper primeiro!")
        return None
    
    print(f"📸 Processando {len(image_files)} imagens encontradas...")
    
    # Agrupar imagens por SKU
    imagens_por_sku = {}
    for filename in image_files:
        # Extrair SKU do nome do arquivo (formato: SKU_NUMERO.extensao)
        if '_' in filename:
            sku = filename.split('_')[0]
            if sku not in imagens_por_sku:
                imagens_por_sku[sku] = []
            imagens_por_sku[sku].append(filename)
    
    # Criar dados para o CSV
    dados_csv = []
    
    for sku, arquivos in imagens_por_sku.items():
        # Ordenar arquivos por número
        arquivos_ordenados = sorted(arquivos, key=lambda x: int(x.split('_')[1].split('.')[0]))
        
        for i, arquivo in enumerate(arquivos_ordenados):
            # Determinar se é a imagem principal (primeira)
            is_main = (i == 0)
            
            # Gerar label e name baseado na posição
            posicoes = ['primeira', 'segunda', 'terceira', 'quarta', 'quinta', 'sexta', 'sétima', 'oitava', 'nona', 'décima']
            if i < len(posicoes):
                label = posicoes[i]
                name = posicoes[i]
            else:
                label = f"posição_{i+1}"
                name = f"posição_{i+1}"
            
            # URL base do repositório da Leo Madeiras
            url = f"https://raw.githubusercontent.com/thomas-ramirez/images-leomadeiras/main/{arquivo}"
            
            dados_csv.append({
                'IDSKU': sku,
                'IsMain': is_main,
                'Label': label,
                'Name': name,
                'url': url
            })
    
    # Criar DataFrame e salvar CSV
    df_imagens = pd.DataFrame(dados_csv)
    csv_path = Path.cwd() / 'data' / 'exports' / 'imagens_leo_madeiras.csv'
    df_imagens.to_csv(csv_path, index=False, sep=',')
    
    print(f"✅ CSV criado com sucesso: {csv_path}")
    print(f"📊 Total de registros: {len(dados_csv)}")
    print(f"🏷️ SKUs processados: {len(imagens_por_sku)}")
    
    # Mostrar preview do CSV
    print(f"\n📋 Preview do CSV criado:")
    print(df_imagens.head(10).to_string(index=False))
    
    return csv_path

def upload_images_git():
    """
    Faz upload das imagens da Leo Madeiras usando Git
    """
    # Primeiro criar o CSV
    csv_path = criar_csv_imagens()
    if not csv_path:
        return
    
    # Configurações
    repo_url = "https://github.com/thomas-ramirez/images-leomadeiras.git"
    images_folder = Path.cwd() / 'data' / 'exports' / 'imagens_produtos'
    temp_repo = Path.cwd() / 'temp_images_repo'
    
    try:
        # Verificar se existem imagens para upload
        image_files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not image_files:
            print("❌ Nenhuma imagem encontrada para upload!")
            return
        
        print(f"📸 Encontradas {len(image_files)} imagens para upload")
        
        # Criar diretório temporário
        if temp_repo.exists():
            shutil.rmtree(temp_repo)
        temp_repo.mkdir()
        
        print(f"📁 Diretório temporário criado: {temp_repo}")
        
        # Clonar o repositório
        print("🔗 Clonando repositório da Leo Madeiras...")
        subprocess.run([
            'git', 'clone', repo_url, str(temp_repo)
        ], check=True)
        
        # Copiar imagens para o repositório
        print("📁 Copiando imagens para o repositório...")
        copied_count = 0
        for filename in image_files:
            src = images_folder / filename
            dst = temp_repo / filename
            shutil.copy2(src, dst)
            copied_count += 1
            print(f"  ✅ {filename} copiado")
        
        # Copiar o CSV também
        csv_filename = csv_path.name
        src_csv = csv_path
        dst_csv = temp_repo / csv_filename
        shutil.copy2(src_csv, dst_csv)
        print(f"  ✅ {csv_filename} copiado")
        
        print(f"📊 {copied_count} imagens e 1 CSV copiados com sucesso")
        
        # Adicionar, commit e push
        os.chdir(temp_repo)
        
        print("📝 Adicionando arquivos ao Git...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        print("💾 Fazendo commit...")
        commit_message = f"🖼️ Add {copied_count} product images + CSV from Leo Madeiras scraper"
        subprocess.run([
            'git', 'commit', '-m', commit_message
        ], check=True)
        
        print("🚀 Fazendo push para o GitHub...")
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print(f"\n🎉 Upload concluído com sucesso!")
        print(f"📊 Total de imagens enviadas: {copied_count}")
        print(f"📋 CSV enviado: {csv_filename}")
        print(f"🔗 Repositório: {repo_url}")
        print(f"🔗 URLs base: https://raw.githubusercontent.com/thomas-ramirez/images-leomadeiras/main/")
        print(f"📋 Exemplo de URL: https://raw.githubusercontent.com/thomas-ramirez/images-leomadeiras/main/10525549_1.jpg")
        
        # Mostrar lista das imagens enviadas
        print(f"\n📸 Imagens enviadas:")
        for filename in sorted(image_files):
            print(f"  • {filename}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no Git: {e}")
        print("💡 Verifique se você tem acesso ao repositório e se o Git está configurado")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    finally:
        # Limpar diretório temporário
        if temp_repo.exists():
            shutil.rmtree(temp_repo)
            print("🧹 Diretório temporário removido")

if __name__ == "__main__":
    print("🚀 Iniciando processamento de imagens da Leo Madeiras...")
    print("=" * 70)
    upload_images_git()
