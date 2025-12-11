# Capstone Project - Análisis de Marketing y Satisfacción

Proyecto final de análisis de marketing sobre el alcance de las campañas de captación de alumnos y satisfacción post-inscripción para IMMUNE.

## Objetivo

Crear un pipeline de ML y análisis que permita introducir métricas de negocio y obtener resultados útiles para la toma de decisiones, integrando un **Agente Inteligente** para la consulta natural de estos datos.

## Estructura del Proyecto

### Generación de Datos
- `metricas_immune/generar_df_immune_metricas.py`: Script para generar métricas de tráfico y conversión (`Immune_metricas.csv`).
- `metricas_immune/generar_feedbacks_sinteticos.py`: Script para generar encuestas de satisfacción (`Feedbacks.csv`).
- `cursos_immune/`: Contiene el catálogo de cursos (`cursos_immune_agente.xlsx`).

### Immune Agent
- `immune_agent/agent.py`: Sistema multi-agente (Router + Analista) basado en Google Gemini.
- `immune_agent/secrets.env`: Configuración de claves de API (Gemini, Google Drive).
- `immune_agent/fallbacks.txt`: Frases de respuesta para manejo de errores/ambigüedad.

### Documentación y Datos
- `Arquitectura.md`: Documentación técnica y diccionario de variables.
- `Immune_metricas_v3.csv`: Dataset de métricas de negocio.
- `feedbacks/Feedbacks.csv`: Dataset de respuestas de satisfacción.

## Módulos del Pipeline

### 1. Datos Sintéticos
Los datos se generan alineados con la estructura real de negocio:
- **Tráfico y Conversión**: Métricas de Google Analytics/Ads simulando el funnel de ventas.
- **Satisfacción (Feedbacks)**: Encuestas detalladas sobre profesorado, contenidos e infraestructura, vinculadas a los cursos oficiales.

### 2. Immune Agent
Un sistema de IA diseñado para democratizar el acceso a la información del proyecto.
- **Arquitectura**: Basado en `google-adk`, utiliza modelos Gemini 2.5 Flash.
- **Capacidades**:
  - **Buscador (Router)**: Guía al usuario para filtrar cursos por sector, modalidad, precio o nombre.
  - **Analista de Datos**: Procesa los feedbacks de un curso específico, calcula métricas (KPIs) y genera un informe cualitativo sobre fortalezas y debilidades.
  - **Métricas Globales**: Ofrece rankings de cursos y resúmenes ejecutivos de satisfacción general.

## Uso

### Generación de Datos
```bash
# Generar métricas de tráfico
python metricas_immune/generar_df_immune_metricas.py

# Generar feedbacks sintéticos
python metricas_immune/generar_feedbacks_sinteticos.py
```

### Ejecución del Agente
Para interactuar con el Immune Agent:

1. Asegúrate de tener las variables de entorno configuradas en `immune_agent/secrets.env` (API Key de Google Gemini).
2. Ejecuta el agente:
```bash
python immune_agent/agent.py
```

## Recursos Adicionales

- **Resumen Visual**: [Esquema en Excalidraw](https://excalidraw.com/#room=b2f4fb4c0ce095979505,gzZQ7jnj6MIlwEKvtgGA0g)
- **Documentación Técnica**: Ver `Arquitectura.md` para el diccionario de variables y estructura de los DataFrames.
