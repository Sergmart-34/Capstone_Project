# Capstone Project - Análisis de Marketing y Satisfacción

Proyecto final de análisis de marketing sobre el alcance de las campañas de captación de alumnos y satisfacción post-inscripción para IMMUNE.

## Objetivo

Crear un pipeline de ML y análisis que permita introducir métricas de negocio y obtener resultados útiles para la toma de decisiones.

## Estructura del Proyecto

- `metricas_immune/generar_df_immune_metricas.py`: Script para generar Immune_metricas.csv
- `metricas_immune/generar_feedbacks_sinteticos.py`: Script para generar Feedbacks.csv
- `Arquitectura.md`: Documentación completa del proyecto y diccionario de variables
- `Metricas_campanas.csv`: Métricas de Google Analytics y Facebook Ads
- `Feedbacks.csv`: Respuestas de encuesta de satisfacción

## Datos Sintéticos

Los datos sintéticos se generan basándose en las métricas exactas que proporcionan:
- **Google Analytics**: Métricas de campañas de marketing digital
- **Facebook Ads**: Métricas de campañas publicitarias
- **Google Forms**: Encuestas de satisfacción de estudiantes

## Uso

```bash
# Métricas Immune
python metricas_immune/generar_df_immune_metricas.py

# Feedbacks
python metricas_immune/generar_feedbacks_sinteticos.py
```


Enlace para el documento de resumen visual del proyecto : https://excalidraw.com/#room=b2f4fb4c0ce095979505,gzZQ7jnj6MIlwEKvtgGA0g


## Documentación

Ver `Arquitectura.md` para la documentación completa del proyecto, incluyendo:
- Diccionario detallado de variables
- Especificaciones de los DataFrames
- Estructura de datos
