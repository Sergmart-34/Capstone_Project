import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import unicodedata

# Configuración de semilla para reproducibilidad
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
rng = np.random.default_rng(RANDOM_SEED)

# ============================================================================
# 1. UTILIDADES DE CARGA
# ============================================================================

def reparar_texto(texto):
    """
    Intenta corregir mojibake común y normaliza en Unicode NFC.
    """
    if not isinstance(texto, str):
        return texto
    reparado = texto.strip()
    if any(token in reparado for token in ("Ã", "Â")):
        try:
            reparado = reparado.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    reparado = unicodedata.normalize("NFC", reparado)
    return reparado


def limpiar_dataframe(df):
    """
    Aplica reparaciones de encoding a columnas y valores string.
    """
    df = df.copy()
    df.columns = [reparar_texto(col) if isinstance(col, str) else col for col in df.columns]
    object_cols = df.select_dtypes(include=["object"]).columns
    for col in object_cols:
        df[col] = df[col].apply(reparar_texto)
    return df


def normalizar_id_usuario(valor):
    """
    Normaliza cualquier representación de id_usuario al formato U####.
    Devuelve None si no es posible normalizar el valor.
    """
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    valor_str = str(valor).strip().upper()
    if valor_str.startswith("U") and valor_str[1:].isdigit():
        return f"U{int(valor_str[1:]):04d}"
    if valor_str.isdigit():
        return f"U{int(valor_str):04d}"
    return valor_str


def cargar_ids_formularios(ruta_formularios='formularios/formularios_unificado.xlsx'):
    """
    Carga los IDs de usuario y sus países del archivo de formularios unificado
    Retorna: (lista_ids, diccionario_id_pais)
    - lista_ids: lista de IDs disponibles (máximo 700)
    - diccionario_id_pais: mapeo {id_usuario: pais} para coherencia
    """
    try:
        df_formularios = pd.read_excel(ruta_formularios, engine='openpyxl')
        df_formularios = limpiar_dataframe(df_formularios)
        
        # Verificar que existe la columna id_usuario
        if 'id_usuario' not in df_formularios.columns:
            raise ValueError(f"La columna 'id_usuario' no existe en {ruta_formularios}")
        
        # Verificar que existe la columna País
        if 'País' not in df_formularios.columns:
            raise ValueError(f"La columna 'País' no existe en {ruta_formularios}")
        
        # Extraer IDs únicos y normalizarlos
        ids_disponibles = [
            normalizar_id_usuario(id_val)
            for id_val in df_formularios['id_usuario'].unique().tolist()
        ]
        ids_disponibles = [id_val for id_val in ids_disponibles if id_val]
        
        # Crear mapeo ID -> País
        mapeo_id_pais = {}
        for _, row in df_formularios.iterrows():
            id_str = normalizar_id_usuario(row['id_usuario'])
            pais = str(row['País'])
            if id_str:
                mapeo_id_pais[id_str] = pais
        
        print(f"[OK] Cargados {len(ids_disponibles)} IDs de formularios")
        print(f"[OK] Rango: {min(ids_disponibles)} a {max(ids_disponibles)}")
        print(f"[OK] Mapeo ID->País creado para {len(mapeo_id_pais)} registros")
        
        return ids_disponibles, mapeo_id_pais
    
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo: {ruta_formularios}")
        print("[INFO] Generando IDs sintéticos como fallback (U0001-U0700)")
        # Fallback: generar IDs sintéticos del formato esperado
        ids_fallback = [f"U{i+1:04d}" for i in range(700)]
        mapeo_fallback = {id: "España" for id in ids_fallback}  # País por defecto
        return ids_fallback, mapeo_fallback
    except Exception as e:
        print(f"[ERROR] Error al cargar formularios: {e}")
        print("[INFO] Generando IDs sintéticos como fallback (U0001-U0700)")
        ids_fallback = [f"U{i+1:04d}" for i in range(700)]
        mapeo_fallback = {id: "España" for id in ids_fallback}  # País por defecto
        return ids_fallback, mapeo_fallback

def cargar_catalogo_cursos(ruta_cursos='cursos_immune/cursos_immune.xlsx'):
    """
    Carga la lista de ids de curso para garantizar coherencia entre tablas.
    """
    try:
        df_cursos = pd.read_excel(ruta_cursos, engine='openpyxl')
        df_cursos = limpiar_dataframe(df_cursos)
        if 'id_curso' not in df_cursos.columns:
            raise ValueError(f"La columna 'id_curso' no existe en {ruta_cursos}")
        catalogo = (
            df_cursos['id_curso']
            .dropna()
            .astype(str)
            .str.upper()
            .unique()
            .tolist()
        )
        if not catalogo:
            raise ValueError("El catálogo de cursos está vacío")
        return sorted(catalogo)
    except Exception as e:
        print(f"[WARN] No se pudo cargar el catálogo oficial ({e}). Usando fallback.")
        return [f"C{i:04d}" for i in range(1, 21)]

# Cargar recursos base
IDS_FORMULARIOS, MAPEO_ID_PAIS = cargar_ids_formularios()
CATALOGO_CURSOS = cargar_catalogo_cursos()

# ============================================================================
# OPCIONES CATEGÓRICAS
# ============================================================================

# Orígenes/Plataformas (según especificación)
ORIGENES_PLATAFORMA = [
    "LinkedIn", "Instagram", "Google", "Google Ads"
]

# Cursos disponibles para programa_oferta_click (alineados al catálogo oficial)
CURSOS_DISPONIBLES = CATALOGO_CURSOS.copy()

# Ciudades por región
CIUDADES_ESPAÑA = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Málaga", "Zaragoza"]
CIUDADES_LATAM = {
    "México": ["Ciudad de México", "Guadalajara", "Monterrey"],
    "Argentina": ["Buenos Aires", "Córdoba", "Rosario"],
    "Colombia": ["Bogotá", "Medellín", "Cali"],
    "Chile": ["Santiago", "Valparaíso"],
    "Perú": ["Lima", "Arequipa"]
}
CIUDADES_EUROPA = {
    "Portugal": ["Lisboa", "Oporto"],
    "Francia": ["París", "Lyon"],
    "Italia": ["Roma", "Milán"]
}

# Dispositivos normalizados
DISPOSITIVOS = ["mobile", "desktop", "tablet"]

def generar_id_sintetico():
    """Genera un identificador sintético con el formato U####."""
    return f"U{rng.integers(1, 10001):04d}"

def generar_ip_usuario():
    """Genera una IP ficticia para simular diferentes entradas en web."""
    # Generar IPs IPv4 realistas
    return f"{rng.integers(1, 256)}.{rng.integers(0, 256)}.{rng.integers(0, 256)}.{rng.integers(1, 255)}"

# ============================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# ============================================================================

def generar_immune_metricas(n_registros=5000, ids_formularios=None, mapeo_id_pais=None):
    """
    Genera DataFrame sintético con métricas de usuarios de la plataforma Immune
    Incluye correlaciones lógicas críticas entre variables
    Los IDs pueden ser aleatorios, pero aproximadamente 700 coincidirán con formularios
    Cuando un ID coincida con formularios, se usará el País de ese formulario
    """
    
    if ids_formularios is None:
        ids_formularios = IDS_FORMULARIOS
    if mapeo_id_pais is None:
        mapeo_id_pais = MAPEO_ID_PAIS
    
    # ===========================
    # 1. USUARIO_TEMP (ID temporal único)
    # ===========================
    usuario_temp = [f"TEMP_{i:06d}" for i in range(1, n_registros + 1)]
    
    # ===========================
    # 2. FECHA_HORA (Timestamp completo)
    # ===========================
    # Rango restringido al corte real para evitar fechas futuras
    start_date = pd.Timestamp("2024-01-01")
    corte_maximo = pd.Timestamp("2025-11-29")
    hoy = pd.Timestamp(datetime.now().date())
    end_date = min(corte_maximo, hoy)
    if end_date <= start_date:
        end_date = start_date + timedelta(days=1)
    
    # Generar timestamps aleatorios con distribución realista
    # Más actividad en horarios laborales (9-18h) y días laborables
    timestamps = []
    for _ in range(n_registros):
        # Fecha aleatoria
        rango_dias = (end_date - start_date).days + 1
        fecha = start_date + timedelta(
            days=int(rng.integers(0, rango_dias))
        )
        
        # Hora con más probabilidad en horario laboral
        # Probabilidades para 24 horas (0-23) que suman exactamente 1.0
        prob_horas = [0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.03, 0.04, 0.06, 0.07, 0.07, 0.07,
                      0.07, 0.07, 0.07, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.02, 0.01, 0.01]
        # Normalizar para asegurar que sumen exactamente 1.0
        suma_prob = sum(prob_horas)
        prob_horas = [p / suma_prob for p in prob_horas]
        hora = rng.choice(list(range(24)), p=prob_horas)
        minuto = rng.integers(0, 60)
        segundo = rng.integers(0, 60)
        
        timestamp = fecha.replace(hour=hora, minute=minuto, second=segundo)
        timestamps.append(timestamp)
    
    fecha_hora = pd.to_datetime(timestamps)
    
    # ===========================
    # 3. ORIGEN_PLATAFORMA
    # ===========================
    # Distribución realista: LinkedIn, Instagram, Google, Google Ads
    pesos_origen = [0.30, 0.30, 0.20, 0.20]  # LinkedIn, Instagram, Google, Google Ads
    origen_plataforma = rng.choice(ORIGENES_PLATAFORMA, size=n_registros, p=pesos_origen)
    
    # ===========================
    # 4. DISPOSITIVO
    # ===========================
    # Distribución realista con taxonomía cerrada
    pesos_dispositivo = [0.55, 0.25, 0.20]  # mobile, desktop, tablet
    dispositivo = rng.choice(DISPOSITIVOS, size=n_registros, p=pesos_dispositivo)
    
    # ===========================
    # 5. ID_USUARIO (IDs normalizados, con ~15% nulls en los no vinculados)
    # ===========================
    # Los primeros IDs se asignan a TODOS los registros de formularios (hasta 1200)
    # y el resto sigue la lógica previa (nulls ~15% sólo en los no vinculados).
    id_usuario = [None] * n_registros
    
    n_ids_formularios = min(len(ids_formularios), 1200, n_registros)
    if n_ids_formularios > 0:
        ids_form_array = np.array(ids_formularios[:n_ids_formularios])
        id_usuario[:n_ids_formularios] = [
            normalizar_id_usuario(val) or generar_id_sintetico()
            for val in ids_form_array
        ]
    
    restantes = n_registros - n_ids_formularios
    if restantes > 0:
        target_nulls = int(restantes * 0.15)
        indices_disponibles = list(range(n_ids_formularios, n_registros))
        indices_null = set(rng.choice(indices_disponibles, size=target_nulls, replace=False))
        for i in indices_disponibles:
            if i not in indices_null:
                id_usuario[i] = generar_id_sintetico()
    
    # ===========================
    # 6. IP_USUARIO (IPs ficticias para simular diferentes entradas)
    # ===========================
    # Generar IPs que se repiten para el mismo usuario (simulando misma conexión)
    # pero diferentes IPs para diferentes sesiones
    ip_usuario = []
    ip_por_usuario = {}   # Mapeo usuario -> IP (1:1)
    ips_asignadas = set() # Para evitar que dos usuarios compartan IP
    
    for i in range(n_registros):
        usuario_id = id_usuario[i]
        
        if usuario_id:
            # Reutilizar la misma IP para este usuario
            if usuario_id in ip_por_usuario:
                ip_usuario.append(ip_por_usuario[usuario_id])
            else:
                nueva_ip = generar_ip_usuario()
                # Asegurar IP no usada por otro usuario
                while nueva_ip in ips_asignadas:
                    nueva_ip = generar_ip_usuario()
                ip_por_usuario[usuario_id] = nueva_ip
                ips_asignadas.add(nueva_ip)
                ip_usuario.append(nueva_ip)
        else:
            # Visitas sin ID: asignar IP única para no colisionar
            nueva_ip = generar_ip_usuario()
            while nueva_ip in ips_asignadas:
                nueva_ip = generar_ip_usuario()
            ips_asignadas.add(nueva_ip)
            ip_usuario.append(nueva_ip)
    
    # ===========================
    # 7. TIEMPO_EN_PAGINA (en segundos)
    # ===========================
    # Distribución realista: mayoría de visitas cortas, algunas largas
    # Correlacionado con si tiene Id_usuario (más tiempo si tiene ID)
    tiempo_en_pagina = []
    
    for i in range(n_registros):
        tiene_id = id_usuario[i] is not None
        
        if tiene_id:
            # Si tiene ID, tiempo promedio más largo (2-15 minutos)
            tiempo = rng.exponential(300)  # Media de 5 minutos (300 segundos)
            tiempo = np.clip(tiempo, 60, 900)  # Entre 1 y 15 minutos
        else:
            # Si no tiene ID, tiempo más corto (10 segundos - 3 minutos)
            tiempo = rng.exponential(60)  # Media de 1 minuto (60 segundos)
            tiempo = np.clip(tiempo, 10, 180)  # Entre 10 segundos y 3 minutos
        
        tiempo_en_pagina.append(int(tiempo))
    
    # ===========================
    # 8. PROGRAMA_OFERTA_CLICK (asociado a id_curso, con secuencias)
    # ===========================
    # Crear secuencias donde usuarios consulten diferentes programas seguidos
    # Algunos usuarios consultarán múltiples programas en sesiones consecutivas
    cursos_para_click = CURSOS_DISPONIBLES or [f"C{i:04d}" for i in range(1, 21)]
    click_probability = 0.70  # el tagging debe estar presente en la mayoría de los registros
    
    programa_oferta_click = []
    curso_anterior_por_usuario = {}  # Mapeo usuario_id -> último curso consultado
    
    # Ordenar registros por fecha_hora para crear secuencias temporales
    indices_ordenados = np.argsort(fecha_hora)
    
    for idx_ordenado in indices_ordenados:
        usuario_id = id_usuario[idx_ordenado]
        
        if usuario_id and usuario_id in curso_anterior_por_usuario:
            # Este usuario ya consultó un curso antes, usar uno diferente
            curso_previo = curso_anterior_por_usuario[usuario_id]
            cursos_disponibles = [c for c in cursos_para_click if c != curso_previo]
            if cursos_disponibles and rng.random() < 0.80:  # 80% probabilidad de cambiar
                curso = rng.choice(cursos_disponibles)
            else:
                # Mantener el mismo curso o selección aleatoria
                curso = rng.choice(cursos_para_click) if rng.random() < click_probability else None
        else:
            # Primer curso para este usuario o selección aleatoria
            curso = rng.choice(cursos_para_click) if rng.random() < click_probability else None
        
        programa_oferta_click.append((idx_ordenado, curso))
        if usuario_id and curso:
            curso_anterior_por_usuario[usuario_id] = curso
    
    # Reordenar programa_oferta_click al orden original
    programa_oferta_click_ordenado = [None] * n_registros
    for idx_ordenado, curso in programa_oferta_click:
        programa_oferta_click_ordenado[idx_ordenado] = curso
    programa_oferta_click = programa_oferta_click_ordenado
    
    # ===========================
    # 10. LOCALIZACION (Ciudad, País)
    # ===========================
    # Distribución: 60% España, 30% LATAM, 10% Europa
    # PERO: si el ID coincide con formularios, usar el País de ese formulario
    localizaciones = []
    
    for i in range(n_registros):
        # Verificar si el ID está en formularios
        id_str = str(id_usuario[i]) if id_usuario[i] is not None else None
        
        if id_str and id_str in mapeo_id_pais:
            # Si el ID está en formularios, usar su País
            pais_formulario = mapeo_id_pais[id_str]
            
            # Buscar una ciudad apropiada para ese país
            if pais_formulario == "España":
                ciudad = rng.choice(CIUDADES_ESPAÑA)
                localizacion = f"{ciudad}, España"
            elif pais_formulario in CIUDADES_LATAM:
                ciudad = rng.choice(CIUDADES_LATAM[pais_formulario])
                localizacion = f"{ciudad}, {pais_formulario}"
            elif pais_formulario in CIUDADES_EUROPA:
                ciudad = rng.choice(CIUDADES_EUROPA[pais_formulario])
                localizacion = f"{ciudad}, {pais_formulario}"
            else:
                # País no reconocido, usar distribución normal
                region = rng.choice(["ES", "LATAM", "EU"], p=[0.60, 0.30, 0.10])
                if region == "ES":
                    ciudad = rng.choice(CIUDADES_ESPAÑA)
                    localizacion = f"{ciudad}, España"
                elif region == "LATAM":
                    pais = rng.choice(list(CIUDADES_LATAM.keys()))
                    ciudad = rng.choice(CIUDADES_LATAM[pais])
                    localizacion = f"{ciudad}, {pais}"
                else:
                    pais = rng.choice(list(CIUDADES_EUROPA.keys()))
                    ciudad = rng.choice(CIUDADES_EUROPA[pais])
                    localizacion = f"{ciudad}, {pais}"
        else:
            # ID no está en formularios, usar distribución normal
            region = rng.choice(["ES", "LATAM", "EU"], p=[0.60, 0.30, 0.10])
            
            if region == "ES":
                ciudad = rng.choice(CIUDADES_ESPAÑA)
                localizacion = f"{ciudad}, España"
            elif region == "LATAM":
                pais = rng.choice(list(CIUDADES_LATAM.keys()))
                ciudad = rng.choice(CIUDADES_LATAM[pais])
                localizacion = f"{ciudad}, {pais}"
            else:  # EU
                pais = rng.choice(list(CIUDADES_EUROPA.keys()))
                ciudad = rng.choice(CIUDADES_EUROPA[pais])
                localizacion = f"{ciudad}, {pais}"
        
        localizaciones.append(localizacion)
    
    # ===========================
    # 11. MATRICULADO (con correlaciones críticas)
    # ===========================
    # 32% True, pero con correlaciones lógicas:
    # - Matriculado=True → Id_usuario no null (obligatorio)
    # NO puede haber matrícula sin ID de usuario
    matriculado = []
    
    for i in range(n_registros):
        # No puede estar matriculado si no tiene ID
        if id_usuario[i] is None:
            matriculado.append(False)
        else:
            # Probabilidad base: 32%
            prob_base = 0.32
            
            # Ajustar según origen (LinkedIn tiene mejor conversión)
            if origen_plataforma[i] == "LinkedIn":
                prob_base += 0.15
            elif origen_plataforma[i] == "Instagram":
                prob_base += 0.08
            elif origen_plataforma[i] == "Google Ads":
                prob_base += 0.05
            elif origen_plataforma[i] == "Google":
                prob_base += 0.03
            
            # Desktop tiene más probabilidad de matricularse
            if dispositivo[i] == "desktop":
                prob_base += 0.05
            
            prob_base = np.clip(prob_base, 0.0, 0.95)
            matriculado.append(rng.random() < prob_base)
    
    matriculado = np.array(matriculado)
    
    # Ajuste final: asegurar que exactamente 32% estén matriculados
    # pero respetando las correlaciones (solo donde hay id_usuario)
    target_matriculados = int(n_registros * 0.32)
    current_matriculados = np.sum(matriculado)
    
    if current_matriculados < target_matriculados:
        # Añadir más matriculados (solo donde hay id_usuario)
        candidates = [i for i in range(n_registros) 
                     if not matriculado[i] and id_usuario[i] is not None]
        additional = min(target_matriculados - current_matriculados, len(candidates))
        for idx in rng.choice(candidates, size=additional, replace=False):
            matriculado[idx] = True
    elif current_matriculados > target_matriculados:
        # Reducir matriculados aleatoriamente
        candidates = np.where(matriculado)[0]
        to_remove = min(current_matriculados - target_matriculados, len(candidates))
        for idx in rng.choice(candidates, size=to_remove, replace=False):
            matriculado[idx] = False
    
    # Asegurar que toda matrícula tenga programa asociado
    cursos_para_matricula = CURSOS_DISPONIBLES or [f"C{i:04d}" for i in range(1, 21)]
    for idx, esta_matriculado in enumerate(matriculado):
        if esta_matriculado and programa_oferta_click[idx] is None:
            programa_oferta_click[idx] = rng.choice(cursos_para_matricula)
    
    # ===========================
    # 12. CREAR DATAFRAME
    # ===========================
    df = pd.DataFrame({
        "usuario_temp": usuario_temp,
        "origen_plataforma": origen_plataforma,
        "IP_usuario": ip_usuario,
        "tiempo_en_pagina": tiempo_en_pagina,
        "fecha_hora": fecha_hora,
        "Localizacion": localizaciones,
        "programa_oferta_click": programa_oferta_click,
        "Id_usuario": id_usuario,
        "Dispositivo": dispositivo,
        "Matriculado": matriculado
    })
    
    # Post-procesado: IP ↔ Id 1:1 y matrícula única por IP (evitando la primera visita si hay varias)
    # 1) Propagar un solo Id por IP (el primero no nulo encontrado para esa IP)
    ip_to_id = {}
    for ip, grp in df.groupby("IP_usuario"):
        non_null = grp["Id_usuario"].dropna()
        ip_to_id[ip] = non_null.iloc[0] if len(non_null) else None
    df["Id_usuario"] = df["IP_usuario"].map(ip_to_id)

    # Formatear Id_usuario como U00{n}, manteniendo nulos vacíos
    def _fmt_id(val):
        if pd.isna(val) or str(val).strip() == "":
            return pd.NA
        s = str(val).strip().upper()
        digits = None
        if s.startswith("U"):
            rest = "".join(ch for ch in s[1:] if ch.isdigit())
            if rest:
                digits = rest
        if digits is None:
            try:
                digits = str(int(float(s)))
            except Exception:
                return s  # deja el valor tal cual si no se puede interpretar
        return f"U00{int(digits)}"

    df["Id_usuario"] = df["Id_usuario"].apply(_fmt_id)
    
    # 2) Recalcular Matriculado: solo filas con Id no nulo pueden ser True; máximo 1 True por IP
    df["Matriculado"] = False
    mask = df["Id_usuario"].notna()
    for ip, grp in df[mask].groupby("IP_usuario"):
        idxs = grp.index.to_list()
        if len(idxs) == 1:
            choice = idxs[0]
        else:
            # Evitar la primera visita si hay más de una
            choice_pool = idxs[1:] if len(idxs) > 1 else idxs
            choice = rng.choice(choice_pool)
        df.at[choice, "Matriculado"] = True
    
    return df

# ============================================================================
# FUNCIÓN MAIN
# ============================================================================

if __name__ == "__main__":
    print("Generando DataFrame sintético: Immune_metricas...")
    print("-" * 50)
    
    # Generar DataFrame
    df_immune = generar_immune_metricas(n_registros=5000, ids_formularios=IDS_FORMULARIOS, mapeo_id_pais=MAPEO_ID_PAIS)
    print(f"[OK] Generados {len(df_immune)} registros")
    print(f"[OK] Columnas: {list(df_immune.columns)}")
    print(f"[OK] Rango de fechas: {df_immune['fecha_hora'].min()} a {df_immune['fecha_hora'].max()}")
    
    # Verificar cuántos IDs coinciden con formularios
    ids_usados = df_immune['Id_usuario'].dropna().unique()
    ids_en_formularios = set(IDS_FORMULARIOS)
    ids_coincidentes = [str(id) for id in ids_usados if str(id) in ids_en_formularios]
    
    print(f"[OK] IDs únicos usados: {len(ids_usados)}")
    print(f"[OK] IDs que coinciden con formularios: {len(ids_coincidentes)} (de {len(IDS_FORMULARIOS)} disponibles)")
    
    # Guardar como CSV
    print("\nGuardando DataFrame...")
    df_immune.to_csv('Immune_metricas.csv', index=False, encoding='utf-8-sig')
    print("[OK] Immune_metricas.csv guardado")
    
    # Resumen estadístico
    print("\n" + "=" * 50)
    print("RESUMEN ESTADÍSTICO")
    print("=" * 50)
    
    print(f"\nTotal de registros: {len(df_immune)}")
    
    print(f"\n[ID_USUARIO]")
    null_count = df_immune['Id_usuario'].isna().sum()
    print(f"Valores null: {null_count} ({null_count/len(df_immune)*100:.2f}%)")
    print(f"Valores no null: {len(df_immune) - null_count}")
    ids_unicos_usados = df_immune['Id_usuario'].dropna().nunique()
    print(f"IDs únicos usados: {ids_unicos_usados} (de {len(IDS_FORMULARIOS)} disponibles)")
    
    print(f"\n[MATRICULADO]")
    print(df_immune['Matriculado'].value_counts())
    print(f"Porcentaje True: {df_immune['Matriculado'].mean()*100:.2f}%")
    
    print(f"\n[ORIGEN_PLATAFORMA]")
    print(df_immune['origen_plataforma'].value_counts())
    
    print(f"\n[DISPOSITIVO]")
    print(df_immune['Dispositivo'].value_counts())
    
    print(f"\n[LOCALIZACION] - Top 10")
    print(df_immune['Localizacion'].value_counts().head(10))
    
    print(f"\n[IP_USUARIO]")
    print(f"IPs únicas: {df_immune['IP_usuario'].nunique()}")
    print(f"IPs más frecuentes (Top 5):")
    print(df_immune['IP_usuario'].value_counts().head(5))
    
    print(f"\n[PROGRAMA_OFERTA_CLICK]")
    print(f"Registros con click: {df_immune['programa_oferta_click'].notna().sum()} ({df_immune['programa_oferta_click'].notna().mean()*100:.2f}%)")
    print(f"Cursos más consultados (Top 5):")
    print(df_immune['programa_oferta_click'].value_counts().head(5))
    
    # Verificar correlaciones lógicas
    print("\n" + "=" * 50)
    print("VERIFICACIÓN DE CORRELACIONES LÓGICAS")
    print("=" * 50)
    
    # 1. Matriculado=True → Id_usuario no null (obligatorio)
    matriculados = df_immune[df_immune['Matriculado'] == True]
    if len(matriculados) > 0:
        todos_con_id = matriculados['Id_usuario'].notna().all()
        print(f"✓ Matriculados con Id_usuario no null: {todos_con_id} ({len(matriculados)} registros)")
        if not todos_con_id:
            print(f"  [ERROR] Hay {matriculados['Id_usuario'].isna().sum()} matriculados sin Id_usuario")
    
    # 2. Verificar que no hay matrículas sin ID
    matriculados_sin_id = df_immune[(df_immune['Matriculado'] == True) & (df_immune['Id_usuario'].isna())]
    if len(matriculados_sin_id) > 0:
        print(f"  [ERROR] Encontrados {len(matriculados_sin_id)} registros matriculados sin Id_usuario")
    else:
        print(f"✓ No hay matrículas sin Id_usuario")
    
    # 4. Verificar coherencia País para IDs de formularios
    ids_formularios_set = set([str(id) for id in IDS_FORMULARIOS])
    registros_con_id_formulario = df_immune[df_immune['Id_usuario'].notna() & 
                                            df_immune['Id_usuario'].astype(str).isin(ids_formularios_set)]
    
    if len(registros_con_id_formulario) > 0:
        # Verificar que los países coinciden (muestra aleatoria)
        muestra = registros_con_id_formulario.sample(min(10, len(registros_con_id_formulario)))
        coherentes = 0
        for idx, row in muestra.iterrows():
            id_str = str(row['Id_usuario'])
            if id_str in MAPEO_ID_PAIS:
                pais_formulario = MAPEO_ID_PAIS[id_str]
                localizacion = str(row['Localizacion'])
                # Verificar que el país del formulario está en la localización
                if pais_formulario in localizacion:
                    coherentes += 1
        print(f"[OK] Coherencia País para IDs de formularios: {coherentes}/{len(muestra)} muestras verificadas")
    
    # Mostrar primeras filas
    print("\n" + "=" * 50)
    print("PRIMERAS 5 FILAS")
    print("=" * 50)
    print(df_immune.head())

