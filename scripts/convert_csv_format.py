#!/usr/bin/env python3
"""
Script para converter o formato do CSV imagens_colcci.csv
para o formato do images.csv com colunas: _IDSKU, IsMain, Label, Name, url
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

def convert_csv_format():
    # Caminho do arquivo original
    input_file = Path.cwd() / 'data' / 'exports' / 'imagens_colcci.csv'
    output_file = Path.cwd() / 'data' / 'exports' / 'imagens_colcci_formatted.csv'
    
    # Dicionário para agrupar imagens por SKUID
    skuid_images = defaultdict(list)
    
    # Ler o arquivo original
    with open(input_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            skuid = row['skuid']
            url = row['url']
            
            # Extrair o número da imagem do nome do arquivo
            filename = url.split('/')[-1]
            match = re.match(r'\d+_(\d+)\.jpg', filename)
            if match:
                image_number = int(match.group(1))
                skuid_images[skuid].append((image_number, url))
    
    # Ordenar imagens por número e criar linhas do novo formato
    new_rows = []
    
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
            
            new_rows.append({
                '_IDSKU': skuid,
                'IsMain': str(is_main),
                'Label': label,
                'Name': name,
                'url': url
            })
    
    # Escrever o novo arquivo
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['_IDSKU', 'IsMain', 'Label', 'Name', 'url']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_rows)
    
    print(f"✅ CSV convertido com sucesso!")
    print(f"📁 Arquivo original: {input_file}")
    print(f"📁 Arquivo novo: {output_file}")
    print(f"📊 Total de SKUIDs processados: {len(skuid_images)}")
    print(f"📊 Total de imagens: {len(new_rows)}")
    
    # Mostrar alguns exemplos
    print("\n📋 Exemplos de conversão:")
    for i, row in enumerate(new_rows[:10]):
        print(f"  {row['_IDSKU']} | {row['IsMain']} | {row['Label']} | {row['Name']} | {row['url'].split('/')[-1]}")
        if i == 9:
            print("  ...")
            break

if __name__ == "__main__":
    convert_csv_format()
