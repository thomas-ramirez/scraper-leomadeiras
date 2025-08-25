import os
import csv
import re
from pathlib import Path
from collections import defaultdict

# Caminho para a pasta onde estão as imagens
folder_path = Path.cwd() / 'data' / 'exports' / 'imagens_produtos'

# Hash do commit usado nas URLs (atualizar quando necessário)
commit_hash = "main"  # ou usar um hash específico se necessário
base_url = f"https://raw.githubusercontent.com/thomas-ramirez/imagens-colcci/{commit_hash}/"

# Dicionário para agrupar imagens por SKUID
skuid_images = defaultdict(list)

# Percorre todos os arquivos da pasta
for filename in os.listdir(folder_path):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        match = re.match(r"(\d+)_(\d+)\.(jpg|jpeg|png)", filename, re.IGNORECASE)
        if match:
            skuid = match.group(1)
            image_number = int(match.group(2))
            url = f"{base_url}{filename}"
            skuid_images[skuid].append((image_number, url))

# Criar linhas do CSV no novo formato
rows = []

for skuid, images in skuid_images.items():
    # Ordenar imagens por número
    images.sort(key=lambda x: x[0])
    
    # Criar linhas para cada imagem
    for i, (image_number, url) in enumerate(images):
        is_main = (i == 0)  # Primeira imagem é a principal
        
        # Determinar label e name baseado na posição
        if i == 0:
            label = "primeira"
            name = "primeira"
        elif i == 1:
            label = "segunda"
            name = "segunda"
        elif i == 2:
            label = "terceira"
            name = "terceira"
        elif i == 3:
            label = "quarta"
            name = "quarta"
        elif i == 4:
            label = "quinta"
            name = "quinta"
        else:
            label = f"{i+1}ª"
            name = f"{i+1}ª"
        
        rows.append([skuid, str(is_main), label, name, url])

# ✅ Salvar o CSV na pasta exports (mesmo local das imagens)
csv_path = folder_path.parent / 'imagens_colcci.csv'
with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['_IDSKU', 'IsMain', 'Label', 'Name', 'url'])
    writer.writerows(rows)

print(f"✅ CSV criado com sucesso em: {csv_path}")
print(f"📁 Pasta das imagens: {folder_path}")
print(f"🔗 Base URL: {base_url}")
print(f"📊 Total de SKUIDs processados: {len(skuid_images)}")
print(f"📊 Total de imagens: {len(rows)}")

# Mostrar alguns exemplos
print("\n📋 Exemplos de conversão:")
for i, row in enumerate(rows[:10]):
    print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4].split('/')[-1]}")
    if i == 9:
        print("  ...")
        break
