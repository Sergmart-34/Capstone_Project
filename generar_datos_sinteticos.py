import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuración de semilla para reproducibilidad
np.random.seed(42)
random.seed(42)

# ============================================================================
# 1. GENERACIÓN DE DATAFRAME: Metricas_campañas
# ============================================================================

def generar_metricas_campanas(n_registros=500):
    """
    Genera DataFrame sintético con métricas de Google Analytics y Facebook Ads
    """
    # Rango de fechas: año lectivo (septiembre 2024 - junio 2025)
    start_date = pd.Timestamp('2024-09-01')
    end_date = pd.Timestamp('2025-06-30')
    
    # Generar fechas aleatorias
    fechas = pd.date_range(start_date, end_date, periods=n_registros)
    fechas = np.random.choice(fechas, n_registros, replace=True)
    fechas = pd.to_datetime(fechas).sort_values()
    
    # Nombres de campañas realistas
    campanas_ga = [
        'Master Data Science 2024', 'Bootcamp Full Stack', 'Curso Python Avanzado',
        'Master IA y ML', 'Bootcamp Marketing Digital', 'Curso SQL Profesional',
        'Master Ciberseguridad', 'Bootcamp UX/UI', 'Curso Cloud Computing'
    ]
    
    campanas_fb = [
        'Master Data Science 2024', 'Bootcamp Full Stack', 'Curso Python Avanzado',
        'Master IA y ML', 'Bootcamp Marketing Digital', 'Curso SQL Profesional',
        'Master Ciberseguridad', 'Bootcamp UX/UI', 'Curso Cloud Computing'
    ]
    
    # Fuentes y medios (Google Analytics)
    fuentes = ['google', 'facebook', 'direct', 'organic', 'referral', 'email']
    medios = ['cpc', 'organic', 'referral', 'email', 'display', 'social']
    
    # Conjuntos de anuncios y nombres de anuncios (Facebook Ads)
    conjuntos_anuncios = [
        'Conjunto Retargeting', 'Conjunto Lookalike', 'Conjunto Intereses',
        'Conjunto Demográfico', 'Conjunto Audiencia Personalizada'
    ]
    
    anuncios_nombres = [
        'Anuncio Video Master', 'Anuncio Carousel', 'Anuncio Imagen Simple',
        'Anuncio Lead Gen', 'Anuncio Conversión', 'Anuncio Brand Awareness'
    ]
    
    # Determinar qué plataforma usar para cada registro
    plataformas = np.random.choice(['Google Analytics', 'Facebook Ads'], 
                                   n_registros, p=[0.5, 0.5])
    
    # Inicializar listas para almacenar datos
    datos = []
    
    for i, fecha in enumerate(fechas):
        plataforma = plataformas[i]
        
        if plataforma == 'Google Analytics':
            # Métricas específicas de Google Analytics
            sesiones = np.random.randint(50, 2000)
            usuarios = int(sesiones * np.random.uniform(0.7, 0.95))
            paginas_vistas = int(sesiones * np.random.uniform(1.5, 4.5))
            tasa_rebote = np.random.uniform(30, 75)
            duracion_promedio = np.random.uniform(60, 600)  # segundos
            conversiones = np.random.randint(0, int(sesiones * 0.1))
            tasa_conversion = (conversiones / sesiones * 100) if sesiones > 0 else 0
            ingresos = conversiones * np.random.uniform(500, 5000)
            
            datos.append({
                'fecha': fecha,
                'plataforma': 'Google Analytics',
                'campana_nombre': np.random.choice(campanas_ga),
                'fuente': np.random.choice(fuentes),
                'medio': np.random.choice(medios),
                'sesiones': sesiones,
                'usuarios': usuarios,
                'paginas_vistas': paginas_vistas,
                'tasa_rebote': round(tasa_rebote, 2),
                'duracion_promedio_sesion': round(duracion_promedio, 2),
                'conversiones': conversiones,
                'tasa_conversion': round(tasa_conversion, 2),
                'ingresos': round(ingresos, 2),
                # Campos específicos de Facebook (NaN para GA)
                'conjunto_anuncios': None,
                'anuncio_nombre': None,
                'impresiones': None,
                'alcance': None,
                'clics': None,
                'gasto': None,
                'ctr': None,
                'cpc': None,
                'cpm': None,
                'costo_por_conversion': None
            })
        else:
            # Métricas específicas de Facebook Ads
            impresiones = np.random.randint(1000, 50000)
            alcance = int(impresiones * np.random.uniform(0.6, 0.9))
            clics = np.random.randint(10, int(impresiones * 0.05))
            gasto = np.random.uniform(50, 2000)
            ctr = (clics / impresiones * 100) if impresiones > 0 else 0
            cpc = (gasto / clics) if clics > 0 else 0
            cpm = (gasto / impresiones * 1000) if impresiones > 0 else 0
            conversiones = np.random.randint(0, int(clics * 0.15))
            costo_por_conversion = (gasto / conversiones) if conversiones > 0 else 0
            
            datos.append({
                'fecha': fecha,
                'plataforma': 'Facebook Ads',
                'campana_nombre': np.random.choice(campanas_fb),
                'conjunto_anuncios': np.random.choice(conjuntos_anuncios),
                'anuncio_nombre': np.random.choice(anuncios_nombres),
                'impresiones': impresiones,
                'alcance': alcance,
                'clics': clics,
                'gasto': round(gasto, 2),
                'ctr': round(ctr, 2),
                'cpc': round(cpc, 2),
                'cpm': round(cpm, 2),
                'conversiones': conversiones,
                'costo_por_conversion': round(costo_por_conversion, 2),
                # Campos específicos de Google Analytics (NaN para FB)
                'fuente': None,
                'medio': None,
                'sesiones': None,
                'usuarios': None,
                'paginas_vistas': None,
                'tasa_rebote': None,
                'duracion_promedio_sesion': None,
                'tasa_conversion': None,
                'ingresos': None
            })
    
    df_campanas = pd.DataFrame(datos)
    return df_campanas

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
    Metricas_campanas = generar_metricas_campanas(n_registros=500)
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

