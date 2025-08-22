#!/usr/bin/env python3
"""
Script para configurar repositório Git local após criar no GitHub
"""

import subprocess
import sys
from pathlib import Path

def check_git_installed():
    """Verifica se o Git está instalado"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_git_configured():
    """Verifica se o Git está configurado"""
    try:
        subprocess.run(["git", "config", "user.name"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def setup_git_repo(repo_url):
    """Configura o repositório Git local"""
    
    print("🔧 Configurando repositório Git local...")
    
    # Verificar se já é um repositório Git
    if Path(".git").exists():
        print("⚠️ Repositório Git já existe. Continuando...")
    else:
        # Inicializar Git
        print("📁 Inicializando repositório Git...")
        subprocess.run(["git", "init"], check=True)
    
    # Verificar se remote já existe
    try:
        result = subprocess.run(["git", "remote", "get-url", "origin"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"🔗 Remote origin já configurado: {result.stdout.strip()}")
            update_remote = input("🔄 Atualizar remote origin? (s/n): ").lower().startswith('s')
            if update_remote:
                subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)
                print(f"✅ Remote origin atualizado: {repo_url}")
        else:
            # Adicionar remote
            print(f"🔗 Adicionando remote origin: {repo_url}")
            subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
    except subprocess.CalledProcessError:
        print(f"🔗 Adicionando remote origin: {repo_url}")
        subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
    
    # Adicionar todos os arquivos
    print("📦 Adicionando arquivos...")
    subprocess.run(["git", "add", "."], check=True)
    
    # Verificar se há mudanças para commit
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        print("ℹ️ Nenhuma mudança para commitar")
        return
    
    # Commit inicial
    print("💾 Fazendo commit inicial...")
    commit_message = """feat: Initial commit - VTEX Product Scraper POC

- Scraper para Colcci e MercadoCar
- Suporte a páginas dinâmicas e estáticas
- Geração de planilhas VTEX
- Documentação completa
- Estrutura organizada e profissional"""
    
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    
    # Push para GitHub
    print("🚀 Enviando para GitHub...")
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    
    print("✅ Repositório configurado e enviado para GitHub!")

def main():
    """Função principal"""
    
    print("🚀 Configurando repositório Git para VTEX Product Scraper")
    print("=" * 60)
    
    # Verificar Git
    if not check_git_installed():
        print("❌ Git não está instalado. Instale o Git primeiro.")
        sys.exit(1)
    
    if not check_git_configured():
        print("❌ Git não está configurado. Configure seu nome e email:")
        print("   git config --global user.name 'Seu Nome'")
        print("   git config --global user.email 'seu@email.com'")
        sys.exit(1)
    
    print("📝 Instruções:")
    print("1. Crie um repositório no GitHub com o nome 'scrapper-poc-example'")
    print("2. Copie a URL do repositório (ex: https://github.com/seu-usuario/scrapper-poc-example.git)")
    print("3. Cole a URL abaixo")
    print()
    
    repo_url = input("🔗 URL do repositório GitHub: ").strip()
    
    if not repo_url:
        print("❌ URL não fornecida")
        sys.exit(1)
    
    if not repo_url.endswith('.git'):
        repo_url += '.git'
    
    try:
        setup_git_repo(repo_url)
        
        # Extrair nome do repositório da URL
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        print(f"\n🎉 Repositório configurado com sucesso!")
        print(f"🔗 Acesse: https://github.com/{repo_name}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro durante configuração: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
