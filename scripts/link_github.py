import os
import csv
import re
from pathlib import Path

# Caminho para a pasta onde estão as imagens
folder_path = Path.cwd() / 'data' / 'exports' / 'imagens_produtos'

# Pasta atual do script
current_dir = Path(__file__).parent

# Hash do commit usado nas URLs (atualizar quando necessário)
commit_hash = "main"  # ou usar um hash específico se necessário
base_url = f"https://raw.githubusercontent.com/thomas-ramirez/imagens-colcci/{commit_hash}/"

rows = []

# Percorre todos os arquivos da pasta
for filename in os.listdir(folder_path):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        match = re.match(r"(\d+)_\d+\.(jpg|jpeg|png)", filename, re.IGNORECASE)
        if match:
            skuid = match.group(1)
            url = f"{base_url}{filename}"
            rows.append([skuid, url])

# ✅ Salvar o CSV na pasta atual do script (autopoc)
csv_path = current_dir / 'imagens_colcci.csv'
with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['skuid', 'url'])
    writer.writerows(rows)

print(f"✅ CSV criado com sucesso em: {csv_path}")
print(f"📁 Pasta das imagens: {folder_path}")
print(f"🔗 Base URL: {base_url}")
print(f"📊 Total de imagens processadas: {len(rows)}")
