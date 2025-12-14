# Proyecto Final: Análisis de Marketing y Satisfacción - IMMUNE

## Objetivo del Proyecto

Desarrollo de un ecosistema completo de análisis de marketing y satisfacción que integra:
- **Extracción y generación de datos** mediante web scraping y síntesis con LLMs
- **Análisis exploratorio (EDA)** y **clustering** para segmentación de usuarios
- **Dashboard interactivo** en Power BI para visualización de métricas de negocio
- **Agente conversacional inteligente** para consulta natural de datos

El objetivo es crear un pipeline end-to-end que permita desde la captura de datos hasta la toma de decisiones basada en insights accionables.

---

## 1. Extracción y Generación de Datos

### 1.1 Web Scraping de Cursos (`EDA y clustering/Proyecto_Capstone.ipynb`)

Extracción automatizada del catálogo oficial de IMMUNE mediante:
- **Fuente**: https://immune.institute/programas/
- **Tecnología**: GPT-4o-mini para parsing inteligente de HTML
- **Output**: `cursos_immune.xlsx` (31 programas)
- **Campos extraídos**: 
  - Identificación: `id_curso`, `nombre`, `tipo_de_programa`
  - Características: `horas_totales`, `duracion`, `modalidad`, `sector`
  - Comercial: `precio`, `financiacion`, `salidas_profesionales`

### 1.2 Generación de Datos Sintéticos

Dado que no se disponen de datos reales, se generan datasets sintéticos coherentes usando LLMs:

#### **Formularios de Registro** (700 registros)
- **Script**: Generación con GPT-4o-mini
- **Output**: `formularios.xlsx`
- **Campos**: Perfil demográfico, académico y laboral de usuarios registrados
- **Coherencia**: Ciudad-País, Edad-Experiencia, Formación-Sector laboral

#### **Métricas de Tráfico Web** (3000 registros)
- **Script**: `metricas_immune/generar_df_immune_metricas.py`
- **Output**: `Immune_metricas.csv`
- **Simulación**: Sesiones de Google Analytics/Ads con seguimiento cross-device
- **Período**: Enero 2024 - Noviembre 2025

#### **Encuestas de Satisfacción** (500 registros)
- **Script**: `metricas_immune/generar_feedbacks_sinteticos.py`
- **Output**: `feedbacks/Feedbacks.csv`
- **Contenido**: Valoraciones de profesorado, contenidos e infraestructura

---

## 2. Análisis Exploratorio de Datos (EDA)

### 2.1 Análisis de Métricas Web (`Immune_metricas_PBI.xlsx`)

**Variables numéricas analizadas**:
- `tiempo_en_pagina`: Distribución con outliers identificados (>800s), moda en ~60s
- Creación de columna `solicita_informacion` (binaria) para análisis de conversión

**Variables categóricas analizadas**:
- `origen_plataforma`: 4 canales (LinkedIn, Instagram, Google, Google Ads)
- `dispositivo`: 3 tipos (mobile, desktop, tablet)
- `pais`: 9 países, 26 ciudades
- Temporalidad: 2 años completos, 12 meses, distribución por día de semana y hora

**Patrones identificados**:
- Pico de consultas: Sábados a las 13:00h
- Tasa de conversión programa_oferta_click: ~X%

### 2.2 Análisis de Formularios (`formularios_PBI.xlsx`)

**Estadísticas descriptivas**:
- **Edad**: μ=30, σ=8, rango [18, 50] sin outliers
- **Experiencia laboral**: μ=6 años, rango [0, 29], outliers coherentes con edad
- **Validación**: Correlación lineal positiva entre edad y experiencia

**Distribuciones cualitativas**:
- `pais`, `genero`, `area_de_interes_para_formarse`
- `titulacion_academica`, `area_de_estudios`, `motivo_de_la_formacion`

### 2.3 Análisis de Feedbacks (`feedbacks_PBI.csv`)

**Segmentación de encuestas**:
- Por año, edición del curso, tipo de programa y modalidad
- Extracción de variables temporales para análisis de tendencias

---

## 3. Modelo de Clustering (K-Means)

### 3.1 Objetivo

Segmentación de usuarios en base a comportamiento web y perfil registrado para personalización de estrategias de marketing.

### 3.2 Metodología

**Preprocesamiento**:
1. Estandarización de variables numéricas con `StandardScaler`
2. Reducción dimensional con **PCA** a 2 componentes para visualización
3. One-hot encoding de variables categóricas

**Optimización de K**:
- **Método del codo**: Inercia vs. número de clusters
- **Coeficiente de silueta**: Validación de cohesión interna
- **K óptimo seleccionado**: 5 clusters

### 3.3 Perfiles de Clusters Identificados

| Cluster | Perfil | Edad | Experiencia | Motivación | Match con Immune |
|---------|--------|------|-------------|------------|------------------|
| **0** | Graduados en transición | Media | Media | Cambio de empleo | Media |
| **1** | Profesionales tech | Media-Alta | Alta | Ampliar conocimiento | **Alta** |
| **2** | Profesionales senior | Alta | Muy alta | Especialización | Media |
| **3** | Jóvenes sin experiencia | Baja | Nula | Búsqueda de empleo | Baja |
| **4** | Recualificación profesional | Media | Media | Cambio de sector | **Alta** |

**Insights de negocio**:
- Clusters 1 y 4 muestran mayor tasa de matriculación
- Cluster 3 realiza más consultas pero menor conversión (alta exploración)
- Cluster 2 tiene búsqueda más dirigida (pocas consultas, alta intención)

---

## 4. Dashboard Power BI

### 4.1 Arquitectura de Datos

**Modelo en estrella** con extensiones copo de nieve:

**Tablas Fact**:
- `Immune_metricas_PBI`: Métricas de tráfico y conversión
- `Feedbacks_PBI`: Respuestas de encuestas

**Tablas Dimension**:
- `Cursos_immune`: Catálogo de programas (31 cursos)
- `Formularios_PBI`: Perfil de usuarios registrados
- `Radar_Feedbacks_Profesor`: KPIs de evaluación docente
- `Radar_Feedbacks_Clases`: KPIs de metodología e infraestructura
- `Medidas`: Tabla de medidas DAX

**Relaciones**:
```
Immune_metricas[programa_oferta_click] ↔ Cursos[id_curso]
Immune_metricas[id_usuario] ↔ Formularios[id_usuario]
Feedbacks[id_curso] ↔ Cursos[id_curso]
Feedbacks[id_usuario] ↔ Formularios[id_usuario]
Feedbacks[id_curso] ↔ Radar_Feedbacks_Profesor[id_curso]
Feedbacks[id_curso] ↔ Radar_Feedbacks_Clases[id_curso]
```

### 4.2 Páginas del Dashboard

#### **Página 1: Feedbacks**
- KPIs principales: Nº cursos, alumnos, encuestas, % positivas/negativas (umbral: 3.5/5)
- Tabla dinámica: Listado de programas con métricas de satisfacción
- Gráficos: Desglose por modalidad, tipo de programa, edad y evolución temporal

#### **Página 2: KPIs Feedbacks**
- Gráficos radar con medias de categorías:
  - **Profesor**: Preparación, dominio, atención, puntualidad, NPS
  - **Clases**: Organización, contenidos, dificultad, utilidad

#### **Página 3: Immune (Métricas de Marketing)**
- Distribución temporal: Visitas y matriculaciones (serie temporal)
- Análisis de canales: Impacto de origen_plataforma en conversión
- Mapa geográfico: Distribución de interesados por país
- Comparativa de programas: Top más/menos visitados y su tasa de conversión

#### **Páginas de Detalle**
- Drill-through desde visualizaciones principales
- Análisis específicos por programa, usuario o período

### 4.3 Preguntas de Negocio Respondidas

1. ¿Cómo se distribuyen las visitas a la página de Immune en el tiempo? ¿Y las matriculaciones?
2. ¿Qué influencia tienen los canales por donde acceden los interesados?
3. ¿Desde qué países llegan interesados por los programas?
4. ¿Qué programas son los más y menos visitados y qué proporción de matriculados tienen?
5. ¿Qué valoraciones obtenemos de nuestros programas y cómo evolucionan en el tiempo?
6. ¿Las valoraciones son positivas (puntuación superior a 3.5/5) o negativas?
7. ¿Cómo se distribuyen estas categorías entre los distintos tipos de programas (bootcamp, máster, cursos, etc.) y modalidades?
8. ¿Las puntuaciones obtenidas se deben al profesor o a las clases?

---

## 5. Immune Agent (Sistema Conversacional)

### 5.1 Arquitectura

Sistema multi-agente basado en **Google ADK** y **Gemini 2.5 Flash**:
- **Router Agent**: Guía al usuario para filtrar cursos por sector, modalidad, precio o nombre
- **Analista Agent**: Procesa feedbacks, calcula KPIs y genera informes cualitativos
- **Tools**: Búsqueda en catálogo, análisis de satisfacción, rankings de cursos

### 5.2 Capacidades

- Consulta natural sobre catálogo de cursos
- Análisis de satisfacción por programa específico
- Generación de informes ejecutivos con fortalezas y debilidades
- Rankings de cursos basados en valoraciones
- Manejo de ambigüedad con fallbacks contextuales

---

---

# Diccionario de Variables

## DataFrame: Immune_metricas.csv

Métricas de sesión y conversión por usuario único.

| Variable | Tipo | Descripción | Valores / Reglas |
|----------|------|-------------|------------------|
| `usuario_temp` | string | ID de sesión temporal | `TEMP_######` |
| `origen_plataforma` | string | Fuente de adquisición | LinkedIn, Instagram, Google, Google Ads |
| `tiempo_en_pagina` | int | Segundos en el sitio | 10 - 900 s |
| `fecha_hora` | datetime | Timestamp de la sesión | ISO 8601 (hasta 29-nov-2025) |
| `Localizacion` | string | Ciudad y país | "Madrid, España", "Lima, Perú", etc. |
| `programa_oferta_click` | string | Slug del curso visitado | IDs oficiales (`C####`) o nulo |
| `Inicio_sesion` | bool | ¿Inició sesión? | True/False |
| `Id_usuario` | string | ID único de alumno | `U####` (4 dígitos) |
| `Dispositivo` | string | Dispositivo de acceso | mobile, desktop, tablet |
| `Matriculado` | bool | ¿Se matriculó en esta sesión? | True (implica `Inicio_sesion=True` y `Id_usuario` válido) |

## DataFrame: Feedbacks.csv

Resultados de la encuesta de satisfacción.

### 1. Identificación y Contexto

| Variable | Tipo | Descripción | Valores / Reglas |
|----------|------|-------------|------------------|
| `Id_encuesta` | string | ID único de respuesta | `E####` |
| `id_usuario` | string | ID del alumno | `U####` (coincide con métricas) |
| `Id_curso` | string | Código del curso evaluado | `C####` (del catálogo oficial) |
| `Tipo_clase` | string | Modalidad cursada | "Online" o "Presencial" (según curso) |
| `fecha` | datetime | Fecha de la encuesta | ISO 8601 |

### 2. Variables de Evaluación (Escala 1-5)

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `preparado_clases` | int | Preparación del profesor |
| `dominio_materia` | int | Dominio de la materia |
| `mantiene_atencion` | int | Capacidad de mantener atención |
| `relaciona_con_ejemplos` | int | Uso de ejemplos teóricos |
| `ejemplos_mundo_profesional` | int | Ejemplos del mundo real |
| `accesible_y_atiende_consultas` | int | Atención a dudas |
| `fomenta_colaboracion` | int | Fomento del trabajo en equipo |
| `puntualidad` | int | Puntualidad del docente |
| `referencias_en_redes` | int | Uso de referencias externas |
| `recomendaria_profesor` | int | NPS del profesor |

### 3. Metodología y Contenidos (Escala 1-5)

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `organiza_actividades` | int | Organización general |
| `contenidos_adecuados` | int | Calidad del temario |
| `grado_dificultad` | int | Dificultad (1=Fácil, 5=Difícil) |
| `conocimientos_utiles_futuro` | int | Utilidad laboral percibida |

### 4. Infraestructura y Clase (Matriz cualitativa)

Valores: "Pésimo", "Mal", "Regular", "Bien", "Genial" (o "No aplica").

| Variable | Tipo | Regla de integridad |
|----------|------|---------------------|
| `clase_duracion` | string | Aplica siempre |
| `clase_horario` | string | Aplica siempre |
| `clase_conveniencia_dia` | string | Aplica siempre |
| `clase_calidad_conexion` | string | "No aplica" si `Tipo_clase == Presencial` |
| `clase_visibilidad_pantalla` | string | "No aplica" si `Tipo_clase == Presencial` |
| `clase_calidad_audio` | string | "No aplica" si `Tipo_clase == Presencial` |

### 5. Soporte y Satisfacción Global

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `velocidad_respuesta` | int | Rapidez de soporte (1-5) |
| `utilidad_anuncios` | int | Relevancia de avisos (1-5) |
| `satisfaccion_general` | int | Valoración global del curso (1-5) |
| `comentarios` | string | Feedback abierto (texto libre) |

## DataFrame: Feedbacks.csv (recordatorio)

Véase sección anterior; ya no se genera Metricas_campanas.csv.
