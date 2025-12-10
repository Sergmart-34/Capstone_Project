# Proyecto Final: Análisis de Marketing y Satisfacción - IMMUNE

## Objetivo del Proyecto

Análisis de marketing sobre el alcance de las campañas de captación de alumnos y satisfacción post-inscripción. El objetivo es crear un pipeline de ML y análisis que permita introducir métricas de negocio y obtener resultados útiles para la toma de decisiones.

## Datos Sintéticos

Dado que aún no se disponen de datos reales de la escuela, se generan DataFrames sintéticos alineados con el catálogo oficial de cursos y las métricas de las plataformas utilizadas:

- **Google Analytics & Facebook Ads**: Métricas unificadas de campañas de marketing digital (`Immune_metricas.csv`).
- **Google Forms**: Encuestas de satisfacción de estudiantes (`feedbacks/Feedbacks.csv`).

### Scripts de Generación

1. **`metricas_immune/generar_df_immune_metricas.py`** genera:
   - **`Immune_metricas.csv`** (3000 registros):
     - Sesiones de usuario con seguimiento cross-device y cross-platform.
     - Tagging de oferta (`programa_oferta_click`) consistente con el catálogo.
     - IDs de usuario normalizados (`U####`) compartidos con formularios y feedback.
     - Rango temporal: enero 2024 a noviembre 2025 (sin fechas futuras).

2. **`metricas_immune/generar_feedbacks_sinteticos.py`** genera:
   - **`feedbacks/Feedbacks.csv`** (500 registros):
     - Encuestas de satisfacción post-curso.
     - Modalidad (`Tipo_clase`) alineada con la oferta oficial del curso.
     - Campos de conectividad marcados como "No aplica" para modalidad Presencial.

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
