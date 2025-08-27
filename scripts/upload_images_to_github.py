#!/usr/bin/env python3
"""
Script para fazer upload das imagens para o repositório GitHub
"""

import os
import base64
from pathlib import Path
from github import Github
import time

def upload_images_to_github():
    """
    Faz upload das imagens para o repositório GitHub
    """
    # Configurações
    repo_name = "thomas-ramirez/imagens-koerich"
    images_folder = Path.cwd() / 'data' / 'exports' / 'imagens_produtos'
    
    # Token do GitHub (você precisa criar um token pessoal)
    # https://github.com/settings/tokens
    github_token = input("Digite seu token do GitHub: ").strip()
    
    if not github_token:
        print("❌ Token do GitHub é obrigatório!")
        return
    
    try:
        # Conectar ao GitHub
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        
        print(f"🔗 Conectado ao repositório: {repo_name}")
        
        # Listar todas as imagens
        image_files = []
        for filename in os.listdir(images_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
        
        print(f"📁 Encontradas {len(image_files)} imagens para upload")
        
        # Fazer upload de cada imagem
        uploaded_count = 0
        for i, filename in enumerate(image_files, 1):
            file_path = images_folder / filename
            
            try:
                # Ler o arquivo
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Verificar se o arquivo já existe
                try:
                    repo.get_contents(filename)
                    print(f"⚠️  {filename} já existe, pulando...")
                    continue
                except:
                    pass  # Arquivo não existe, pode fazer upload
                
                # Fazer upload
                repo.create_file(
                    path=filename,
                    message=f"Add {filename}",
                    content=content,
                    branch="main"
                )
                
                print(f"✅ [{i}/{len(image_files)}] {filename} enviado com sucesso")
                uploaded_count += 1
                
                # Pequena pausa para não sobrecarregar a API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Erro ao enviar {filename}: {e}")
        
        print(f"\n🎉 Upload concluído!")
        print(f"📊 Total de imagens enviadas: {uploaded_count}")
        print(f"🔗 Repositório: https://github.com/{repo_name}")
        print(f"🔗 URLs base: https://raw.githubusercontent.com/{repo_name}/main/")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando upload das imagens para o GitHub...")
    upload_images_to_github()
