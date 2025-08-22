import pandas as pd

# Ler o CSV
df = pd.read_csv('/Users/thomasramirez/Downloads/produtos_vtex.csv')

print("🔍 VERIFICAÇÃO DOS CAMPOS DE DEPARTAMENTO, CATEGORIA E MARCA")
print("=" * 80)

# Verificar campos específicos
campos_verificar = [
    '_IDDepartamento (Não alterável)',
    '_NomeDepartamento', 
    '_IDCategoria',
    '_NomeCategoria',
    '_IDMarca',
    '_Marca'
]

print("\n📊 ESTATÍSTICAS DOS CAMPOS:")
for campo in campos_verificar:
    if campo in df.columns:
        valores_nao_vazios = df[campo].notna().sum()
        total = len(df)
        print(f"   {campo}: {valores_nao_vazios}/{total} ({valores_nao_vazios/total*100:.1f}%)")
    else:
        print(f"   {campo}: CAMPO NÃO ENCONTRADO")

print("\n📋 AMOSTRAS DOS DADOS:")
# Mostrar algumas linhas com os campos relevantes
colunas_mostrar = ['_NomeProduto (Obrigatório)', '_NomeDepartamento', '_NomeCategoria', '_Marca']
for col in colunas_mostrar:
    if col in df.columns:
        print(f"\n{col}:")
        valores_unicos = df[col].dropna().unique()
        for i, valor in enumerate(valores_unicos[:5]):  # Primeiros 5 valores únicos
            print(f"   {i+1}. {valor}")

print("\n✅ VERIFICAÇÃO COMPLETA!")
