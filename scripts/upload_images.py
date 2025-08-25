#!/usr/bin/env python3
"""
Script para automatizar o upload de imagens para o repositório GitHub
"""

import os
import subprocess
import shutil
from pathlib import Path

def upload_images_to_github():
    """
    Upload das imagens processadas para o repositório GitHub
    """
    print("🚀 Iniciando upload das imagens para GitHub...")
    
    # Caminhos
    current_dir = Path(__file__).parent.parent
    images_dir = current_dir / "data" / "exports" / "imagens_produtos"
    github_repo_dir = current_dir.parent / "imagens-colcci"
    
    # Verificar se as imagens existem
    if not images_dir.exists():
        print("❌ Diretório de imagens não encontrado!")
        return False
    
    # Contar imagens
    image_files = list(images_dir.glob("*.jpg"))
    if not image_files:
        print("❌ Nenhuma imagem encontrada!")
        return False
    
    print(f"📊 Encontradas {len(image_files)} imagens")
    
    # Verificar se o repositório GitHub existe
    if not github_repo_dir.exists():
        print("❌ Repositório GitHub não encontrado!")
        print("💡 Execute: git clone https://github.com/thomas-ramirez/imagens-colcci.git")
        return False
    
    try:
        # Navegar para o repositório
        os.chdir(github_repo_dir)
        print(f"📁 Diretório: {github_repo_dir}")
        
        # Limpar imagens antigas
        print("🧹 Limpando imagens antigas...")
        for old_file in github_repo_dir.glob("*.jpg"):
            old_file.unlink()
        
        # Copiar novas imagens
        print("📋 Copiando novas imagens...")
        for image_file in image_files:
            shutil.copy2(image_file, github_repo_dir)
        
        # Adicionar ao Git
        print("➕ Adicionando ao Git...")
        subprocess.run(["git", "add", "."], check=True)
        
        # Verificar se há mudanças
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True, check=True)
        
        if not result.stdout.strip():
            print("✅ Nenhuma mudança detectada")
            return True
        
        # Commit
        print("💾 Fazendo commit...")
        commit_message = f"feat: atualizar imagens - {len(image_files)} arquivos"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push
        print("🚀 Fazendo push...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ Upload concluído com sucesso!")
        print(f"📊 {len(image_files)} imagens enviadas para GitHub")
        print("🔗 Acesse: https://github.com/thomas-ramirez/imagens-colcci")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no Git: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def update_readme():
    """
    Atualizar o README do repositório de imagens
    """
    try:
        github_repo_dir = Path(__file__).parent.parent.parent / "imagens-colcci"
        os.chdir(github_repo_dir)
        
        # Contar imagens
        image_files = list(github_repo_dir.glob("*.jpg"))
        
        # Ler README atual
        readme_path = github_repo_dir / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Atualizar estatísticas
            content = content.replace(
                "- **Total de imagens**: 108",
                f"- **Total de imagens**: {len(image_files)}"
            )
            
            # Salvar
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("📝 README atualizado")
            
    except Exception as e:
        print(f"⚠️ Erro ao atualizar README: {e}")

if __name__ == "__main__":
    print("🖼️ Upload de Imagens para GitHub")
    print("=" * 40)
    
    success = upload_images_to_github()
    
    if success:
        update_readme()
        print("\n🎉 Processo concluído!")
    else:
        print("\n❌ Processo falhou!")
        exit(1)
