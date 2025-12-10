"""
Script para unificar dos archivos Excel de formularios y generar 700 registros totales
con correlaciones lógicas y máxima coherencia entre variables.
"""

import pandas as pd
import numpy as np
import random
import os
from collections import Counter

# Configuración de semilla para reproducibilidad
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# Obtener el directorio del script
try:
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
except NameError:
    # Si __file__ no está definido, usar el directorio actual
    script_dir = os.getcwd()

# Verificar si los archivos están en el directorio actual o en un subdirectorio
if not os.path.exists(os.path.join(script_dir, 'formularios.xlsx')):
    # Intentar en el directorio padre
    parent_dir = os.path.dirname(script_dir)
    if os.path.exists(os.path.join(parent_dir, 'formularios', 'formularios.xlsx')):
        script_dir = os.path.join(parent_dir, 'formularios')
    elif os.path.exists(os.path.join(script_dir, 'formularios', 'formularios.xlsx')):
        script_dir = os.path.join(script_dir, 'formularios')

# ============================================================================
# 1. LECTURA DE ARCHIVOS
# ============================================================================

print("=" * 70)
print("UNIFICACIÓN Y GENERACIÓN DE FORMULARIOS")
print("=" * 70)

print("\n1. Leyendo archivos Excel...")
# Buscar archivos Excel originales (solo los que tienen ~100 registros, excluyendo unificado)
archivos_excel = []
for f in os.listdir(script_dir):
    if f.endswith('.xlsx') and 'unificado' not in f.lower():
        try:
            df_temp = pd.read_excel(os.path.join(script_dir, f))
            # Solo incluir archivos con aproximadamente 100 registros (archivos originales)
            if 90 <= len(df_temp) <= 110:
                archivos_excel.append((f, len(df_temp)))
        except:
            pass

if len(archivos_excel) < 2:
    raise FileNotFoundError(f"Se necesitan al menos 2 archivos Excel con ~100 registros. Encontrados: {[f[0] for f in archivos_excel]}")

# Ordenar por nombre y usar los dos primeros
archivos_excel.sort(key=lambda x: x[0])
archivo1 = os.path.join(script_dir, archivos_excel[0][0])
archivo2 = os.path.join(script_dir, archivos_excel[1][0])
df1 = pd.read_excel(archivo1)
df2 = pd.read_excel(archivo2)
print(f"   [INFO] Leyendo: {archivos_excel[0][0]} ({archivos_excel[0][1]} registros) y {archivos_excel[1][0]} ({archivos_excel[1][1]} registros)")

print(f"   [OK] formularios.xlsx: {len(df1)} registros, {len(df1.columns)} columnas")
print(f"   [OK] formularios (1).xlsx: {len(df2)} registros, {len(df2.columns)} columnas")

# Verificar que tienen las mismas columnas
assert list(df1.columns) == list(df2.columns), "Las columnas no coinciden entre archivos"
columnas = list(df1.columns)
print(f"   [OK] Columnas: {columnas}")

# ============================================================================
# 2. ANÁLISIS DE DATOS EXISTENTES
# ============================================================================

print("\n2. Analizando datos existentes...")

# Combinar temporalmente para análisis
df_temp = pd.concat([df1, df2], ignore_index=True)

# Extraer valores únicos y distribuciones
valores_unicos = {}
distribuciones = {}

for col in columnas:
    if col == 'id_usuario':
        continue
    
    valores_unicos[col] = df_temp[col].unique().tolist()
    
    if df_temp[col].dtype in ['int64', 'float64']:
        distribuciones[col] = {
            'min': int(df_temp[col].min()),
            'max': int(df_temp[col].max()),
            'mean': float(df_temp[col].mean()),
            'std': float(df_temp[col].std())
        }
    else:
        # Distribución de frecuencias para variables categóricas
        frecuencias = df_temp[col].value_counts().to_dict()
        total = len(df_temp)
        distribuciones[col] = {k: v/total for k, v in frecuencias.items()}

print(f"   [OK] Valores únicos extraídos para {len(valores_unicos)} columnas")

# Identificar IDs duplicados
ids_df1 = set(df1['id_usuario'].astype(str))
ids_df2 = set(df2['id_usuario'].astype(str))
duplicados = ids_df1 & ids_df2
print(f"   [OK] IDs duplicados encontrados: {len(duplicados)}")

# ============================================================================
# 3. MAPEO DE CORRELACIONES LÓGICAS
# ============================================================================

print("\n3. Creando mapeos de correlaciones lógicas...")

# Mapeo: Área de interés -> Sectores laborales coherentes
area_a_sector = {}
if 'Área de interés para formarse' in valores_unicos:
    areas_interes = valores_unicos['Área de interés para formarse']
    sectores = valores_unicos.get('Sector laboral', [])
    
    # Crear mapeos lógicos basados en los datos existentes
    for area in areas_interes:
        # Buscar sectores que aparecen con esta área en los datos
        sectores_coherentes = df_temp[df_temp['Área de interés para formarse'] == area]['Sector laboral'].unique().tolist()
        if sectores_coherentes:
            area_a_sector[area] = sectores_coherentes
        else:
            # Si no hay datos, usar todos los sectores disponibles
            area_a_sector[area] = sectores

# Mapeo: Titulación -> Áreas de estudio coherentes
titulacion_a_area_estudios = {}
if 'Titulación académica' in valores_unicos and 'Área de estudios' in valores_unicos:
    titulaciones = valores_unicos['Titulación académica']
    areas_estudios = valores_unicos['Área de estudios']
    
    for tit in titulaciones:
        areas_coherentes = df_temp[df_temp['Titulación académica'] == tit]['Área de estudios'].unique().tolist()
        if areas_coherentes:
            titulacion_a_area_estudios[tit] = areas_coherentes
        else:
            titulacion_a_area_estudios[tit] = areas_estudios

# Mapeo: País -> Ciudades coherentes
pais_a_ciudad = {}
if 'País' in valores_unicos and 'Ciudad' in valores_unicos:
    paises = valores_unicos['País']
    ciudades = valores_unicos['Ciudad']
    
    for pais in paises:
        ciudades_coherentes = df_temp[df_temp['País'] == pais]['Ciudad'].unique().tolist()
        if ciudades_coherentes:
            pais_a_ciudad[pais] = ciudades_coherentes
        else:
            pais_a_ciudad[pais] = ciudades

# Mapeo: Experiencia -> Motivo de formación (lógica)
# Personas con más experiencia tienden a buscar "Escalar", estudiantes buscan "Búsqueda de empleo"
experiencia_a_motivo = {}
motivos = valores_unicos.get('Motivo de la formación', [])

print(f"   [OK] Mapeos de correlaciones creados")

# ============================================================================
# 4. UNIFICACIÓN DE IDs
# ============================================================================

print("\n4. Unificando IDs...")

# Renumerar IDs del primer dataframe
df1_unificado = df1.copy()
df1_unificado['id_usuario'] = [f"U{i+1:04d}" for i in range(len(df1))]

# Renumerar IDs del segundo dataframe (continuando desde donde terminó el primero)
df2_unificado = df2.copy()
df2_unificado['id_usuario'] = [f"U{i+len(df1)+1:04d}" for i in range(len(df2))]

# Combinar los 200 registros unificados
df_existente = pd.concat([df1_unificado, df2_unificado], ignore_index=True)

# Ajustar edades de registros existentes al rango 18-50 y redistribuir según objetivo
print("\n4.1. Ajustando edades de registros existentes al rango 18-50...")
edades_ajustadas = 0
# Redistribuir todos los registros existentes según la distribución objetivo
n_existentes = len(df_existente)
n_18_30 = int(n_existentes * 0.60)
n_30_40 = int(n_existentes * 0.30)
n_40_50 = n_existentes - n_18_30 - n_30_40

# Generar edades según distribución
edades_nuevas = []
edades_nuevas.extend([random.randint(18, 30) for _ in range(n_18_30)])
edades_nuevas.extend([random.randint(30, 40) for _ in range(n_30_40)])
edades_nuevas.extend([random.randint(40, 50) for _ in range(n_40_50)])
random.shuffle(edades_nuevas)

for idx, row in df_existente.iterrows():
    nueva_edad = edades_nuevas[idx]
    edad_original = row['Edad']
    
    if edad_original != nueva_edad:
        df_existente.at[idx, 'Edad'] = nueva_edad
        edades_ajustadas += 1
    
    # Ajustar experiencia si es incoherente con la nueva edad
    edad_actual = df_existente.at[idx, 'Edad']
    exp_actual = df_existente.at[idx, 'Experiencia laboral']
    max_exp_permitida = edad_actual - 18
    if exp_actual > max_exp_permitida:
        df_existente.at[idx, 'Experiencia laboral'] = max(0, max_exp_permitida)
        edades_ajustadas += 1

if edades_ajustadas > 0:
    print(f"   [OK] Ajustadas {edades_ajustadas} edades/experiencias en registros existentes")

print(f"   [OK] IDs unificados: U0001 a U{len(df_existente):04d}")
print(f"   [OK] Total registros existentes: {len(df_existente)}")

# ============================================================================
# 5. GENERACIÓN DE 500 REGISTROS NUEVOS
# ============================================================================

print("\n5. Generando 500 registros nuevos con correlaciones lógicas...")

def generar_edad_coherente():
    """Genera edad realista (18-50 años) con distribución específica"""
    # Distribución: 60% 18-30, 30% 30-40, 10% 40-50
    weights = [0.60, 0.30, 0.10]
    rangos = [(18, 30), (30, 40), (40, 50)]
    rango = random.choices(rangos, weights=weights)[0]
    # Generar edad uniformemente dentro del rango seleccionado
    return random.randint(rango[0], rango[1])

def generar_experiencia_coherente(edad):
    """Genera experiencia laboral coherente con la edad (rango 18-50)"""
    # Experiencia máxima = edad - 18 (asumiendo que se empieza a trabajar a los 18)
    max_exp = max(0, edad - 18)
    
    # Si es muy joven (18-22), probablemente estudiante (0-2 años exp)
    if edad <= 22:
        exp_max = min(2, max_exp)
        return random.randint(0, exp_max)
    # Si es joven (23-30), experiencia moderada (0-12 años, pero típicamente 1-8)
    elif edad <= 30:
        # La mayoría tiene 1-8 años, algunos tienen 0 (estudiantes), pocos tienen 9-12
        if random.random() < 0.1:  # 10% estudiantes sin experiencia
            return 0
        elif random.random() < 0.8:  # 80% experiencia típica
            return random.randint(1, min(8, max_exp))
        else:  # 10% con más experiencia (solo si max_exp >= 9)
            if max_exp >= 9:
                return random.randint(9, min(12, max_exp))
            else:
                return random.randint(1, max_exp)
    # Si es adulto joven (31-40), experiencia considerable (3-22 años)
    elif edad <= 40:
        exp_min = max(2, max_exp - 18)  # Mínimo 2 años, pero coherente con edad
        exp_max = max_exp
        if exp_min > exp_max:
            exp_min = max(0, exp_max - 5)  # Ajustar si el mínimo es mayor que el máximo
        return random.randint(exp_min, exp_max)
    # Si es adulto (41-50), experiencia alta (5-32 años)
    else:
        exp_min = max(5, max_exp - 20)  # Mínimo 5 años, pero coherente con edad
        exp_max = max_exp
        if exp_min > exp_max:
            exp_min = max(0, exp_max - 10)  # Ajustar si el mínimo es mayor que el máximo
        return random.randint(exp_min, exp_max)

def generar_motivo_por_experiencia(experiencia):
    """Genera motivo de formación coherente con experiencia"""
    if experiencia == 0:
        return random.choices(
            motivos,
            weights=[0.4, 0.3, 0.1, 0.1, 0.1] if len(motivos) >= 5 else [1/len(motivos)]*len(motivos)
        )[0]
    elif experiencia <= 3:
        # Búsqueda de empleo o ampliar conocimiento
        return random.choice(motivos)
    elif experiencia <= 8:
        # Cambio de trabajo o escalar
        return random.choice(motivos)
    else:
        # Escalar en el trabajo o ampliar conocimiento
        return random.choice(motivos)

def generar_sector_por_area(area_interes):
    """Genera sector laboral coherente con área de interés"""
    if area_interes in area_a_sector:
        return random.choice(area_a_sector[area_interes])
    else:
        return random.choice(valores_unicos.get('Sector laboral', ['Tecnología']))

def generar_area_estudios_por_titulacion(titulacion):
    """Genera área de estudios coherente con titulación"""
    if titulacion in titulacion_a_area_estudios:
        return random.choice(titulacion_a_area_estudios[titulacion])
    else:
        return random.choice(valores_unicos.get('Área de estudios', ['Ingeniería']))

def generar_ciudad_por_pais(pais):
    """Genera ciudad coherente con país"""
    if pais in pais_a_ciudad:
        return random.choice(pais_a_ciudad[pais])
    else:
        return random.choice(valores_unicos.get('Ciudad', ['Madrid']))

# Generar los 500 registros nuevos
nuevos_registros = []
inicio_id = len(df_existente) + 1

for i in range(500):
    # Generar edad y experiencia de forma coherente
    edad = generar_edad_coherente()
    experiencia = generar_experiencia_coherente(edad)
    
    # Asegurar coherencia: si la experiencia es mayor que lo permitido, ajustar
    if experiencia > (edad - 18):
        experiencia = max(0, edad - 18)
    
    # Generar otras variables con distribuciones realistas
    genero = random.choices(
        valores_unicos['Género'],
        weights=[distribuciones['Género'].get(g, 0.25) for g in valores_unicos['Género']]
    )[0]
    
    pais = random.choices(
        valores_unicos['País'],
        weights=[distribuciones['País'].get(p, 1/len(valores_unicos['País'])) for p in valores_unicos['País']]
    )[0]
    
    ciudad = generar_ciudad_por_pais(pais)
    
    area_interes = random.choices(
        valores_unicos['Área de interés para formarse'],
        weights=[distribuciones['Área de interés para formarse'].get(a, 1/len(valores_unicos['Área de interés para formarse'])) for a in valores_unicos['Área de interés para formarse']]
    )[0]
    
    sector_laboral = generar_sector_por_area(area_interes)
    
    titulacion = random.choices(
        valores_unicos['Titulación académica'],
        weights=[distribuciones['Titulación académica'].get(t, 1/len(valores_unicos['Titulación académica'])) for t in valores_unicos['Titulación académica']]
    )[0]
    
    area_estudios = generar_area_estudios_por_titulacion(titulacion)
    
    motivo = generar_motivo_por_experiencia(experiencia)
    
    # Generar ID
    id_usuario = f"U{inicio_id + i:04d}"
    
    nuevo_registro = {
        'id_usuario': id_usuario,
        'Ciudad': ciudad,
        'País': pais,
        'Edad': edad,
        'Género': genero,
        'Área de interés para formarse': area_interes,
        'Titulación académica': titulacion,
        'Área de estudios': area_estudios,
        'Experiencia laboral': experiencia,
        'Sector laboral': sector_laboral,
        'Motivo de la formación': motivo
    }
    
    nuevos_registros.append(nuevo_registro)

df_nuevos = pd.DataFrame(nuevos_registros)
print(f"   [OK] Generados {len(df_nuevos)} registros nuevos")

# ============================================================================
# 6. VALIDACIÓN DE COHERENCIA
# ============================================================================

print("\n6. Validando coherencia lógica de todos los registros...")

def validar_coherencia(df):
    """Valida y corrige inconsistencias lógicas"""
    inconsistencias = []
    
    for idx, row in df.iterrows():
        edad = row['Edad']
        experiencia = row['Experiencia laboral']
        
        # Validar: edad debe estar en rango 18-50
        if edad < 18:
            df.at[idx, 'Edad'] = 18
            inconsistencias.append(f"Fila {idx}: Ajustada edad mínima a 18")
        elif edad > 50:
            # Redistribuir según distribución objetivo
            if random.random() < 0.60:
                nueva_edad = random.randint(18, 30)
            elif random.random() < 0.90:
                nueva_edad = random.randint(30, 40)
            else:
                nueva_edad = random.randint(40, 50)
            df.at[idx, 'Edad'] = nueva_edad
            inconsistencias.append(f"Fila {idx}: Ajustada edad ({edad} -> {nueva_edad})")
            edad = nueva_edad  # Actualizar para validación de experiencia
        
        # Validar: experiencia no puede ser mayor que edad - 18
        if experiencia > (edad - 18):
            df.at[idx, 'Experiencia laboral'] = max(0, edad - 18)
            inconsistencias.append(f"Fila {idx}: Ajustada experiencia ({experiencia} -> {df.at[idx, 'Experiencia laboral']}) para edad {edad}")
        
        # Validar: ciudad debe pertenecer al país (si tenemos el mapeo)
        if row['País'] in pais_a_ciudad:
            if row['Ciudad'] not in pais_a_ciudad[row['País']]:
                # Corregir asignando una ciudad válida del país
                df.at[idx, 'Ciudad'] = random.choice(pais_a_ciudad[row['País']])
                inconsistencias.append(f"Fila {idx}: Corregida ciudad para país {row['País']}")
    
    return inconsistencias

# Validar registros existentes
inconsistencias_existentes = validar_coherencia(df_existente)
if inconsistencias_existentes:
    print(f"   [INFO] Corregidas {len(inconsistencias_existentes)} inconsistencias en registros existentes")

# Validar registros nuevos
inconsistencias_nuevos = validar_coherencia(df_nuevos)
if inconsistencias_nuevos:
    print(f"   [INFO] Corregidas {len(inconsistencias_nuevos)} inconsistencias en registros nuevos")

print(f"   [OK] Validación completada")

# ============================================================================
# 7. COMBINACIÓN FINAL
# ============================================================================

print("\n7. Combinando todos los registros...")

df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)

# Verificar que todos los IDs sean únicos
ids_unicos = df_final['id_usuario'].nunique()
total_registros = len(df_final)
assert ids_unicos == total_registros, f"Error: Hay IDs duplicados ({ids_unicos} únicos de {total_registros} totales)"

# Ordenar por ID
df_final = df_final.sort_values('id_usuario').reset_index(drop=True)

print(f"   [OK] Total registros: {len(df_final)}")
print(f"   [OK] IDs únicos: {df_final['id_usuario'].nunique()}")
print(f"   [OK] Rango de IDs: {df_final['id_usuario'].min()} a {df_final['id_usuario'].max()}")

# ============================================================================
# 8. GUARDADO
# ============================================================================

print("\n8. Guardando archivo unificado...")

archivo_salida = os.path.join(script_dir, 'formularios_unificado.xlsx')
df_final.to_excel(archivo_salida, index=False, engine='openpyxl')

print(f"   [OK] Archivo guardado: {archivo_salida}")

# ============================================================================
# 9. RESUMEN FINAL
# ============================================================================

print("\n" + "=" * 70)
print("RESUMEN FINAL")
print("=" * 70)

print(f"\nTotal de registros: {len(df_final)}")
print(f"  - Registros existentes (unificados): {len(df_existente)}")
print(f"  - Registros nuevos generados: {len(df_nuevos)}")

print(f"\nDistribución por columnas:")
for col in ['Género', 'País', 'Área de interés para formarse', 'Titulación académica']:
    if col in df_final.columns:
        print(f"\n{col}:")
        distrib = df_final[col].value_counts().head(5)
        for valor, count in distrib.items():
            print(f"  - {valor}: {count} ({count/len(df_final)*100:.1f}%)")

print(f"\nEstadísticas numéricas:")
print(f"  - Edad: {df_final['Edad'].min()}-{df_final['Edad'].max()} años (media: {df_final['Edad'].mean():.1f})")
print(f"  - Experiencia laboral: {df_final['Experiencia laboral'].min()}-{df_final['Experiencia laboral'].max()} años (media: {df_final['Experiencia laboral'].mean():.1f})")

print(f"\nDistribución de edades:")
edad_18_30 = len(df_final[(df_final['Edad'] >= 18) & (df_final['Edad'] <= 30)])
edad_30_40 = len(df_final[(df_final['Edad'] > 30) & (df_final['Edad'] <= 40)])
edad_40_50 = len(df_final[(df_final['Edad'] > 40) & (df_final['Edad'] <= 50)])
total = len(df_final)
print(f"  - 18-30 años: {edad_18_30} ({edad_18_30/total*100:.1f}%) - Objetivo: 60%")
print(f"  - 30-40 años: {edad_30_40} ({edad_30_40/total*100:.1f}%) - Objetivo: 30%")
print(f"  - 40-50 años: {edad_40_50} ({edad_40_50/total*100:.1f}%) - Objetivo: 10%")

print(f"\n[OK] Proceso completado exitosamente!")
print("=" * 70)

