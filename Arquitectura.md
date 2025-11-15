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

### Variables Comunes

| Variable | Tipo | Descripción | Valores Posibles | Plataforma |
|----------|------|-------------|------------------|------------|
| `fecha` | datetime | Fecha de registro de la métrica | 2024-09-01 a 2025-06-30 | Ambas |
| `plataforma` | string | Plataforma de origen de los datos | "Google Analytics", "Facebook Ads" | Ambas |
| `campana_nombre` | string | Nombre de la campaña de marketing | Varios (ej: "Master Data Science 2024", "Bootcamp Full Stack") | Ambas |

### Variables Específicas de Google Analytics

| Variable | Tipo | Descripción | Rango/Valores | Unidad |
|----------|------|-------------|---------------|--------|
| `fuente` | string | Fuente del tráfico web | "google", "facebook", "direct", "organic", "referral", "email" | - |
| `medio` | string | Medio de adquisición | "cpc", "organic", "referral", "email", "display", "social" | - |
| `sesiones` | int | Número total de sesiones iniciadas | 50 - 2000 | sesiones |
| `usuarios` | int | Número de usuarios únicos | 30 - 1900 (70-95% de sesiones) | usuarios |
| `paginas_vistas` | int | Total de páginas vistas | 75 - 9000 (1.5-4.5x sesiones) | páginas |
| `tasa_rebote` | float | Porcentaje de sesiones de una sola página | 30.0 - 75.0 | % |
| `duracion_promedio_sesion` | float | Duración promedio de sesión | 60.0 - 600.0 | segundos |
| `conversiones` | int | Número de conversiones completadas | 0 - 200 (hasta 10% de sesiones) | conversiones |
| `tasa_conversion` | float | Porcentaje de sesiones con conversión | 0.0 - 10.0 | % |
| `ingresos` | float | Ingresos generados por conversiones | 0.0 - 1,000,000.0 | € |

**Nota**: Para registros de Facebook Ads, estas variables tendrán valor `None` (NaN).

### Variables Específicas de Facebook Ads

| Variable | Tipo | Descripción | Rango/Valores | Unidad |
|----------|------|-------------|---------------|--------|
| `conjunto_anuncios` | string | Nombre del conjunto de anuncios | "Conjunto Retargeting", "Conjunto Lookalike", "Conjunto Intereses", "Conjunto Demográfico", "Conjunto Audiencia Personalizada" | - |
| `anuncio_nombre` | string | Nombre del anuncio específico | "Anuncio Video Master", "Anuncio Carousel", "Anuncio Imagen Simple", "Anuncio Lead Gen", "Anuncio Conversión", "Anuncio Brand Awareness" | - |
| `impresiones` | int | Número de veces que se mostró el anuncio | 1,000 - 50,000 | impresiones |
| `alcance` | int | Número de personas únicas que vieron el anuncio | 600 - 45,000 (60-90% de impresiones) | personas |
| `clics` | int | Número total de clics en el anuncio | 10 - 2,500 (hasta 5% de impresiones) | clics |
| `gasto` | float | Cantidad de dinero gastada en el anuncio | 50.0 - 2,000.0 | € |
| `ctr` | float | Click-Through Rate (tasa de clics) | 0.1 - 10.0 | % |
| `cpc` | float | Costo por clic | 0.1 - 5.0 | € |
| `cpm` | float | Costo por mil impresiones | 1.0 - 20.0 | € |
| `costo_por_conversion` | float | Costo promedio por conversión | 5.0 - 2,000.0 | € |

**Nota**: Para registros de Google Analytics, estas variables tendrán valor `None` (NaN).

**Fórmulas calculadas**:
- `ctr = (clics / impresiones) * 100`
- `cpc = gasto / clics`
- `cpm = (gasto / impresiones) * 1000`
- `costo_por_conversion = gasto / conversiones`

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
