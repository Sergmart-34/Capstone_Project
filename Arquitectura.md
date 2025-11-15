# Proyecto Final: Análisis de Marketing y Satisfacción - IMMUNE

## Objetivo del Proyecto

Análisis de marketing sobre el alcance de las campañas de captación de alumnos y satisfacción post-inscripción. El objetivo es crear un pipeline de ML y análisis que permita introducir métricas de negocio y obtener resultados útiles para la toma de decisiones.

## Datos Sintéticos

Dado que aún no se disponen de datos reales de la escuela, se generan DataFrames sintéticos basados en las métricas exactas que proporcionan las plataformas utilizadas:

- **Google Analytics**: Métricas de campañas de marketing digital
- **Facebook Ads**: Métricas de campañas publicitarias
- **Google Forms**: Encuestas de satisfacción de estudiantes

### Script de Generación

`generar_datos_sinteticos.py` genera dos DataFrames:

1. **`Metricas_campanas.csv`** (500 registros)
   - Métricas de Google Analytics: sesiones, usuarios, conversiones, ingresos, etc.
   - Métricas de Facebook Ads: impresiones, alcance, clics, gasto, CTR, CPC, etc.
   - Período: año lectivo (septiembre 2024 - junio 2025)

2. **`Metricas_satisfaccion.csv`** (500 registros)
   - Respuestas de encuesta de satisfacción de estudiantes
   - Distribución: año lectivo con media de 20 estudiantes por mes
   - Variables según especificación de Google Forms (ver sección siguiente)

---

# Diccionario de Variables

## DataFrame: Metricas_campanas.csv

### 1. Identidad / Contexto

| Variable | Tipo | Descripción | Valores Posibles |
|----------|------|-------------|------------------|
| `fecha` | datetime | Fecha de registro | 2024-01-01 a 2024-12-31 |
| `mes` | int | Mes del año | 1-12 |
| `dia_semana` | string | Día de la semana | "Monday", "Tuesday", etc. |
| `franja_horaria` | string | Franja horaria del día | "manana", "tarde", "noche" |
| `periodo_academico` | string | Período académico | "pre_matricula", "captacion", "cierre", "post_matricula" |
| `plataforma` | string | Plataforma publicitaria | "Google Ads", "Meta Ads", "LinkedIn Ads", "TikTok Ads" |
| `fuente` | string | Fuente del tráfico | "google", "facebook", "instagram", "linkedin", "newsletter" |
| `medio` | string | Medio de adquisición | "cpc", "social", "email", "display", "video" |
| `canal_agrupado` | string | Canal agrupado | "search", "paid_social", "display_video", "email_own", "organic_like" |
| `campana_id` | string | ID de campaña | "100"-"999" |
| `campana_nombre` | string | Nombre de campaña | "Campaña_" + ID |
| `conjunto_anuncios_id` | string | ID conjunto anuncios | "1000"-"9999" |
| `conjunto_anuncios` | string | Nombre conjunto anuncios | "Conjunto_" + ID |
| `anuncio_id` | string | ID de anuncio | "10000"-"99999" |
| `anuncio_nombre` | string | Nombre de anuncio | "Anuncio_" + ID |
| `landing_url` | string | URL de landing page | "https://immune.institute/landing/[area]" |
| `ciudad_usuario` | string | Ciudad del usuario | "Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Online" |
| `pais_usuario` | string | País del usuario (código ISO) | "ES", "PT", "FR", "IT", "MX", "AR", "CO" |
| `device_category` | string | Categoría de dispositivo | "desktop", "mobile", "tablet" |

### 2. Perfil del Usuario

| Variable | Tipo | Descripción | Valores Posibles |
|----------|------|-------------|------------------|
| `edad` | int | Edad del usuario | 18-55 |
| `genero` | string | Género | "M", "F", "Otro", "Prefiere_no_decirlo" |
| `nivel_estudios` | string | Nivel de estudios | "ESO", "Bachillerato", "FP", "Grado universitario", "Postgrado/Master", "Doctorado" |
| `situacion_laboral` | string | Situación laboral | "estudiante", "trabajando", "en_transicion", "desempleado" |
| `interes_area` | string | Área de interés | "IA", "Ciberseguridad", "Data", "Full-Stack", "Cloud", "UX/UI" |
| `experiencia_previa_tech` | int | Experiencia previa en tech | 0 (bajo), 1 (medio), 2 (alto) |
| `objetivo` | string | Objetivo profesional | "first_job", "reskilling", "upskilling", "emprendimiento" |
| `capacidad_inversion` | string | Capacidad de inversión | "baja", "media", "alta" |

### 3. Comportamiento Web

| Variable | Tipo | Descripción | Rango/Valores |
|----------|------|-------------|---------------|
| `sesiones` | int | Número de sesiones web | Derivado de clics (0.8-1.1x) |
| `usuarios` | int | Usuarios únicos | 60-100% de sesiones |
| `nuevos_usuarios` | int | Usuarios nuevos | 30-80% de usuarios |
| `usuarios_recurrentes` | int | Usuarios recurrentes | usuarios - nuevos_usuarios |
| `paginas_vistas` | int | Total páginas vistas | sesiones * (1-6) |
| `paginas_por_sesion` | float | Promedio páginas por sesión | paginas_vistas / sesiones |
| `engagement_rate` | float | Tasa de engagement | 0.1 - 0.9 |
| `scroll_max` | float | Scroll máximo (%) | 30-100 |
| `eventos_interaccion` | int | Eventos de interacción | sesiones * (0.5-3.0) |
| `eventos_form_view` | int | Visualizaciones de formulario | sesiones * (0.1-0.8) |
| `eventos_form_start` | int | Inicios de formulario | eventos_form_view * (0.4-0.9) |
| `eventos_form_submit` | int | Envíos de formulario | eventos_form_start * (0.3-0.9) |

### 4. Funnel Educativo / Negocio

| Variable | Tipo | Descripción | Rango/Valores |
|----------|------|-------------|---------------|
| `leads` | int | Leads generados | eventos_form_submit * (0.5-1.0) |
| `leads_cualificados` | int | Leads cualificados | leads * (0.4-0.9) |
| `entrevistas_agendadas` | int | Entrevistas agendadas | leads_cualificados * (0.5-0.95) |
| `entrevistas_realizadas` | int | Entrevistas realizadas | entrevistas_agendadas * (0.7-1.0) |
| `matriculas` | int | Matrículas completadas | entrevistas_realizadas * (0.2-0.8) |
| `importe_matricula` | float | Importe de matrícula | 4,000 - 12,000 € |
| `ingresos` | float | Ingresos totales | matriculas * importe_matricula |
| `conversiones` | int | Conversiones (equivalente a leads) | leads |
| `tasa_conversion` | float | Tasa de conversión | conversiones / sesiones |

### 5. Paid Media

| Variable | Tipo | Descripción | Rango/Valores |
|----------|------|-------------|---------------|
| `impresiones` | int | Impresiones del anuncio | 500 - 50,000 |
| `alcance` | int | Alcance único | 200 - 20,000 (≤ impresiones) |
| `frecuencia` | float | Frecuencia de exposición | impresiones / alcance |
| `clics` | int | Clics en el anuncio | impresiones * CTR (mínimo 1) |
| `gasto` | float | Gasto total | clics * CPC |
| `ctr` | float | Click-Through Rate | 0.005 - 0.20 (0.5% - 20%) |
| `cpc` | float | Costo por clic | 0.3 - 5.0 € |
| `cpm` | float | Costo por mil impresiones | (gasto / impresiones) * 1000 |
| `cpl` | float | Costo por lead | gasto / leads |
| `cpmatricula` | float | Costo por matrícula | gasto / matriculas |
| `roas` | float | Return on Ad Spend | ingresos / gasto |

### 6. Creatividad

| Variable | Tipo | Descripción | Valores Posibles |
|----------|------|-------------|------------------|
| `tipo_creatividad` | string | Tipo de creatividad | "imagen", "video", "carrusel" |
| `formato_creatividad` | string | Formato de la creatividad | "feed", "stories", "shorts/reels", "search", "display" |
| `cta_mensaje` | string | Mensaje del CTA | "Inscríbete ahora", "Reserva tu plaza", "Descargar guía", "Agenda una llamada", "Solicita información" |
| `angulo_mensaje` | string | Ángulo del mensaje | "empleabilidad", "salario", "vocacion_tech", "flexibilidad", "internacional" |
| `duracion_video_segundos` | int | Duración del video (si aplica) | 10-120 segundos (0 si no es video) |
| `color_dominante` | int | Color dominante (cluster) | 0-4 |

### 7. Atribución

| Variable | Tipo | Descripción | Valores Posibles |
|----------|------|-------------|------------------|
| `modelo_atribucion` | string | Modelo de atribución | "last_click", "first_click", "data_driven" |
| `conversiones_last_click` | int | Conversiones (last click) | conversiones * factor (0.6-1.1) |
| `conversiones_data_driven` | int | Conversiones (data driven) | conversiones * factor (0.8-1.2) |

### 8. Features ML Derivadas

| Variable | Tipo | Descripción | Fórmula |
|----------|------|-------------|---------|
| `interaccion_media` | float | Interacción media por sesión | eventos_interaccion / sesiones |
| `indice_intencion_form` | float | Índice de intención de formulario | eventos_form_start / sesiones |
| `porcentaje_scroll` | float | Porcentaje de scroll | scroll_max / 100 |
| `engagement_relevante` | float | Engagement relevante | engagement_rate * paginas_por_sesion |
| `eficiencia_creatividad` | float | Eficiencia de creatividad | clics / alcance |
| `eficiencia_gasto` | float | Eficiencia del gasto | conversiones / gasto |
| `valor_prospecto` | float | Valor del prospecto | ingresos / leads |
| `ratio_frecuencia` | float | Ratio de frecuencia | frecuencia |
| `propension_matricula` | float | Propensión a matrícula | matriculas / leads |
| `data_health_score` | int | Score de salud de datos | 100 - penalización (0-100) |

---

## DataFrame: Metricas_satisfaccion.csv

### Variable Temporal

| Variable | Tipo | Descripción | Rango | Notas |
|----------|------|-------------|-------|-------|
| `fecha` | datetime | Fecha de respuesta a la encuesta | 2024-09-01 a 2025-06-30 | Distribuido a lo largo del año lectivo |

### Variables de Evaluación del Profesor (Escala 1-5)

Todas estas variables son enteros del 1 al 5, donde 1 = Muy bajo/Muy malo y 5 = Muy alto/Muy bueno.

| Variable | Tipo | Descripción | Valores | Distribución |
|----------|------|-------------|---------|--------------|
| `preparado_clases` | int | Nivel de preparación del profesor para las clases | 1-5 | Sesgo positivo (3-5) |
| `dominio_materia` | int | Dominio del profesor sobre la materia | 1-5 | Sesgo positivo (3-5) |
| `mantiene_atencion` | int | Capacidad del profesor para mantener la atención | 1-5 | Sesgo positivo (3-5) |
| `relaciona_con_ejemplos` | int | Uso de ejemplos para relacionar conceptos | 1-5 | Sesgo positivo (3-5) |
| `ejemplos_mundo_profesional` | int | Uso de ejemplos del mundo profesional | 1-5 | Sesgo positivo (3-5) |
| `accesible_y_atiende_consultas` | int | Accesibilidad y atención a consultas | 1-5 | Sesgo positivo (3-5) |
| `fomenta_colaboracion` | int | Fomento de la colaboración entre estudiantes | 1-5 | Sesgo positivo (3-5) |
| `puntualidad` | int | Puntualidad del profesor | 1-5 | Sesgo positivo (3-5) |
| `referencias_en_redes` | int | Uso de referencias en redes sociales | 1-5 | Distribución equilibrada |
| `recomendaria_profesor` | int | Probabilidad de recomendar al profesor | 1-5 | Sesgo positivo (3-5) |

### Variables de Impartición / Metodología (Escala 1-5)

| Variable | Tipo | Descripción | Valores | Distribución |
|----------|------|-------------|---------|--------------|
| `organiza_actividades` | int | Nivel de organización de actividades | 1-5 | Sesgo positivo (3-5) |
| `contenidos_adecuados` | int | Adecuación de los contenidos | 1-5 | Sesgo positivo (3-5) |
| `grado_dificultad` | int | Grado de dificultad percibido | 1-5 | Distribución equilibrada<br>*(1 = muy fácil, 5 = muy difícil)* |
| `conocimientos_utiles_futuro` | int | Utilidad percibida de los conocimientos para el futuro | 1-5 | Sesgo positivo (3-5) |

### Variables de Valoración de Clases (Matriz)

Estas variables son texto literal con las opciones de la matriz de Google Forms.

| Variable | Tipo | Descripción | Valores Posibles | Distribución |
|----------|------|-------------|------------------|--------------|
| `clase_duracion` | string | Valoración de la duración de las clases | "Pésimo", "Mal", "Regular", "Bien", "Genial" | Sesgo positivo |
| `clase_horario` | string | Valoración del horario de las clases | "Pésimo", "Mal", "Regular", "Bien", "Genial" | Sesgo positivo |
| `clase_conveniencia_dia` | string | Conveniencia del día de la clase | "Pésimo", "Mal", "Regular", "Bien", "Genial" | Sesgo positivo |
| `clase_calidad_conexion` | string | Calidad de la conexión (para clases online) | "Pésimo", "Mal", "Regular", "Bien", "Genial" | Distribución equilibrada |
| `clase_visibilidad_pantalla` | string | Visibilidad de la pantalla | "Pésimo", "Mal", "Regular", "Bien", "Genial" | Sesgo positivo |
| `clase_calidad_audio` | string | Calidad del audio | "Pésimo", "Mal", "Regular", "Bien", "Genial" | Sesgo positivo |

### Variables de Soporte y Comunicaciones (Escala 1-5)

| Variable | Tipo | Descripción | Valores | Distribución |
|----------|------|-------------|---------|--------------|
| `velocidad_respuesta` | int | Velocidad de respuesta a consultas | 1-5 | Sesgo positivo (3-5) |
| `utilidad_anuncios` | int | Utilidad percibida de los anuncios/comunicaciones | 1-5 | Distribución equilibrada |

### Variables Categóricas

| Variable | Tipo | Descripción | Valores Posibles | Distribución |
|----------|------|-------------|------------------|--------------|
| `tipo_programa` | string | Modalidad del programa cursado | "Online", "Presencial" | 70% Online, 30% Presencial |

### Variables de Satisfacción General

| Variable | Tipo | Descripción | Valores | Distribución |
|----------|------|-------------|---------|--------------|
| `satisfaccion_general` | int | Satisfacción general con el módulo | 1-5 | Correlacionada con otras métricas<br>Sesgo positivo (3-5) |

### Variables de Texto Libre

| Variable | Tipo | Descripción | Valores | Notas |
|----------|------|-------------|---------|-------|
| `comentarios` | string | Comentarios abiertos del estudiante | Texto libre | 50% vacíos, 50% con texto |

---

# Variables encuesta de satisfacción IMMUNE

## 1. Variables de evaluación del profesor (escala 1–5)
Estas preguntas se cuantifican como números enteros del 1 al 5.

- preparado_clases
- dominio_materia
- mantiene_atencion
- relaciona_con_ejemplos
- ejemplos_mundo_profesional
- accesible_y_atiende_consultas
- fomenta_colaboracion
- puntualidad
- referencias_en_redes
- recomendaria_profesor

## 2. Impartición / metodología (escala 1–5)
Cuantificación: enteros del 1 al 5.

- organiza_actividades
- contenidos_adecuados
- grado_dificultad   *(1 = muy fácil, 5 = muy difícil)*
- conocimientos_utiles_futuro

## 3. Valoración de clases en directo/presencial (matriz)
Google Forms devuelve cada fila como una columna independiente.  
Cuantificación: texto literal de la opción elegida:  
“Pésimo”, “Mal”, “Regular”, “Bien”, “Genial”.

Columnas exportadas:

- clase_duracion
- clase_horario
- clase_conveniencia_dia
- clase_calidad_conexion
- clase_visibilidad_pantalla
- clase_calidad_audio

## 4. Soporte y comunicaciones (escala 1–5)
Cuantificación: enteros 1–5.

- velocidad_respuesta
- utilidad_anuncios

## 5. Tipo de programa cursado (categoría)
Cuantificación: texto literal.

Valores posibles:
- "Online"
- "Presencial"

Variable:
- tipo_programa

## 6. Satisfacción general módulo (escala 1–5)
Cuantificación: enteros 1–5.

- satisfaccion_general

## 7. Comentarios abiertos
Cuantificación: texto libre (string).

- comentarios
