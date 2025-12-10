import pandas as pd

# Leer el CSV
df = pd.read_csv('feedbacks/Feedbacks.csv')

print('=' * 70)
print('VERIFICACION DE COMENTARIOS UNICOS')
print('=' * 70)

print(f'\nTotal registros: {len(df)}')
print(f'Comentarios no vacios: {len(df[df["comentarios"] != ""])}')

# Verificar comentarios únicos
comentarios_no_vacios = df[df['comentarios'] != '']['comentarios']
comentarios_unicos = comentarios_no_vacios.nunique()
total_comentarios = len(comentarios_no_vacios)

print(f'\nComentarios no vacios: {total_comentarios}')
print(f'Comentarios unicos: {comentarios_unicos}')
print(f'Comentarios duplicados: {total_comentarios - comentarios_unicos}')

# Buscar duplicados si los hay
if total_comentarios > comentarios_unicos:
    print(f'\n[ADVERTENCIA] Se encontraron comentarios duplicados:')
    duplicados = comentarios_no_vacios[comentarios_no_vacios.duplicated(keep=False)]
    print(f'Total registros con comentarios duplicados: {len(duplicados)}')
    
    # Mostrar los comentarios duplicados
    print(f'\nComentarios duplicados (primeros 10):')
    for comentario, count in duplicados.value_counts().head(10).items():
        print(f'\n  Repetido {count} veces:')
        print(f'  "{comentario[:100]}..."')
        
    # Mostrar registros con comentarios duplicados
    print(f'\nRegistros con comentarios duplicados (primeros 5):')
    for idx, row in df[df['comentarios'].isin(duplicados.unique())].head(5).iterrows():
        print(f'\n  Id_encuesta: {row["Id_encuesta"]}, id_usuario: {row["id_usuario"]}')
        print(f'  Comentario: {row["comentarios"][:80]}...')
else:
    print(f'\n[OK] Todos los comentarios son unicos!')

# Verificar también comentarios vacíos
comentarios_vacios = len(df[df['comentarios'] == ''])
print(f'\nComentarios vacios: {comentarios_vacios}')

# Estadísticas adicionales
if total_comentarios > 0:
    longitudes = comentarios_no_vacios.str.len()
    print(f'\nEstadisticas de longitud:')
    print(f'  Promedio: {longitudes.mean():.1f} caracteres')
    print(f'  Minimo: {longitudes.min()} caracteres')
    print(f'  Maximo: {longitudes.max()} caracteres')
    print(f'  Mediana: {longitudes.median():.1f} caracteres')

print('\n' + '=' * 70)
if total_comentarios == comentarios_unicos:
    print('[OK] Todos los comentarios son unicos')
else:
    print(f'[ADVERTENCIA] Hay {total_comentarios - comentarios_unicos} comentarios duplicados')
print('=' * 70)

