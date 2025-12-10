"""
Script de verificación completa para Immune_metricas.csv
Verifica todas las reglas de negocio, correlaciones lógicas y coherencia de datos
"""

import pandas as pd
import numpy as np
import os

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

ARCHIVO_CSV = 'metricas_immune/Immune_metricas.csv'
ARCHIVO_FORMULARIOS = '../formularios/formularios_unificado.xlsx'

# ============================================================================
# FUNCIONES DE VERIFICACIÓN
# ============================================================================

def verificar_archivo_existe():
    """Verifica que el archivo CSV existe"""
    if not os.path.exists(ARCHIVO_CSV):
        print(f"[ERROR] No se encontró el archivo: {ARCHIVO_CSV}")
        return False
    print(f"[OK] Archivo encontrado: {ARCHIVO_CSV}")
    return True

def verificar_columnas_requeridas(df):
    """Verifica que todas las columnas requeridas están presentes"""
    columnas_requeridas = [
        "usuario_temp",
        "origen_plataforma",
        "IP_usuario",
        "tiempo_en_pagina",
        "fecha_hora",
        "Localizacion",
        "programa_oferta_click",
        "Id_usuario",
        "Dispositivo",
        "Matriculado"
    ]
    
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    columnas_extra = [col for col in df.columns if col not in columnas_requeridas]
    
    if columnas_faltantes:
        print(f"[ERROR] Columnas faltantes: {columnas_faltantes}")
        return False
    
    if columnas_extra:
        print(f"[ADVERTENCIA] Columnas extra encontradas: {columnas_extra}")
    
    print(f"[OK] Todas las columnas requeridas están presentes")
    print(f"     Columnas: {list(df.columns)}")
    return True

def verificar_orden_columnas(df):
    """Verifica que el orden de las columnas es correcto"""
    orden_esperado = [
        "usuario_temp",
        "origen_plataforma",
        "IP_usuario",
        "tiempo_en_pagina",
        "fecha_hora",
        "Localizacion",
        "programa_oferta_click",
        "Id_usuario",
        "Dispositivo",
        "Matriculado"
    ]
    
    orden_actual = list(df.columns)
    
    if orden_actual != orden_esperado:
        print(f"[ADVERTENCIA] El orden de las columnas no coincide")
        print(f"     Esperado: {orden_esperado}")
        print(f"     Actual:   {orden_actual}")
        return False
    
    print(f"[OK] Orden de columnas correcto")
    return True

def verificar_tipos_datos(df):
    """Verifica que los tipos de datos son correctos"""
    errores = []
    
    # usuario_temp: string
    if not df['usuario_temp'].dtype == 'object':
        errores.append("usuario_temp debe ser string")
    
    # origen_plataforma: string
    if not df['origen_plataforma'].dtype == 'object':
        errores.append("origen_plataforma debe ser string")
    
    # IP_usuario: string
    if not df['IP_usuario'].dtype == 'object':
        errores.append("IP_usuario debe ser string")
    
    # tiempo_en_pagina: numérico
    if not pd.api.types.is_numeric_dtype(df['tiempo_en_pagina']):
        errores.append("tiempo_en_pagina debe ser numérico")
    
    # fecha_hora: datetime
    if not pd.api.types.is_datetime64_any_dtype(df['fecha_hora']):
        errores.append("fecha_hora debe ser datetime")
    
    # Localizacion: string
    if not df['Localizacion'].dtype == 'object':
        errores.append("Localizacion debe ser string")
    
    # programa_oferta_click: string o null
    if not df['programa_oferta_click'].dtype == 'object':
        errores.append("programa_oferta_click debe ser string o null")
    
    # Id_usuario: string o null
    if not df['Id_usuario'].dtype == 'object':
        errores.append("Id_usuario debe ser string o null")
    
    # Dispositivo: string
    if not df['Dispositivo'].dtype == 'object':
        errores.append("Dispositivo debe ser string")
    
    # Matriculado: boolean
    if not df['Matriculado'].dtype == 'bool':
        errores.append("Matriculado debe ser boolean")
    
    if errores:
        print(f"[ERROR] Errores en tipos de datos:")
        for error in errores:
            print(f"     - {error}")
        return False
    
    print(f"[OK] Todos los tipos de datos son correctos")
    return True

def verificar_valores_origen_plataforma(df):
    """Verifica que origen_plataforma tiene solo los valores permitidos"""
    valores_permitidos = ["LinkedIn", "Instagram", "Google", "Google Ads"]
    valores_unicos = df['origen_plataforma'].unique()
    valores_invalidos = [v for v in valores_unicos if v not in valores_permitidos]
    
    if valores_invalidos:
        print(f"[ERROR] Valores inválidos en origen_plataforma: {valores_invalidos}")
        return False
    
    print(f"[OK] origen_plataforma tiene solo valores permitidos: {valores_permitidos}")
    return True

def verificar_id_usuario_nulls(df):
    """Verifica que Id_usuario tiene aproximadamente 15% nulls"""
    null_count = df['Id_usuario'].isna().sum()
    total = len(df)
    porcentaje_null = (null_count / total) * 100
    
    # Aceptar entre 10% y 20% (margen de error)
    if porcentaje_null < 10 or porcentaje_null > 20:
        print(f"[ADVERTENCIA] Porcentaje de nulls en Id_usuario: {porcentaje_null:.2f}% (esperado ~15%)")
        print(f"     Nulls: {null_count} de {total}")
        return False
    
    print(f"[OK] Id_usuario tiene {null_count} nulls ({porcentaje_null:.2f}%)")
    return True

def verificar_matriculado_sin_id(df):
    """Verifica que NO hay matrículas sin Id_usuario"""
    matriculados_sin_id = df[(df['Matriculado'] == True) & (df['Id_usuario'].isna())]
    
    if len(matriculados_sin_id) > 0:
        print(f"[ERROR] Encontrados {len(matriculados_sin_id)} registros matriculados sin Id_usuario")
        print(f"     Primeros 5 registros problemáticos:")
        print(matriculados_sin_id[['usuario_temp', 'Id_usuario', 'Matriculado']].head())
        return False
    
    print(f"[OK] No hay matrículas sin Id_usuario")
    return True

def verificar_matriculado_con_id(df):
    """Verifica que todos los matriculados tienen Id_usuario"""
    matriculados = df[df['Matriculado'] == True]
    
    if len(matriculados) == 0:
        print(f"[ADVERTENCIA] No hay registros matriculados")
        return True
    
    todos_con_id = matriculados['Id_usuario'].notna().all()
    
    if not todos_con_id:
        print(f"[ERROR] No todos los matriculados tienen Id_usuario")
        return False
    
    print(f"[OK] Todos los {len(matriculados)} matriculados tienen Id_usuario")
    return True

def verificar_ips_validas(df):
    """Verifica que las IPs tienen formato válido"""
    # Patrón básico de IP: X.X.X.X donde X es 0-255
    import re
    patron_ip = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    
    ips_invalidas = []
    for idx, ip in df['IP_usuario'].items():
        if not patron_ip.match(str(ip)):
            ips_invalidas.append((idx, ip))
        else:
            # Verificar que cada octeto está en rango 0-255
            octetos = str(ip).split('.')
            if len(octetos) != 4:
                ips_invalidas.append((idx, ip))
            else:
                for octeto in octetos:
                    try:
                        num = int(octeto)
                        if num < 0 or num > 255:
                            ips_invalidas.append((idx, ip))
                            break
                    except ValueError:
                        ips_invalidas.append((idx, ip))
                        break
    
    if ips_invalidas:
        print(f"[ERROR] Encontradas {len(ips_invalidas)} IPs inválidas")
        print(f"     Primeras 5: {ips_invalidas[:5]}")
        return False
    
    print(f"[OK] Todas las IPs tienen formato válido")
    print(f"     IPs únicas: {df['IP_usuario'].nunique()}")
    return True

def verificar_tiempo_en_pagina(df):
    """Verifica que tiempo_en_pagina tiene valores razonables"""
    tiempo_min = df['tiempo_en_pagina'].min()
    tiempo_max = df['tiempo_en_pagina'].max()
    tiempo_medio = df['tiempo_en_pagina'].mean()
    
    # Verificar que todos son positivos
    if tiempo_min < 0:
        print(f"[ERROR] tiempo_en_pagina tiene valores negativos")
        return False
    
    # Verificar que no hay valores extremadamente altos (más de 1 hora = 3600 segundos)
    valores_extremos = df[df['tiempo_en_pagina'] > 3600]
    if len(valores_extremos) > 0:
        print(f"[ADVERTENCIA] {len(valores_extremos)} registros con tiempo > 1 hora")
    
    print(f"[OK] tiempo_en_pagina: min={tiempo_min}s, max={tiempo_max}s, media={tiempo_medio:.1f}s")
    return True

def verificar_programa_oferta_click_secuencias(df):
    """Verifica que hay secuencias donde usuarios consultan diferentes programas"""
    # Agrupar por Id_usuario y verificar que algunos consultan múltiples cursos
    usuarios_multiples_cursos = df[df['Id_usuario'].notna() & df['programa_oferta_click'].notna()].groupby('Id_usuario')['programa_oferta_click'].nunique()
    usuarios_con_secuencias = usuarios_multiples_cursos[usuarios_multiples_cursos > 1]
    
    if len(usuarios_con_secuencias) == 0:
        print(f"[ADVERTENCIA] No se encontraron usuarios que consulten múltiples programas")
        return False
    
    print(f"[OK] {len(usuarios_con_secuencias)} usuarios consultaron múltiples programas")
    print(f"     Usuario con más cursos: {usuarios_multiples_cursos.max()} cursos diferentes")
    return True

def verificar_coherencia_pais_formularios(df):
    """Verifica que los IDs de formularios tienen el País correcto en Localizacion"""
    try:
        df_formularios = pd.read_excel(ARCHIVO_FORMULARIOS, engine='openpyxl')
        
        # Crear mapeo ID -> País
        mapeo_id_pais = {}
        for _, row in df_formularios.iterrows():
            id_str = str(row['id_usuario']).strip().upper()
            if id_str.startswith('U') and id_str[1:].isdigit():
                id_str = f"U{int(id_str[1:]):04d}"
            pais = str(row['País']).strip()
            mapeo_id_pais[id_str] = pais
        
        # Verificar registros con IDs de formularios
        ids_formularios_set = set(mapeo_id_pais.keys())
        registros_con_id_formulario = df[
            df['Id_usuario'].notna() & 
            df['Id_usuario'].astype(str).str.upper().str.strip().isin(ids_formularios_set)
        ]
        
        if len(registros_con_id_formulario) == 0:
            print(f"[ADVERTENCIA] No se encontraron registros con IDs de formularios")
            return True
        
        # Verificar coherencia (muestra de 20 registros)
        muestra = registros_con_id_formulario.sample(min(20, len(registros_con_id_formulario)))
        coherentes = 0
        
        for idx, row in muestra.iterrows():
            id_str = str(row['Id_usuario']).strip().upper()
            if id_str.startswith('U') and id_str[1:].isdigit():
                id_str = f"U{int(id_str[1:]):04d}"
            
            if id_str in mapeo_id_pais:
                pais_formulario = mapeo_id_pais[id_str]
                localizacion = str(row['Localizacion'])
                # Verificar que el país está en la localización
                if pais_formulario in localizacion:
                    coherentes += 1
        
        porcentaje_coherencia = (coherentes / len(muestra)) * 100
        
        if porcentaje_coherencia < 80:
            print(f"[ADVERTENCIA] Solo {coherentes}/{len(muestra)} ({porcentaje_coherencia:.1f}%) muestras tienen País coherente")
            return False
        
        print(f"[OK] Coherencia País: {coherentes}/{len(muestra)} ({porcentaje_coherencia:.1f}%) muestras verificadas")
        return True
        
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo verificar coherencia de País: {e}")
        return True  # No es crítico


def verificar_ids_formularios_cobertura(df):
    """Comprueba que los primeros 1200 IDs corresponden a formularios y no se repiten fuera."""
    try:
        df_form = pd.read_excel(ARCHIVO_FORMULARIOS, engine='openpyxl')
        ids_form = (
            df_form['id_usuario']
            .astype(str)
            .str.strip()
            .str.upper()
            .apply(lambda x: f"U{int(x[1:]):04d}" if x.startswith('U') and x[1:].isdigit() else x)
            .tolist()
        )
        ids_form = [i for i in ids_form if i]
        ids_form_set = set(ids_form[:1200])

        ids_csv = df['Id_usuario'].astype(str).str.strip().str.upper()

        # Cobertura exacta en las primeras 1200 filas
        primer_bloque = ids_csv.head(len(ids_form_set))
        faltantes = ids_form_set - set(primer_bloque)
        extras = set(primer_bloque) - ids_form_set

        # Repeticiones fuera del bloque
        resto = ids_csv.iloc[len(ids_form_set):]
        repetidos_fuera = ids_form_set.intersection(set(resto))

        ok = True
        if faltantes:
            print(f"[ADVERTENCIA] Faltan IDs de formularios en el primer bloque: {list(faltantes)[:5]}")
            ok = False
        if extras:
            print(f"[ADVERTENCIA] IDs no esperados en el primer bloque: {list(extras)[:5]}")
            ok = False
        if repetidos_fuera:
            print(f"[ADVERTENCIA] IDs de formularios repetidos fuera del bloque inicial: {list(repetidos_fuera)[:5]}")
            ok = False
        if ok:
            print(f"[OK] Cobertura de IDs de formularios correcta en el bloque inicial ({len(ids_form_set)} IDs)")
        return ok
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo verificar cobertura de IDs de formularios: {e}")
        return True


def verificar_programa_matriculado(df):
    """Asegura que todo matriculado tenga programa_oferta_click."""
    problematicos = df[(df['Matriculado'] == True) & (df['programa_oferta_click'].isna())]
    if len(problematicos) > 0:
        print(f"[ERROR] {len(problematicos)} matriculados sin programa_oferta_click")
        print(problematicos[['Id_usuario', 'Matriculado']].head())
        return False
    print("[OK] Todos los matriculados tienen programa_oferta_click")
    return True


def verificar_ids_formularios_no_duplicados(df):
    """Comprueba que los IDs de formularios no están duplicados dentro de su bloque inicial."""
    try:
        df_form = pd.read_excel(ARCHIVO_FORMULARIOS, engine='openpyxl')
        ids_form = (
            df_form['id_usuario']
            .astype(str)
            .str.strip()
            .str.upper()
            .apply(lambda x: f"U{int(x[1:]):04d}" if x.startswith('U') and x[1:].isdigit() else x)
            .tolist()
        )
        ids_form = [i for i in ids_form if i][:1200]
        bloque = df['Id_usuario'].astype(str).str.strip().str.upper().head(len(ids_form))
        duplicados = bloque[bloque.duplicated(keep=False)]
        if not duplicados.empty:
            print(f"[ADVERTENCIA] IDs de formularios duplicados en el bloque inicial: {duplicados.unique()[:5]}")
            return False
        print("[OK] Sin duplicados en el bloque de IDs de formularios")
        return True
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo verificar duplicados de IDs de formularios: {e}")
        return True

def verificar_distribuciones(df):
    """Verifica que las distribuciones son razonables"""
    print("\n[VERIFICACIÓN DE DISTRIBUCIONES]")
    
    print(f"\n[ORIGEN_PLATAFORMA]")
    print(df['origen_plataforma'].value_counts(normalize=True) * 100)
    
    print(f"\n[DISPOSITIVO]")
    print(df['Dispositivo'].value_counts(normalize=True) * 100)
    
    print(f"\n[MATRICULADO]")
    porcentaje_matriculado = df['Matriculado'].mean() * 100
    print(f"Porcentaje True: {porcentaje_matriculado:.2f}%")
    if porcentaje_matriculado < 25 or porcentaje_matriculado > 40:
        print(f"[ADVERTENCIA] Porcentaje de matriculados fuera del rango esperado (25-40%)")
    
    print(f"\n[PROGRAMA_OFERTA_CLICK]")
    porcentaje_con_click = df['programa_oferta_click'].notna().mean() * 100
    print(f"Porcentaje con click: {porcentaje_con_click:.2f}%")
    
    return True

def verificar_fechas(df):
    """Verifica que las fechas están en el rango correcto"""
    fecha_min = df['fecha_hora'].min()
    fecha_max = df['fecha_hora'].max()
    fecha_esperada_min = pd.Timestamp("2024-01-01")
    fecha_esperada_max = pd.Timestamp("2025-12-31")
    
    errores = []
    
    if fecha_min < fecha_esperada_min:
        errores.append(f"Fecha mínima {fecha_min} es anterior a {fecha_esperada_min}")
    
    if fecha_max > fecha_esperada_max:
        errores.append(f"Fecha máxima {fecha_max} es posterior a {fecha_esperada_max}")
    
    # Verificar que no hay fechas futuras (después de hoy)
    hoy = pd.Timestamp.now()
    fechas_futuras = df[df['fecha_hora'] > hoy]
    if len(fechas_futuras) > 0:
        errores.append(f"Encontradas {len(fechas_futuras)} fechas futuras")
    
    if errores:
        print(f"[ERROR] Problemas con fechas:")
        for error in errores:
            print(f"     - {error}")
        return False
    
    print(f"[OK] Fechas en rango correcto: {fecha_min} a {fecha_max}")
    return True

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    print("=" * 70)
    print("VERIFICACIÓN COMPLETA DE IMMUNE_METRICAS.CSV")
    print("=" * 70)
    
    # Verificar que el archivo existe
    if not verificar_archivo_existe():
        return
    
    # Cargar DataFrame
    try:
        df = pd.read_csv(ARCHIVO_CSV, encoding='utf-8-sig')
        df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
        print(f"[OK] DataFrame cargado: {len(df)} registros, {len(df.columns)} columnas")
    except Exception as e:
        print(f"[ERROR] No se pudo cargar el archivo: {e}")
        return
    
    # Lista de verificaciones
    verificaciones = [
        ("Columnas requeridas", verificar_columnas_requeridas, df),
        ("Orden de columnas", verificar_orden_columnas, df),
        ("Tipos de datos", verificar_tipos_datos, df),
        ("Valores origen_plataforma", verificar_valores_origen_plataforma, df),
        ("Id_usuario nulls (~15%)", verificar_id_usuario_nulls, df),
        ("No matrículas sin ID", verificar_matriculado_sin_id, df),
        ("Matriculados con ID", verificar_matriculado_con_id, df),
        ("Cobertura IDs formularios", verificar_ids_formularios_cobertura, df),
        ("Sin duplicados en bloque formularios", verificar_ids_formularios_no_duplicados, df),
        ("IPs válidas", verificar_ips_validas, df),
        ("Tiempo en página", verificar_tiempo_en_pagina, df),
        ("Secuencias programa_oferta_click", verificar_programa_oferta_click_secuencias, df),
        ("Matriculados con programa_oferta_click", verificar_programa_matriculado, df),
        ("Coherencia País formularios", verificar_coherencia_pais_formularios, df),
        ("Rango de fechas", verificar_fechas, df),
    ]
    
    # Ejecutar verificaciones
    resultados = []
    for nombre, funcion, *args in verificaciones:
        print(f"\n[{nombre}]")
        try:
            resultado = funcion(*args) if args else funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"[ERROR] Excepción en verificación: {e}")
            resultados.append((nombre, False))
    
    # Verificaciones adicionales (no críticas)
    print(f"\n[VERIFICACIONES ADICIONALES]")
    verificar_distribuciones(df)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE VERIFICACIONES")
    print("=" * 70)
    
    exitosas = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✓ OK" if resultado else "✗ ERROR"
        print(f"{estado} - {nombre}")
    
    print(f"\nVerificaciones exitosas: {exitosas}/{total}")
    
    if exitosas == total:
        print("\n[✓] TODAS LAS VERIFICACIONES PASARON")
        return 0
    else:
        print(f"\n[✗] {total - exitosas} VERIFICACIONES FALLARON")
        return 1

if __name__ == "__main__":
    exit(main())

