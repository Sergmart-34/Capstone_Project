"""
Script de verificación completa del archivo generado
Verifica todas las peculiaridades y requisitos configurados
"""

import pandas as pd
import os

# Obtener el directorio del script
script_dir = os.path.dirname(os.path.abspath(__file__))
archivo = os.path.join(script_dir, 'formularios_unificado.xlsx')

print("=" * 70)
print("VERIFICACIÓN COMPLETA DEL ARCHIVO GENERADO")
print("=" * 70)

# Leer el archivo
try:
    df = pd.read_excel(archivo)
    print(f"\n[OK] Archivo leído correctamente: {archivo}")
except Exception as e:
    print(f"\n[ERROR] No se pudo leer el archivo: {e}")
    exit(1)

# ============================================================================
# 1. VERIFICACIÓN BÁSICA
# ============================================================================

print("\n" + "=" * 70)
print("1. VERIFICACIÓN BÁSICA")
print("=" * 70)

print(f"\nTotal de registros: {len(df)}")
print(f"Total de columnas: {len(df.columns)}")
print(f"Columnas: {list(df.columns)}")

# Verificar número de registros
if len(df) != 700:
    print(f"[ERROR] Número de registros incorrecto: {len(df)} (esperado: 700)")
else:
    print(f"[OK] Número de registros correcto: {len(df)}")

# Verificar columnas requeridas
columnas_requeridas = ['id_usuario', 'Ciudad', 'País', 'Edad', 'Género', 
                       'Área de interés para formarse', 'Titulación académica', 
                       'Área de estudios', 'Experiencia laboral', 'Sector laboral', 
                       'Motivo de la formación']
columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
if columnas_faltantes:
    print(f"[ERROR] Columnas faltantes: {columnas_faltantes}")
else:
    print(f"[OK] Todas las columnas requeridas están presentes")

# ============================================================================
# 2. VERIFICACIÓN DE IDs
# ============================================================================

print("\n" + "=" * 70)
print("2. VERIFICACIÓN DE IDs")
print("=" * 70)

ids_unicos = df['id_usuario'].nunique()
total_ids = len(df)
print(f"\nIDs únicos: {ids_unicos}")
print(f"Total de registros: {total_ids}")

if ids_unicos != total_ids:
    print(f"[ERROR] Hay IDs duplicados: {total_ids - ids_unicos} duplicados")
    duplicados = df[df.duplicated(subset=['id_usuario'], keep=False)]
    print(f"Registros con IDs duplicados:\n{duplicados[['id_usuario']].head(10)}")
else:
    print(f"[OK] Todos los IDs son únicos")

# Verificar formato de IDs
print(f"\nPrimer ID: {df['id_usuario'].iloc[0]}")
print(f"Último ID: {df['id_usuario'].iloc[-1]}")

if df['id_usuario'].iloc[0] != 'U0001':
    print(f"[ERROR] El primer ID no es U0001: {df['id_usuario'].iloc[0]}")
else:
    print(f"[OK] Primer ID correcto: U0001")

if df['id_usuario'].iloc[-1] != 'U0700':
    print(f"[ERROR] El último ID no es U0700: {df['id_usuario'].iloc[-1]}")
else:
    print(f"[OK] Último ID correcto: U0700")

# Verificar formato de IDs
formato_incorrecto = df[~df['id_usuario'].astype(str).str.match(r'^U\d{4}$')]
if len(formato_incorrecto) > 0:
    print(f"[ERROR] IDs con formato incorrecto: {len(formato_incorrecto)}")
    print(formato_incorrecto[['id_usuario']].head())
else:
    print(f"[OK] Todos los IDs tienen el formato correcto (U####)")

# ============================================================================
# 3. VERIFICACIÓN DE EDADES
# ============================================================================

print("\n" + "=" * 70)
print("3. VERIFICACIÓN DE EDADES")
print("=" * 70)

edad_min = df['Edad'].min()
edad_max = df['Edad'].max()
edad_media = df['Edad'].mean()

print(f"\nEdad mínima: {edad_min}")
print(f"Edad máxima: {edad_max}")
print(f"Edad media: {edad_media:.2f}")

# Verificar rango 18-50
if edad_min < 18:
    print(f"[ERROR] Hay edades menores a 18: mínimo {edad_min}")
else:
    print(f"[OK] Todas las edades son >= 18")

if edad_max > 50:
    print(f"[ERROR] Hay edades mayores a 50: máximo {edad_max}")
else:
    print(f"[OK] Todas las edades son <= 50")

# Verificar distribución
edad_18_30 = len(df[(df['Edad'] >= 18) & (df['Edad'] <= 30)])
edad_30_40 = len(df[(df['Edad'] > 30) & (df['Edad'] <= 40)])
edad_40_50 = len(df[(df['Edad'] > 40) & (df['Edad'] <= 50)])

pct_18_30 = edad_18_30 / len(df) * 100
pct_30_40 = edad_30_40 / len(df) * 100
pct_40_50 = edad_40_50 / len(df) * 100

print(f"\nDistribución de edades:")
print(f"  18-30 años: {edad_18_30} ({pct_18_30:.1f}%) - Objetivo: 60%")
print(f"  30-40 años: {edad_30_40} ({pct_30_40:.1f}%) - Objetivo: 30%")
print(f"  40-50 años: {edad_40_50} ({pct_40_50:.1f}%) - Objetivo: 10%")

# Verificar si está dentro de tolerancia (5%)
tolerancia = 5
if abs(pct_18_30 - 60) > tolerancia:
    print(f"[ADVERTENCIA] Distribución 18-30 fuera de tolerancia: {pct_18_30:.1f}% (objetivo: 60% ± {tolerancia}%)")
else:
    print(f"[OK] Distribución 18-30 dentro de tolerancia")

if abs(pct_30_40 - 30) > tolerancia:
    print(f"[ADVERTENCIA] Distribución 30-40 fuera de tolerancia: {pct_30_40:.1f}% (objetivo: 30% ± {tolerancia}%)")
else:
    print(f"[OK] Distribución 30-40 dentro de tolerancia")

if abs(pct_40_50 - 10) > tolerancia:
    print(f"[ADVERTENCIA] Distribución 40-50 fuera de tolerancia: {pct_40_50:.1f}% (objetivo: 10% ± {tolerancia}%)")
else:
    print(f"[OK] Distribución 40-50 dentro de tolerancia")

# ============================================================================
# 4. VERIFICACIÓN DE COHERENCIA EDAD-EXPERIENCIA
# ============================================================================

print("\n" + "=" * 70)
print("4. VERIFICACIÓN DE COHERENCIA EDAD-EXPERIENCIA")
print("=" * 70)

# Calcular experiencia máxima permitida (edad - 18)
df['exp_max_permitida'] = df['Edad'] - 18
df['coherencia_exp'] = df['Experiencia laboral'] <= df['exp_max_permitida']

incoherentes = df[~df['coherencia_exp']]

if len(incoherentes) > 0:
    print(f"\n[ERROR] Encontrados {len(incoherentes)} registros con experiencia incoherente:")
    print(incoherentes[['id_usuario', 'Edad', 'Experiencia laboral', 'exp_max_permitida']].head(10))
else:
    print(f"\n[OK] Todos los registros tienen coherencia edad-experiencia (100%)")

exp_min = df['Experiencia laboral'].min()
exp_max = df['Experiencia laboral'].max()
exp_media = df['Experiencia laboral'].mean()

print(f"\nExperiencia laboral:")
print(f"  Mínima: {exp_min} años")
print(f"  Máxima: {exp_max} años")
print(f"  Media: {exp_media:.2f} años")

# ============================================================================
# 5. VERIFICACIÓN DE VALORES NULOS
# ============================================================================

print("\n" + "=" * 70)
print("5. VERIFICACIÓN DE VALORES NULOS")
print("=" * 70)

valores_nulos = df.isnull().sum()
columnas_con_nulos = valores_nulos[valores_nulos > 0]

if len(columnas_con_nulos) > 0:
    print(f"\n[ERROR] Columnas con valores nulos:")
    for col, count in columnas_con_nulos.items():
        print(f"  {col}: {count} valores nulos")
else:
    print(f"\n[OK] No hay valores nulos en ninguna columna")

# ============================================================================
# 6. VERIFICACIÓN DE CORRELACIONES LÓGICAS
# ============================================================================

print("\n" + "=" * 70)
print("6. VERIFICACIÓN DE CORRELACIONES LÓGICAS")
print("=" * 70)

# Verificar País-Ciudad (muestra de ejemplos)
print("\nEjemplos de correlación País-Ciudad (primeros 10):")
for idx, row in df.head(10).iterrows():
    print(f"  {row['País']} -> {row['Ciudad']}")

# Verificar Área de interés - Sector laboral
print("\nEjemplos de correlación Área de interés - Sector laboral (primeros 10):")
for idx, row in df.head(10).iterrows():
    print(f"  {row['Área de interés para formarse']} -> {row['Sector laboral']}")

# Verificar Titulación - Área de estudios
print("\nEjemplos de correlación Titulación - Área de estudios (primeros 10):")
for idx, row in df.head(10).iterrows():
    print(f"  {row['Titulación académica']} -> {row['Área de estudios']}")

# ============================================================================
# 7. VERIFICACIÓN DE DISTRIBUCIONES
# ============================================================================

print("\n" + "=" * 70)
print("7. VERIFICACIÓN DE DISTRIBUCIONES")
print("=" * 70)

print("\nDistribución de Género:")
print(df['Género'].value_counts())

print("\nDistribución de Países (top 5):")
print(df['País'].value_counts().head())

print("\nDistribución de Áreas de interés (top 5):")
print(df['Área de interés para formarse'].value_counts().head())

# ============================================================================
# 8. RESUMEN FINAL
# ============================================================================

print("\n" + "=" * 70)
print("RESUMEN FINAL")
print("=" * 70)

errores = []
advertencias = []

# Resumen de verificaciones
if len(df) != 700:
    errores.append(f"Número de registros incorrecto: {len(df)} (esperado: 700)")

if df['id_usuario'].nunique() != len(df):
    errores.append("Hay IDs duplicados")

if df['id_usuario'].iloc[0] != 'U0001' or df['id_usuario'].iloc[-1] != 'U0700':
    errores.append("Rango de IDs incorrecto")

if df['Edad'].min() < 18 or df['Edad'].max() > 50:
    errores.append("Edades fuera del rango 18-50")

if len(incoherentes) > 0:
    errores.append(f"Coherencia edad-experiencia: {len(incoherentes)} registros incoherentes")

if len(columnas_con_nulos) > 0:
    errores.append(f"Valores nulos en {len(columnas_con_nulos)} columnas")

if abs(pct_18_30 - 60) > tolerancia:
    advertencias.append(f"Distribución 18-30: {pct_18_30:.1f}% (objetivo: 60%)")

if abs(pct_30_40 - 30) > tolerancia:
    advertencias.append(f"Distribución 30-40: {pct_30_40:.1f}% (objetivo: 30%)")

if abs(pct_40_50 - 10) > tolerancia:
    advertencias.append(f"Distribución 40-50: {pct_40_50:.1f}% (objetivo: 10%)")

print(f"\nErrores encontrados: {len(errores)}")
if errores:
    for error in errores:
        print(f"  [ERROR] {error}")
else:
    print("  [OK] No se encontraron errores")

print(f"\nAdvertencias: {len(advertencias)}")
if advertencias:
    for adv in advertencias:
        print(f"  [ADVERTENCIA] {adv}")
else:
    print("  [OK] No hay advertencias")

if len(errores) == 0:
    print("\n" + "=" * 70)
    print("[OK] VERIFICACIÓN COMPLETA: El archivo cumple con todos los requisitos")
    print("=" * 70)
else:
    print("\n" + "=" * 70)
    print("[ERROR] Se encontraron errores que deben corregirse")
    print("=" * 70)

