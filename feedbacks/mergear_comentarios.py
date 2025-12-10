"""
Script para asignar comentarios sintéticos a las encuestas de satisfacción
basándose en matching inteligente de polaridad, satisfacción y aspectos específicos.
"""

import pandas as pd
import numpy as np
from random import choice, seed

# Configuración de semilla para reproducibilidad
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
seed(RANDOM_SEED)

# Mapeo de texto a número para variables de tipo matriz
MATRIZ_A_NUMERO = {
    "Pésimo": 1,
    "Mal": 2,
    "Regular": 3,
    "Bien": 4,
    "Genial": 5
}

# Variables que son de tipo texto (matriz)
VARIABLES_TEXTO = {
    "clase_duracion", "clase_horario", "clase_conveniencia_dia",
    "clase_calidad_conexion", "clase_calidad_audio", "clase_visibilidad_pantalla"
}


def convertir_valor_a_numero(valor, variable):
    """
    Convierte un valor a número para comparación.
    Si es variable de texto, usa el mapeo. Si ya es numérico, lo devuelve tal cual.
    """
    if variable in VARIABLES_TEXTO:
        # Es variable de tipo texto (matriz)
        return MATRIZ_A_NUMERO.get(valor, 3)  # Default a 3 si no encuentra
    else:
        # Es variable numérica
        if isinstance(valor, (int, float)):
            return float(valor)
        return 3  # Default


def calcular_score_matching(comentario_row, encuesta_row):
    """
    Calcula un score de matching entre un comentario y una encuesta.
    Retorna un score de 0 a 100, donde 100 es match perfecto.
    """
    score = 0
    max_score = 100
    
    # 1. Matching de satisfacción general (40 puntos)
    sat_encuesta = encuesta_row['satisfaccion_general']
    sat_min = comentario_row['satisfaccion_min']
    sat_max = comentario_row['satisfaccion_max']
    
    if sat_min <= sat_encuesta <= sat_max:
        # Match perfecto
        score += 40
    elif sat_encuesta < sat_min:
        # Muy cerca por debajo
        diferencia = sat_min - sat_encuesta
        if diferencia == 1:
            score += 20
        else:
            score += 0
    elif sat_encuesta > sat_max:
        # Muy cerca por encima
        diferencia = sat_encuesta - sat_max
        if diferencia == 1:
            score += 20
        else:
            score += 0
    
    # 2. Matching de aspecto específico (60 puntos)
    aspecto_variable = comentario_row['aspecto_variable']
    
    if aspecto_variable == 'ninguno':
        # Si no hay aspecto específico, da puntos por default
        score += 30
    else:
        # Verificar que la variable existe en la encuesta
        if aspecto_variable in encuesta_row.index:
            valor_encuesta = encuesta_row[aspecto_variable]
            valor_encuesta_num = convertir_valor_a_numero(valor_encuesta, aspecto_variable)
            
            aspecto_min = comentario_row['aspecto_valor_min']
            aspecto_max = comentario_row['aspecto_valor_max']
            
            if aspecto_min <= valor_encuesta_num <= aspecto_max:
                # Match perfecto del aspecto
                score += 60
            elif valor_encuesta_num < aspecto_min:
                diferencia = aspecto_min - valor_encuesta_num
                if diferencia == 1:
                    score += 30
                else:
                    score += 0
            elif valor_encuesta_num > aspecto_max:
                diferencia = valor_encuesta_num - aspecto_max
                if diferencia == 1:
                    score += 30
                else:
                    score += 0
        else:
            # Variable no existe en encuesta, no da puntos
            score += 0
    
    return score


def asignar_comentarios(df_encuestas, df_comentarios):
    """
    Asigna comentarios a las encuestas basándose en matching inteligente.
    """
    print("Iniciando asignación de comentarios...")
    print(f"  - Encuestas: {len(df_encuestas)}")
    print(f"  - Comentarios disponibles: {len(df_comentarios)}")
    
    # Crear copia del DataFrame de encuestas
    df_resultado = df_encuestas.copy()
    
    # Inicializar columna de comentarios (mantener los existentes si hay)
    if 'comentarios' in df_resultado.columns:
        print("  - Columna 'comentarios' ya existe, se actualizará")
    else:
        df_resultado['comentarios'] = ''
    
    # Crear lista de comentarios disponibles (para evitar duplicados)
    comentarios_disponibles = df_comentarios.copy()
    comentarios_texto_usados = set()  # Textos de comentarios ya asignados (para evitar duplicados)
    
    # Para cada encuesta, encontrar el mejor comentario
    asignaciones = []
    scores_promedio = []
    
    for idx, encuesta in df_encuestas.iterrows():
        # Calcular scores solo para comentarios no usados
        scores = []
        comentarios_candidatos = []
        indices_candidatos = []
        
        for comentario_idx, comentario in comentarios_disponibles.iterrows():
            # Solo considerar comentarios que no se han usado antes (por texto)
            comentario_texto = comentario['comentario']
            if comentario_texto not in comentarios_texto_usados:
                score = calcular_score_matching(comentario, encuesta)
                scores.append(score)
                comentarios_candidatos.append(comentario)
                indices_candidatos.append(comentario_idx)
        
        # Seleccionar comentario con mejor score
        if scores:
            # Encontrar el mejor score
            mejor_score = max(scores)
            indices_mejores = [i for i, s in enumerate(scores) if s == mejor_score]
            
            # Si hay empate, elegir aleatoriamente entre los mejores
            idx_elegido = choice(indices_mejores)
            comentario_asignado = comentarios_candidatos[idx_elegido]
            comentario_idx_original = indices_candidatos[idx_elegido]
            
            # Asignar comentario
            comentario_texto = comentario_asignado['comentario']
            df_resultado.at[idx, 'comentarios'] = comentario_texto
            
            # Marcar comentario como usado (por texto para evitar duplicados)
            comentarios_texto_usados.add(comentario_texto)
            
            # Eliminar de la lista de disponibles
            comentarios_disponibles = comentarios_disponibles.drop(comentario_idx_original)
            
            asignaciones.append({
                'encuesta_idx': idx,
                'comentario_idx': comentario_idx_original,
                'score': mejor_score,
                'polaridad': comentario_asignado['polaridad'],
                'tema': comentario_asignado['tema']
            })
            
            scores_promedio.append(mejor_score)
        else:
            # No hay comentarios disponibles sin usar
            # En este caso, usar el mejor comentario disponible aunque esté duplicado
            # (solo si ya se agotaron todos los comentarios únicos)
            if len(comentarios_disponibles) > 0:
                scores = []
                comentarios_candidatos = []
                
                for _, comentario in comentarios_disponibles.iterrows():
                    score = calcular_score_matching(comentario, encuesta)
                    scores.append(score)
                    comentarios_candidatos.append(comentario)
                
                if scores:
                    mejor_score = max(scores)
                    idx_elegido = scores.index(mejor_score)
                    comentario_asignado = comentarios_candidatos[idx_elegido]
                    comentario_texto = comentario_asignado['comentario']
                    df_resultado.at[idx, 'comentarios'] = comentario_texto
                    
                    asignaciones.append({
                        'encuesta_idx': idx,
                        'comentario_idx': None,
                        'score': mejor_score,
                        'polaridad': comentario_asignado['polaridad'],
                        'tema': comentario_asignado['tema']
                    })
                    scores_promedio.append(mejor_score)
            else:
                df_resultado.at[idx, 'comentarios'] = ''
                asignaciones.append({
                    'encuesta_idx': idx,
                    'comentario_idx': None,
                    'score': 0,
                    'polaridad': None,
                    'tema': None
                })
    
    # Estadísticas
    print(f"\n[OK] Asignación completada")
    print(f"  - Comentarios asignados: {len([a for a in asignaciones if a['comentario_idx'] is not None])}")
    print(f"  - Score promedio: {np.mean(scores_promedio):.2f}")
    print(f"  - Score mínimo: {min(scores_promedio) if scores_promedio else 0}")
    print(f"  - Score máximo: {max(scores_promedio) if scores_promedio else 0}")
    
    # Distribución de polaridades asignadas
    print(f"\nDistribución de polaridades asignadas:")
    polaridades_asignadas = [a['polaridad'] for a in asignaciones if a['polaridad']]
    if polaridades_asignadas:
        from collections import Counter
        dist_polaridad = Counter(polaridades_asignadas)
        for pol, count in dist_polaridad.most_common():
            print(f"  - {pol}: {count}")
    
    return df_resultado, asignaciones


def main():
    print("=" * 60)
    print("MERCEO DE COMENTARIOS CON ENCUESTAS DE SATISFACCIÓN")
    print("=" * 60)
    
    # 1. Cargar datos
    print("\n1. Cargando datos...")
    try:
        df_encuestas = pd.read_csv('feedbacks/Feedbacks.csv')
        df_comentarios = pd.read_csv('feedbacks/comentarios_sinteticos_1000.csv')
        print(f"   [OK] Encuestas cargadas: {len(df_encuestas)} registros")
        print(f"   [OK] Comentarios cargados: {len(df_comentarios)} registros")
    except FileNotFoundError as e:
        print(f"   [ERROR] No se encontró el archivo: {e}")
        return
    
    # 2. Asignar comentarios
    print("\n2. Asignando comentarios...")
    df_resultado, asignaciones = asignar_comentarios(df_encuestas, df_comentarios)
    
    # 3. Guardar resultado
    print("\n3. Guardando resultado...")
    archivo_salida = 'feedbacks/Feedbacks.csv'
    df_resultado.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
    print(f"   [OK] Archivo guardado: {archivo_salida}")
    
    # 4. Mostrar ejemplos
    print("\n" + "=" * 60)
    print("EJEMPLOS DE ASIGNACIONES")
    print("=" * 60)
    
    # Ejemplo 1: Encuesta con alta satisfacción
    ejemplos_alta = df_resultado[df_resultado['satisfaccion_general'] >= 4].head(2)
    if len(ejemplos_alta) > 0:
        print("\n--- Ejemplo: Alta satisfacción (4-5) ---")
        for idx, row in ejemplos_alta.iterrows():
            print(f"\nSatisfacción: {row['satisfaccion_general']}")
            print(f"Comentario: {row['comentarios'][:100]}...")
    
    # Ejemplo 2: Encuesta con baja satisfacción
    ejemplos_baja = df_resultado[df_resultado['satisfaccion_general'] <= 2].head(2)
    if len(ejemplos_baja) > 0:
        print("\n--- Ejemplo: Baja satisfacción (1-2) ---")
        for idx, row in ejemplos_baja.iterrows():
            print(f"\nSatisfacción: {row['satisfaccion_general']}")
            print(f"Comentario: {row['comentarios'][:100]}...")
    
    # Ejemplo 3: Encuesta con satisfacción media
    ejemplos_media = df_resultado[df_resultado['satisfaccion_general'] == 3].head(2)
    if len(ejemplos_media) > 0:
        print("\n--- Ejemplo: Satisfacción media (3) ---")
        for idx, row in ejemplos_media.iterrows():
            print(f"\nSatisfacción: {row['satisfaccion_general']}")
            print(f"Comentario: {row['comentarios'][:100]}...")
    
    # 5. Verificar coherencia
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE COHERENCIA")
    print("=" * 60)
    
    # Verificar que comentarios con alta satisfacción están en encuestas con alta satisfacción
    comentarios_no_vacios = df_resultado[df_resultado['comentarios'] != '']
    if len(comentarios_no_vacios) > 0:
        print(f"\nComentarios asignados: {len(comentarios_no_vacios)}")
        print(f"Satisfacción promedio de encuestas con comentarios: {comentarios_no_vacios['satisfaccion_general'].mean():.2f}")
        print(f"Satisfacción promedio general: {df_resultado['satisfaccion_general'].mean():.2f}")
    
    print("\n" + "=" * 60)
    print("MERCEO COMPLETADO EXITOSAMENTE")
    print("=" * 60)


if __name__ == "__main__":
    main()

