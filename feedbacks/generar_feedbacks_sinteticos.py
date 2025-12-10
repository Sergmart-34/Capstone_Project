import pandas as pd
import numpy as np
import random
import unicodedata

# Configuración de semilla para reproducibilidad
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
rng = np.random.default_rng(RANDOM_SEED)

def reparar_texto(texto):
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
    df = df.copy()
    df.columns = [reparar_texto(col) if isinstance(col, str) else col for col in df.columns]
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(reparar_texto)
    return df


def cargar_catalogo_cursos(ruta='cursos_immune/cursos_immune.xlsx'):
    try:
        df = pd.read_excel(ruta, engine='openpyxl')
        df = limpiar_dataframe(df)
        if not {'id_curso', 'modalidad'}.issubset(df.columns):
            raise ValueError("El catálogo no tiene columnas 'id_curso' y 'modalidad'")
        df = df[['id_curso', 'modalidad']].dropna()
        df['id_curso'] = df['id_curso'].astype(str).str.upper()
        df['modalidad'] = df['modalidad'].astype(str).str.strip()
        df = df[df['id_curso'].str.len() > 0]
        if df.empty:
            raise ValueError("El catálogo está vacío")
        return df.reset_index(drop=True)
    except Exception as exc:
        print(f"[WARN] No se pudo cargar cursos_immune ({exc}). Usando fallback sintético.")
        ids = [f"C{i:04d}" for i in range(10, 32)]
        modalidades = ["Online" if i % 2 == 0 else "Presencial" for i in range(len(ids))]
        return pd.DataFrame({"id_curso": ids, "modalidad": modalidades})


CATALOGO_CURSOS = cargar_catalogo_cursos()
CATALOGO_CURSOS['modalidad_normalizada'] = CATALOGO_CURSOS['modalidad'].str.lower()
CATALOGO_CURSOS['modalidad_ascii'] = CATALOGO_CURSOS['modalidad_normalizada'].apply(
    lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode('utf-8')
)
CATALOGO_CURSOS['tipo_clase'] = np.where(
    CATALOGO_CURSOS['modalidad_ascii'].str.contains('online', na=False),
    'Online',
    'Híbrido'
)
CATALOGO_ARRAY = CATALOGO_CURSOS[['id_curso', 'tipo_clase']].to_numpy()

# ============================================================================
# Comentarios sintéticos
# ============================================================================

COMENTARIOS_PATH = "feedbacks/comentarios_sinteticos_1500.csv"

VARIABLES_TEXTO_COMENTARIOS = {
    "clase_duracion",
    "clase_horario",
    "clase_conveniencia_dia",
    "clase_calidad_conexion",
    "clase_calidad_audio",
    "clase_visibilidad_pantalla",
}

MATRIZ_A_NUMERO_COMENTARIOS = {
    "Pésimo": 1,
    "Mal": 2,
    "Regular": 3,
    "Bien": 4,
    "Genial": 5,
}


def _convertir_valor_a_numero(valor, variable):
    if variable in VARIABLES_TEXTO_COMENTARIOS:
        return MATRIZ_A_NUMERO_COMENTARIOS.get(valor, 3)
    if isinstance(valor, (int, float)):
        return float(valor)
    return 3


def _calcular_score_matching(comentario_row, encuesta_row):
    score = 0

    sat_encuesta = encuesta_row.get("satisfaccion_general", 3)
    sat_min = comentario_row.get("satisfaccion_min", 1)
    sat_max = comentario_row.get("satisfaccion_max", 5)

    if sat_min <= sat_encuesta <= sat_max:
        score += 40
    elif abs(sat_encuesta - sat_min) == 1 or abs(sat_encuesta - sat_max) == 1:
        score += 20

    aspecto_variable = comentario_row.get("aspecto_variable", "ninguno")
    aspecto_min = comentario_row.get("aspecto_valor_min", 1)
    aspecto_max = comentario_row.get("aspecto_valor_max", 5)

    if aspecto_variable == "ninguno":
        score += 30
    elif aspecto_variable in encuesta_row.index:
        valor = _convertir_valor_a_numero(encuesta_row[aspecto_variable], aspecto_variable)
        if aspecto_min <= valor <= aspecto_max:
            score += 60
        elif abs(valor - aspecto_min) == 1 or abs(valor - aspecto_max) == 1:
            score += 30

    return score


def asignar_comentarios(df_encuestas, ruta_comentarios=COMENTARIOS_PATH):
    """
    Asigna comentarios únicos a cada encuesta basándose en matching inteligente.
    Garantiza que ningún comentario se repita.
    """
    try:
        df_comentarios = pd.read_csv(ruta_comentarios)
    except FileNotFoundError:
        fallback = "feedbacks/comentarios_sinteticos_1000.csv"
        if ruta_comentarios != fallback:
            try:
                df_comentarios = pd.read_csv(fallback)
                print(f"[WARN] No se encontró {ruta_comentarios}. Se usa fallback {fallback}.")
            except FileNotFoundError:
                print(f"[WARN] No se encontraron archivos de comentarios. Se mantienen comentarios vacíos.")
                return df_encuestas
        else:
            print(f"[WARN] No se encontró {ruta_comentarios}. Se mantienen comentarios vacíos.")
            return df_encuestas

    df_comentarios = df_comentarios.dropna(subset=["comentario"]).reset_index(drop=True)
    df_resultado = df_encuestas.copy()
    if "comentarios" not in df_resultado.columns:
        df_resultado["comentarios"] = ""

    comentarios_usados = set()
    comentarios_disponibles = df_comentarios.copy()

    for idx, encuesta in df_resultado.iterrows():
        candidatos = []
        for com_idx, comentario in comentarios_disponibles.iterrows():
            texto = str(comentario["comentario"]).strip()
            # Asegurar que el comentario no haya sido usado
            if texto in comentarios_usados or not texto:
                continue
            score = _calcular_score_matching(comentario, encuesta)
            candidatos.append((score, com_idx, texto))

        if not candidatos:
            # Si no hay candidatos disponibles, dejar vacío (nunca duplicar)
            df_resultado.at[idx, "comentarios"] = ""
            continue

        max_score = max(score for score, _, _ in candidatos)
        mejores = [c for c in candidatos if c[0] == max_score]
        _, elegido_idx, texto_elegido = random.choice(mejores)

        df_resultado.at[idx, "comentarios"] = texto_elegido
        comentarios_usados.add(texto_elegido)
        # Eliminar el comentario usado del DataFrame disponible
        comentarios_disponibles = comentarios_disponibles.drop(elegido_idx).reset_index(drop=True)

    # Validación final: verificar que no hay duplicados
    comentarios_unicos = df_resultado["comentarios"].nunique()
    comentarios_no_vacios = df_resultado[df_resultado["comentarios"] != ""]["comentarios"].nunique()
    total_no_vacios = len(df_resultado[df_resultado["comentarios"] != ""])
    
    if comentarios_no_vacios < total_no_vacios:
        print(f"[WARN] Algunos comentarios están duplicados: {total_no_vacios} no vacíos, {comentarios_no_vacios} únicos")
    else:
        print(f"[OK] Todos los comentarios son únicos: {comentarios_no_vacios} comentarios únicos asignados")

    return df_resultado

# ============================================================================
# GENERACIÓN DE DATAFRAME: Feedbacks
# ============================================================================

def _generar_fechas_en_rango(n_registros, start_date, end_date):
    """Genera fechas aleatorias uniformes en el rango dado (inclusive)."""
    if n_registros <= 0:
        return pd.DatetimeIndex([])

    inicio = pd.Timestamp(start_date).floor("s")
    fin = pd.Timestamp(end_date).floor("s")
    if fin <= inicio:
        raise ValueError("end_date debe ser posterior a start_date")

    # Hacemos inclusivo el último segundo sumando uno al total de segundos posibles
    total_segundos = int((fin - inicio).total_seconds())
    aleatorios = rng.integers(0, total_segundos + 1, size=n_registros)
    fechas = inicio + pd.to_timedelta(aleatorios, unit="s")
    return pd.to_datetime(fechas).sort_values().to_numpy()


def generar_feedbacks(
    n_registros=1200,
    start_date="2023-01-01",
    end_date="2025-12-31",
):
    """
    Genera un DataFrame sintético con métricas de satisfacción de estudiantes.
    Las fechas se reparten de forma uniforme dentro del rango solicitado.
    """
    fechas = _generar_fechas_en_rango(n_registros, start_date, end_date)
    
    # Generar IDs de usuario aleatorios únicos
    ids_usuario_unicos = [f"U{i:04d}" for i in range(1, n_registros + 1)]
    np.random.shuffle(ids_usuario_unicos)  # Mezclar para que sean aleatorios
    
    # Opciones para matrices
    opciones_matriz = ["Pésimo", "Mal", "Regular", "Bien", "Genial"]
    
    # Generar datos con distribuciones realistas
    # Las escalas 1-5 tienden a estar sesgadas hacia valores positivos (3-5)
    def generar_escala_positiva():
        """Genera valores 1-5 con sesgo hacia valores positivos"""
        weights = [0.05, 0.10, 0.20, 0.35, 0.30]  # Más probabilidad en 4 y 5
        return np.random.choice([1, 2, 3, 4, 5], p=weights)
    
    def generar_escala_neutra():
        """Genera valores 1-5 con distribución más equilibrada"""
        weights = [0.10, 0.15, 0.25, 0.30, 0.20]
        return np.random.choice([1, 2, 3, 4, 5], p=weights)
    
    def generar_matriz_positiva():
        """Genera valores de matriz con sesgo positivo"""
        weights = [0.05, 0.10, 0.20, 0.35, 0.30]
        return np.random.choice(opciones_matriz, p=weights)
    
    def generar_matriz_neutra():
        """Genera valores de matriz con distribución equilibrada"""
        weights = [0.10, 0.15, 0.25, 0.30, 0.20]
        return np.random.choice(opciones_matriz, p=weights)
    
    def generar_escala_superpositiva():
        """Genera valores 1-5 muy sesgados hacia 4-5"""
        weights = [0.01, 0.04, 0.10, 0.35, 0.50]
        return int(np.random.choice([1, 2, 3, 4, 5], p=weights))
    
    def generar_escala_negativa():
        """Genera valores 1-5 sesgados hacia 1-2"""
        weights = [0.45, 0.30, 0.15, 0.07, 0.03]
        return int(np.random.choice([1, 2, 3, 4, 5], p=weights))
    
    def generar_matriz_superpositiva():
        """Genera valores de matriz sesgados a Bien/Genial"""
        weights = [0.02, 0.05, 0.13, 0.35, 0.45]
        return np.random.choice(opciones_matriz, p=weights)
    
    def generar_matriz_negativa():
        """Genera valores de matriz sesgados a Pésimo/Mal"""
        weights = [0.45, 0.30, 0.15, 0.07, 0.03]
        return np.random.choice(opciones_matriz, p=weights)
    
    # Generar satisfacción general correlacionada con otras métricas
    datos = []

    num_superfans = int(n_registros * 0.30)
    num_criticos = int(n_registros * 0.10)
    num_equilibrados = max(n_registros - num_superfans - num_criticos, 0)

    objetivos_satisfaccion = (
        [5] * num_superfans
        + [1] * num_criticos
        + [None] * num_equilibrados
    )
    if len(objetivos_satisfaccion) < n_registros:
        objetivos_satisfaccion.extend([None] * (n_registros - len(objetivos_satisfaccion)))
    objetivos_satisfaccion = np.array(objetivos_satisfaccion, dtype=object)
    rng.shuffle(objetivos_satisfaccion)

    indices_superfan = []
    indices_critico = []

    for i in range(n_registros):
        objetivo_satisfaccion = (
            objetivos_satisfaccion[i] if i < len(objetivos_satisfaccion) else None
        )

        if objetivo_satisfaccion == 5:
            escenario = "superfan"
            indices_superfan.append(i)
        elif objetivo_satisfaccion == 1:
            escenario = "critico"
            indices_critico.append(i)
        else:
            escenario = "equilibrado"

        if escenario == "superfan":
            fn_positiva = generar_escala_superpositiva
            fn_neutra = generar_escala_positiva
            fn_matriz_positiva = generar_matriz_superpositiva
            fn_matriz_neutra = generar_matriz_superpositiva
        elif escenario == "critico":
            fn_positiva = generar_escala_negativa
            fn_neutra = generar_escala_negativa
            fn_matriz_positiva = generar_matriz_negativa
            fn_matriz_neutra = generar_matriz_negativa
        else:
            fn_positiva = generar_escala_positiva
            fn_neutra = generar_escala_neutra
            fn_matriz_positiva = generar_matriz_positiva
            fn_matriz_neutra = generar_matriz_neutra

        # Generar métricas de evaluación del profesor (sesgo positivo)
        preparado = fn_positiva()
        dominio = fn_positiva()
        atencion = fn_positiva()
        ejemplos = fn_positiva()
        ejemplos_prof = fn_positiva()
        accesible = fn_positiva()
        colaboracion = fn_positiva()
        puntualidad = fn_positiva()
        redes = fn_neutra()  # Puede ser más variado
        recomendaria = fn_positiva()
        
        # Métricas de metodología
        organiza = fn_positiva()
        contenidos = fn_positiva()
        dificultad = fn_neutra()  # Distribución más equilibrada
        conocimientos_utiles = fn_positiva()
        
        # Valoración de clases (matrices)
        duracion = fn_matriz_positiva()
        horario = fn_matriz_positiva()
        conveniencia = fn_matriz_positiva()
        
        # Selección de curso coherente con su modalidad oficial
        curso_idx = np.random.randint(0, len(CATALOGO_ARRAY))
        id_curso, tipo_clase = CATALOGO_ARRAY[curso_idx]
        
        # Valoraciones de conectividad:
        # - Online e Híbrido dan valores reales.
        if tipo_clase in ("Online", "Híbrido"):
            conexion = fn_matriz_neutra()
            visibilidad = fn_matriz_positiva()
            audio = fn_matriz_positiva()
        else:
            conexion = ""
            visibilidad = ""
            audio = ""
        
        # Soporte y comunicaciones
        velocidad_resp = fn_positiva()
        utilidad_anuncios = fn_neutra()
        
        # IDs
        id_encuesta = f"E{i+1:04d}"  # E0001, E0002, E0003, etc. (ascendente)
        id_usuario = ids_usuario_unicos[i]  # Aleatorio (mezclado)
        # Satisfacción general (correlacionada con otras métricas)
        # Promedio de las métricas principales
        promedio_metricas = np.mean([
            preparado, dominio, atencion, ejemplos, accesible,
            recomendaria, organiza, contenidos, conocimientos_utiles
        ])
        # Ajustar satisfacción general por escenario
        if objetivo_satisfaccion == 5:
            satisfaccion_general = 5
        elif objetivo_satisfaccion == 1:
            satisfaccion_general = 1
        else:
            satisfaccion_general = int(np.clip(
                np.round(promedio_metricas + np.random.normal(0, 0.6)),
                2, 5
            ))
        
        datos.append({
            'Id_encuesta': id_encuesta,
            'id_usuario': id_usuario,
            'Id_curso': id_curso,
            'Tipo_clase': tipo_clase,
            'fecha': fechas[i],
            'preparado_clases': preparado,
            'dominio_materia': dominio,
            'mantiene_atencion': atencion,
            'relaciona_con_ejemplos': ejemplos,
            'ejemplos_mundo_profesional': ejemplos_prof,
            'accesible_y_atiende_consultas': accesible,
            'fomenta_colaboracion': colaboracion,
            'puntualidad': puntualidad,
            'referencias_en_redes': redes,
            'recomendaria_profesor': recomendaria,
            'organiza_actividades': organiza,
            'contenidos_adecuados': contenidos,
            'grado_dificultad': dificultad,
            'conocimientos_utiles_futuro': conocimientos_utiles,
            'clase_duracion': duracion,
            'clase_horario': horario,
            'clase_conveniencia_dia': conveniencia,
            'clase_calidad_conexion': conexion,
            'clase_visibilidad_pantalla': visibilidad,
            'clase_calidad_audio': audio,
            'velocidad_respuesta': velocidad_resp,
            'utilidad_anuncios': utilidad_anuncios,
            'satisfaccion_general': satisfaccion_general,
            'comentarios': ''
        })
    
    df_satisfaccion = pd.DataFrame(datos)
    if indices_superfan:
        df_satisfaccion.loc[indices_superfan, "satisfaccion_general"] = 5
    if indices_critico:
        df_satisfaccion.loc[indices_critico, "satisfaccion_general"] = 1
    df_satisfaccion = asignar_comentarios(df_satisfaccion, COMENTARIOS_PATH)
    return df_satisfaccion

# ============================================================================
# 3. GENERACIÓN Y GUARDADO DE DATAFRAMES
# ============================================================================

if __name__ == "__main__":
    print("Generando DataFrame de feedbacks sintéticos...")
    print("-" * 50)
    
    Feedbacks = generar_feedbacks(
        n_registros=1200,
        start_date="2023-01-01",
        end_date="2025-12-31",
    )
    print(f"[OK] Generados {len(Feedbacks)} registros")
    print(f"[OK] Columnas: {list(Feedbacks.columns)}")
    print(f"[OK] Rango de fechas: {Feedbacks['fecha'].min()} a {Feedbacks['fecha'].max()}")
    
    print("\nGuardando DataFrame...")
    Feedbacks.to_csv(
        'feedbacks/Feedbacks.csv',
        index=False,
        encoding='utf-8-sig',
        date_format='%Y-%m-%d %H:%M:%S'
    )
    print("[OK] Feedbacks.csv guardado en feedbacks/")
    
    print("\n" + "=" * 50)
    print("RESUMEN ESTADÍSTICO FEEDBACKS")
    print("=" * 50)
    print(Feedbacks.describe())
    print(f"\nDistribucion por Tipo_clase:")
    print(Feedbacks['Tipo_clase'].value_counts())
    print(f"\nDistribucion por Id_curso:")
    print(Feedbacks['Id_curso'].value_counts().head(10))
    print(f"\nDistribucion satisfaccion_general:")
    print(Feedbacks['satisfaccion_general'].value_counts().sort_index())
    
    print("\n" + "=" * 50)
    print("PRIMERAS FILAS")
    print("=" * 50)
    print(Feedbacks.head(3))

