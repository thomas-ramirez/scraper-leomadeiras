#!/usr/bin/env python3
"""
Script para criar repositório GitHub para o VTEX Product Scraper
"""

import os
import sys
import subprocess
from pathlib import Path
from github import Github
import getpass

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

def create_github_repo(repo_name, description, is_public=True):
    """Cria repositório no GitHub"""
    
    print("🔐 Para criar o repositório, você precisa de um token do GitHub.")
    print("📝 Crie um token em: https://github.com/settings/tokens")
    print("   - Selecione 'repo' para acesso completo aos repositórios")
    
    token = getpass.getpass("🔑 Digite seu token do GitHub: ")
    
    try:
        g = Github(token)
        user = g.get_user()
        
        print(f"👤 Conectado como: {user.login}")
        
        # Criar repositório
        repo = user.create_repo(
            name=repo_name,
            description=description,
            private=not is_public,
            auto_init=False,
            gitignore_template="Python"
        )
        
        print(f"✅ Repositório criado: {repo.html_url}")
        return repo
        
    except Exception as e:
        print(f"❌ Erro ao criar repositório: {e}")
        return None

def setup_git_repo(repo_url, repo_name):
    """Configura o repositório Git local"""
    
    current_dir = Path.cwd()
    
    # Inicializar Git
    subprocess.run(["git", "init"], check=True)
    
    # Adicionar remote
    subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
    
    # Adicionar todos os arquivos
    subprocess.run(["git", "add", "."], check=True)
    
    # Commit inicial
    subprocess.run([
        "git", "commit", "-m", 
        "feat: Initial commit - VTEX Product Scraper POC\n\n- Scraper para Colcci e MercadoCar\n- Suporte a páginas dinâmicas e estáticas\n- Geração de planilhas VTEX\n- Documentação completa"
    ], check=True)
    
    # Push para GitHub
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    
    print(f"✅ Repositório configurado e enviado para GitHub")
    print(f"🔗 URL: https://github.com/{repo_name}")

def main():
    """Função principal"""
    
    print("🚀 Criando repositório GitHub para VTEX Product Scraper")
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
    
    # Configurações do repositório
    repo_name = "scrapper-poc-example"
    description = "VTEX Product Scraper POC - Solução para extração automatizada de produtos de e-commerces e geração de planilhas compatíveis com VTEX"
    
    print(f"📝 Nome do repositório: {repo_name}")
    print(f"📄 Descrição: {description}")
    
    # Perguntar se é público
    public = input("🌍 Repositório público? (s/n): ").lower().startswith('s')
    
    # Criar repositório no GitHub
    repo = create_github_repo(repo_name, description, public)
    
    if repo:
        # Configurar Git local
        setup_git_repo(repo.clone_url, repo.full_name)
        
        print("\n🎉 Repositório criado com sucesso!")
        print(f"🔗 Acesse: {repo.html_url}")
        print("\n📋 Próximos passos:")
        print("1. Adicione colaboradores se necessário")
        print("2. Configure GitHub Pages se desejar")
        print("3. Adicione issues e milestones")
        print("4. Compartilhe com a comunidade VTEX")
        
    else:
        print("❌ Falha ao criar repositório")
        sys.exit(1)

if __name__ == "__main__":
    main()
