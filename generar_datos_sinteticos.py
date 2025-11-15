import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuración de semilla para reproducibilidad
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
rng = np.random.default_rng(RANDOM_SEED)

# ============================================================================
# 1. GENERACIÓN DE DATAFRAME: Metricas_campañas
# ============================================================================

# ===========================
# OPCIONES CATEGÓRICAS
# ===========================

PLATAFORMAS = ["Google Ads", "Meta Ads", "LinkedIn Ads", "TikTok Ads"]
FUENTES = ["google", "facebook", "instagram", "linkedin", "newsletter"]
MEDIOS = ["cpc", "social", "email", "display", "video"]
PERIODOS_ACADEMICOS = ["pre_matricula", "captacion", "cierre", "post_matricula"]
FRANJAS_HORARIAS = ["manana", "tarde", "noche"]
CIUDADES = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Online"]
PAISES = ["ES", "PT", "FR", "IT", "MX", "AR", "CO"]
DEVICE_CATEGORIES = ["desktop", "mobile", "tablet"]

NIVELES_ESTUDIO = [
    "ESO", "Bachillerato", "FP", "Grado universitario",
    "Postgrado/Master", "Doctorado"
]
SITUACION_LABORAL = [
    "estudiante", "trabajando", "en_transicion", "desempleado"
]
INTERES_AREA = [
    "IA", "Ciberseguridad", "Data", "Full-Stack", "Cloud", "UX/UI"
]
OBJETIVO = [
    "first_job", "reskilling", "upskilling", "emprendimiento"
]
CAPACIDAD_INVERSION = ["baja", "media", "alta"]
GENEROS = ["M", "F", "Otro", "Prefiere_no_decirlo"]

TIPO_CREATIVIDAD = ["imagen", "video", "carrusel"]
FORMATO_CREATIVIDAD = ["feed", "stories", "shorts/reels", "search", "display"]
CTA_MENSAJE = [
    "Inscríbete ahora", "Reserva tu plaza", "Descargar guía",
    "Agenda una llamada", "Solicita información"
]
ANGULO_MENSAJE = [
    "empleabilidad", "salario", "vocacion_tech", "flexibilidad", "internacional"
]
MODELOS_ATRIBUCION = ["last_click", "first_click", "data_driven"]

# Alguna variable extra útil:
CANALES_AGRUPADOS = ["search", "paid_social", "display_video", "email_own", "organic_like"]

def generar_metricas_campanas(n_filas=500):
    # ===========================
    # 1. CONTEXTO TEMPORAL
    # ===========================
    fechas = pd.to_datetime(
        rng.integers(
            pd.Timestamp("2024-01-01").value,
            pd.Timestamp("2024-12-31").value,
            size=n_filas,
        )
    ).normalize()

    df = pd.DataFrame({
        "fecha": fechas,
    })

    df["mes"] = df["fecha"].dt.month
    df["dia_semana"] = df["fecha"].dt.day_name()
    df["es_fin_de_semana"] = df["dia_semana"].isin(["Saturday", "Sunday"]).astype(int)
    df["franja_horaria"] = rng.choice(FRANJAS_HORARIAS, size=n_filas, replace=True)
    df["periodo_academico"] = rng.choice(PERIODOS_ACADEMICOS, size=n_filas, replace=True)

    # ===========================
    # 2. IDENTIDAD / CANAL
    # ===========================
    df["plataforma"] = rng.choice(PLATAFORMAS, size=n_filas, replace=True)
    df["fuente"] = rng.choice(FUENTES, size=n_filas, replace=True)
    df["medio"] = rng.choice(MEDIOS, size=n_filas, replace=True)
    df["canal_agrupado"] = rng.choice(CANALES_AGRUPADOS, size=n_filas, replace=True)

    # IDs sintéticos de campaña / conjunto / anuncio
    df["campana_id"] = rng.integers(100, 999, size=n_filas).astype(str)
    df["campana_nombre"] = "Campaña_" + df["campana_id"]
    df["conjunto_anuncios_id"] = rng.integers(1000, 9999, size=n_filas).astype(str)
    df["conjunto_anuncios"] = "Conjunto_" + df["conjunto_anuncios_id"]
    df["anuncio_id"] = rng.integers(10000, 99999, size=n_filas).astype(str)
    df["anuncio_nombre"] = "Anuncio_" + df["anuncio_id"]

    # Landing / ubicación
    df["landing_url"] = "https://immune.institute/landing/" + rng.choice(
        ["ia", "ciberseguridad", "data", "fullstack", "cloud"], size=n_filas
    )
    df["ciudad_usuario"] = rng.choice(CIUDADES, size=n_filas, replace=True)
    df["pais_usuario"] = rng.choice(PAISES, size=n_filas, replace=True)
    df["device_category"] = rng.choice(DEVICE_CATEGORIES, size=n_filas, replace=True)

    # ===========================
    # 3. PERFIL DEL USUARIO
    # ===========================
    df["edad"] = rng.integers(18, 55, size=n_filas)
    df["genero"] = rng.choice(GENEROS, size=n_filas, replace=True)
    df["nivel_estudios"] = rng.choice(NIVELES_ESTUDIO, size=n_filas, replace=True)
    df["situacion_laboral"] = rng.choice(SITUACION_LABORAL, size=n_filas, replace=True)
    df["interes_area"] = rng.choice(INTERES_AREA, size=n_filas, replace=True)
    df["experiencia_previa_tech"] = rng.choice([0, 1, 2], size=n_filas, replace=True)  # 0,1,2 = bajo/medio/alto
    df["objetivo"] = rng.choice(OBJETIVO, size=n_filas, replace=True)
    df["capacidad_inversion"] = rng.choice(CAPACIDAD_INVERSION, size=n_filas, replace=True)

    # ===========================
    # 4. PAID MEDIA (base)
    # ===========================
    # Impresiones, alcance, clics
    impresiones = rng.integers(500, 50000, size=n_filas)
    alcance = np.minimum(
        impresiones,
        rng.integers(200, 20000, size=n_filas)
    )
    alcance = np.maximum(alcance, 1)  # evitar 0

    ctr = rng.uniform(0.005, 0.20, size=n_filas)  # 0.5% a 20%
    clics = np.maximum((impresiones * ctr).astype(int), 1)

    cpc = rng.uniform(0.3, 5.0, size=n_filas)
    gasto = clics * cpc
    cpm = (gasto / np.maximum(impresiones, 1)) * 1000

    df["impresiones"] = impresiones
    df["alcance"] = alcance
    df["frecuencia"] = df["impresiones"] / df["alcance"]
    df["clics"] = clics
    df["gasto"] = gasto
    df["ctr"] = df["clics"] / df["impresiones"]
    df["cpc"] = cpc
    df["cpm"] = cpm

    # ===========================
    # 5. MÉTRICAS WEB
    # ===========================
    # Sesiones ~ clics (+ ruido)
    sesiones = np.maximum((df["clics"] * rng.uniform(0.8, 1.1, size=n_filas)).astype(int), 1)
    usuarios = np.maximum((sesiones * rng.uniform(0.6, 1.0, size=n_filas)).astype(int), 1)
    nuevos_usuarios = (usuarios * rng.uniform(0.3, 0.8, size=n_filas)).astype(int)
    nuevos_usuarios = np.minimum(nuevos_usuarios, usuarios)
    usuarios_recurrentes = np.maximum(usuarios - nuevos_usuarios, 0)

    paginas_vistas = sesiones * rng.integers(1, 6, size=n_filas)
    paginas_por_sesion = paginas_vistas / sesiones

    engagement_rate = rng.uniform(0.1, 0.9, size=n_filas)
    scroll_max = rng.uniform(30, 100, size=n_filas)

    eventos_interaccion = (sesiones * rng.uniform(0.5, 3.0, size=n_filas)).astype(int)

    # Eventos relacionados con formulario
    eventos_form_view = (sesiones * rng.uniform(0.1, 0.8, size=n_filas)).astype(int)
    eventos_form_start = np.minimum(
        (eventos_form_view * rng.uniform(0.4, 0.9, size=n_filas)).astype(int),
        eventos_form_view
    )
    eventos_form_submit = np.minimum(
        (eventos_form_start * rng.uniform(0.3, 0.9, size=n_filas)).astype(int),
        eventos_form_start
    )

    df["sesiones"] = sesiones
    df["usuarios"] = usuarios
    df["nuevos_usuarios"] = nuevos_usuarios
    df["usuarios_recurrentes"] = usuarios_recurrentes
    df["paginas_vistas"] = paginas_vistas
    df["paginas_por_sesion"] = paginas_por_sesion
    df["engagement_rate"] = engagement_rate
    df["scroll_max"] = scroll_max
    df["eventos_interaccion"] = eventos_interaccion
    df["eventos_form_view"] = eventos_form_view
    df["eventos_form_start"] = eventos_form_start
    df["eventos_form_submit"] = eventos_form_submit

    # ===========================
    # 6. FUNNEL EDUCATIVO / NEGOCIO
    # ===========================
    # leads ~ eventos_form_submit, matriculas ~ leads
    leads = np.maximum(
        (eventos_form_submit * rng.uniform(0.5, 1.0, size=n_filas)).astype(int),
        0
    )

    leads_cualificados = np.minimum(
        (leads * rng.uniform(0.4, 0.9, size=n_filas)).astype(int),
        leads
    )

    entrevistas_agendadas = np.minimum(
        (leads_cualificados * rng.uniform(0.5, 0.95, size=n_filas)).astype(int),
        leads_cualificados
    )

    entrevistas_realizadas = np.minimum(
        (entrevistas_agendadas * rng.uniform(0.7, 1.0, size=n_filas)).astype(int),
        entrevistas_agendadas
    )

    matriculas = np.minimum(
        (entrevistas_realizadas * rng.uniform(0.2, 0.8, size=n_filas)).astype(int),
        entrevistas_realizadas
    )

    # ticket medio
    importe_matricula = rng.uniform(4000, 12000, size=n_filas)
    ingresos = matriculas * importe_matricula

    df["leads"] = leads
    df["leads_cualificados"] = leads_cualificados
    df["entrevistas_agendadas"] = entrevistas_agendadas
    df["entrevistas_realizadas"] = entrevistas_realizadas
    df["matriculas"] = matriculas
    df["importe_matricula"] = importe_matricula
    df["ingresos"] = ingresos

    # conversiones (puedes equipararlo a leads o a otra métrica)
    df["conversiones"] = df["leads"]
    df["tasa_conversion"] = df["conversiones"] / df["sesiones"]

    # ===========================
    # 7. ATRIBUCIÓN
    # ===========================
    df["modelo_atribucion"] = rng.choice(MODELOS_ATRIBUCION, size=n_filas, replace=True)

    # repartimos conversiones en dos modelos para simular diferencias
    factor_ll = rng.uniform(0.6, 1.1, size=n_filas)
    factor_dd = rng.uniform(0.8, 1.2, size=n_filas)

    df["conversiones_last_click"] = np.maximum((df["conversiones"] * factor_ll).astype(int), 0)
    df["conversiones_data_driven"] = np.maximum((df["conversiones"] * factor_dd).astype(int), 0)

    # ===========================
    # 8. CREATIVIDAD
    # ===========================
    df["tipo_creatividad"] = rng.choice(TIPO_CREATIVIDAD, size=n_filas, replace=True)
    df["formato_creatividad"] = rng.choice(FORMATO_CREATIVIDAD, size=n_filas, replace=True)
    df["cta_mensaje"] = rng.choice(CTA_MENSAJE, size=n_filas, replace=True)
    df["angulo_mensaje"] = rng.choice(ANGULO_MENSAJE, size=n_filas, replace=True)
    df["duracion_video_segundos"] = np.where(
        df["tipo_creatividad"] == "video",
        rng.integers(10, 120, size=n_filas),
        0
    )
    # color_dominante representado como cluster 0-4
    df["color_dominante"] = rng.integers(0, 5, size=n_filas)

    # ===========================
    # 9. MÉTRICAS DERIVADAS CLAVE
    # ===========================
    df["cpl"] = df["gasto"] / np.maximum(df["leads"], 1)
    df["cpmatricula"] = df["gasto"] / np.maximum(df["matriculas"], 1)
    df["roas"] = np.where(df["gasto"] > 0, df["ingresos"] / df["gasto"], 0)

    df["interaccion_media"] = df["eventos_interaccion"] / df["sesiones"]
    df["indice_intencion_form"] = df["eventos_form_start"] / np.maximum(df["sesiones"], 1)
    df["porcentaje_scroll"] = df["scroll_max"] / 100.0
    df["engagement_relevante"] = df["engagement_rate"] * df["paginas_por_sesion"]
    df["eficiencia_creatividad"] = df["clics"] / df["alcance"]
    df["eficiencia_gasto"] = df["conversiones"] / np.maximum(df["gasto"], 1)
    df["valor_prospecto"] = np.where(
        df["leads"] > 0,
        df["ingresos"] / df["leads"],
        0
    )
    df["ratio_frecuencia"] = df["frecuencia"]
    df["propension_matricula"] = np.where(
        df["leads"] > 0,
        df["matriculas"] / df["leads"],
        0
    )

    # ===========================
    # 10. SALUD DE LOS DATOS (extra útil)
    # ===========================
    # Simple: penaliza 0 impresiones, 0 sesiones, 0 leads
    penalizacion = (
        (df["impresiones"] == 0).astype(int)
        + (df["sesiones"] == 0).astype(int)
        + (df["leads"] == 0).astype(int)
    )
    df["data_health_score"] = np.clip(100 - penalizacion * 20, 0, 100)

    return df

# ============================================================================
# 2. GENERACIÓN DE DATAFRAME: Metricas_satisfaccion
# ============================================================================

def generar_metricas_satisfaccion(n_registros=500):
    """
    Genera DataFrame sintético con métricas de satisfacción de estudiantes
    Distribuido a lo largo de un año lectivo con media de 20 estudiantes
    """
    # Rango de fechas: año lectivo (septiembre 2024 - junio 2025)
    start_date = pd.Timestamp('2024-09-01')
    end_date = pd.Timestamp('2025-06-30')
    
    # Generar fechas distribuidas a lo largo del año lectivo
    fechas = []
    meses = pd.date_range(start_date, end_date, freq='MS')
    
    for mes in meses:
        # Aproximadamente 50 registros por mes (500/10 meses)
        registros_mes = np.random.poisson(50)
        fechas_mes = pd.date_range(
            mes, 
            min(mes + pd.offsets.MonthEnd(), end_date), 
            periods=registros_mes
        )
        fechas.extend(fechas_mes)
    
    # Si no tenemos suficientes, completar aleatoriamente
    while len(fechas) < n_registros:
        fecha_aleatoria = start_date + timedelta(
            days=np.random.randint(0, (end_date - start_date).days)
        )
        fechas.append(fecha_aleatoria)
    
    fechas = pd.to_datetime(fechas[:n_registros])
    
    # Opciones para matrices
    opciones_matriz = ["Pésimo", "Mal", "Regular", "Bien", "Genial"]
    
    # Opciones para tipo de programa
    tipo_programa_opciones = ["Online", "Presencial"]
    
    # Comentarios de ejemplo (algunos vacíos, otros con texto)
    comentarios_ejemplos = [
        "", "", "", "", "",  # 50% vacíos
        "Excelente profesor, muy claro en las explicaciones",
        "Las clases son muy prácticas y útiles",
        "Me gustaría más tiempo para practicar",
        "El contenido está muy actualizado",
        "A veces las clases se hacen un poco largas",
        "Muy satisfecho con el curso",
        "El profesor explica muy bien pero va muy rápido",
        "Genial, aprendí mucho",
        "Buen curso en general",
        "Podría mejorar la organización de las actividades",
        "Muy recomendable",
        "Las conexiones a veces fallan",
        "Contenido muy útil para mi futuro profesional",
        "Excelente calidad de audio y video",
        "El horario me viene perfecto",
        "Muy buen dominio de la materia por parte del profesor"
    ]
    
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
    
    # Generar satisfacción general correlacionada con otras métricas
    datos = []
    
    for i in range(n_registros):
        # Generar métricas de evaluación del profesor (sesgo positivo)
        preparado = generar_escala_positiva()
        dominio = generar_escala_positiva()
        atencion = generar_escala_positiva()
        ejemplos = generar_escala_positiva()
        ejemplos_prof = generar_escala_positiva()
        accesible = generar_escala_positiva()
        colaboracion = generar_escala_positiva()
        puntualidad = generar_escala_positiva()
        redes = generar_escala_neutra()  # Puede ser más variado
        recomendaria = generar_escala_positiva()
        
        # Métricas de metodología
        organiza = generar_escala_positiva()
        contenidos = generar_escala_positiva()
        dificultad = generar_escala_neutra()  # Distribución más equilibrada
        conocimientos_utiles = generar_escala_positiva()
        
        # Valoración de clases (matrices)
        duracion = generar_matriz_positiva()
        horario = generar_matriz_positiva()
        conveniencia = generar_matriz_positiva()
        conexion = generar_matriz_neutra()  # Puede variar más
        visibilidad = generar_matriz_positiva()
        audio = generar_matriz_positiva()
        
        # Soporte y comunicaciones
        velocidad_resp = generar_escala_positiva()
        utilidad_anuncios = generar_escala_neutra()
        
        # Tipo de programa (70% Online, 30% Presencial)
        tipo_programa = np.random.choice(tipo_programa_opciones, p=[0.7, 0.3])
        
        # Satisfacción general (correlacionada con otras métricas)
        # Promedio de las métricas principales
        promedio_metricas = np.mean([
            preparado, dominio, atencion, ejemplos, accesible,
            recomendaria, organiza, contenidos, conocimientos_utiles
        ])
        # Añadir algo de variabilidad
        satisfaccion_general = int(np.clip(
            np.round(promedio_metricas + np.random.normal(0, 0.5)), 
            1, 5
        ))
        
        # Comentarios (50% vacíos, 50% con texto)
        comentario = np.random.choice(comentarios_ejemplos)
        
        datos.append({
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
            'tipo_programa': tipo_programa,
            'satisfaccion_general': satisfaccion_general,
            'comentarios': comentario
        })
    
    df_satisfaccion = pd.DataFrame(datos)
    return df_satisfaccion

# ============================================================================
# 3. GENERACIÓN Y GUARDADO DE DATAFRAMES
# ============================================================================

if __name__ == "__main__":
    print("Generando DataFrames sintéticos...")
    print("-" * 50)
    
    # Generar DataFrames
    print("1. Generando Metricas_campanas...")
    Metricas_campanas = generar_metricas_campanas(n_filas=500)
    print(f"   [OK] Generados {len(Metricas_campanas)} registros")
    print(f"   [OK] Columnas: {list(Metricas_campanas.columns)}")
    print(f"   [OK] Rango de fechas: {Metricas_campanas['fecha'].min()} a {Metricas_campanas['fecha'].max()}")
    
    print("\n2. Generando Metricas_satisfaccion...")
    Metricas_satisfaccion = generar_metricas_satisfaccion(n_registros=500)
    print(f"   [OK] Generados {len(Metricas_satisfaccion)} registros")
    print(f"   [OK] Columnas: {list(Metricas_satisfaccion.columns)}")
    print(f"   [OK] Rango de fechas: {Metricas_satisfaccion['fecha'].min()} a {Metricas_satisfaccion['fecha'].max()}")
    
    # Guardar como CSV
    print("\n3. Guardando DataFrames...")
    Metricas_campanas.to_csv('Metricas_campanas.csv', index=False, encoding='utf-8-sig')
    Metricas_satisfaccion.to_csv('Metricas_satisfaccion.csv', index=False, encoding='utf-8-sig')
    print("   [OK] Metricas_campanas.csv guardado")
    print("   [OK] Metricas_satisfaccion.csv guardado")
    
    # Mostrar resumen estadístico
    print("\n" + "=" * 50)
    print("RESUMEN ESTADÍSTICO")
    print("=" * 50)
    
    print("\n[METRICAS_CAMPANAS]")
    print(Metricas_campanas.describe())
    print(f"\nDistribucion por plataforma:")
    print(Metricas_campanas['plataforma'].value_counts())
    
    print("\n[METRICAS_SATISFACCION]")
    print(Metricas_satisfaccion.describe())
    print(f"\nDistribucion por tipo_programa:")
    print(Metricas_satisfaccion['tipo_programa'].value_counts())
    print(f"\nDistribucion satisfaccion_general:")
    print(Metricas_satisfaccion['satisfaccion_general'].value_counts().sort_index())
    
    # Mostrar primeras filas
    print("\n" + "=" * 50)
    print("PRIMERAS FILAS")
    print("=" * 50)
    print("\nMetricas_campanas (primeras 3 filas):")
    print(Metricas_campanas.head(3))
    print("\nMetricas_satisfaccion (primeras 3 filas):")
    print(Metricas_satisfaccion.head(3))

