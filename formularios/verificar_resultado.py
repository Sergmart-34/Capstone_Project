import pandas as pd

df = pd.read_excel('formularios_unificado.xlsx')

print('=' * 70)
print('VERIFICACIÓN DEL ARCHIVO GENERADO')
print('=' * 70)

print(f'\nTotal registros: {len(df)}')
print(f'Total columnas: {len(df.columns)}')

print(f'\nPrimeros 5 registros:')
print(df.head().to_string())

print(f'\nÚltimos 5 registros:')
print(df.tail().to_string())

print(f'\nVerificación de IDs:')
print(f'IDs únicos: {df["id_usuario"].nunique()}')
print(f'Primer ID: {df["id_usuario"].iloc[0]}')
print(f'Último ID: {df["id_usuario"].iloc[-1]}')

print(f'\nVerificación de coherencia Edad-Experiencia:')
df['coherencia'] = df['Edad'] - df['Experiencia laboral'] >= 18
coherentes = df['coherencia'].sum()
total = len(df)
print(f'Registros coherentes: {coherentes}/{total} ({coherentes/total*100:.1f}%)')

if coherentes < total:
    print('\nRegistros con posibles inconsistencias:')
    inconsistencias = df[~df['coherencia']]
    print(inconsistencias[['id_usuario', 'Edad', 'Experiencia laboral']].to_string())

print(f'\nVerificación de correlaciones:')
print(f'\nÁrea de interés vs Sector laboral (primeros 10):')
for idx, row in df.head(10).iterrows():
    print(f"  {row['Área de interés para formarse']} -> {row['Sector laboral']}")

print(f'\nPaís vs Ciudad (primeros 10):')
for idx, row in df.head(10).iterrows():
    print(f"  {row['País']} -> {row['Ciudad']}")

print('\n' + '=' * 70)

