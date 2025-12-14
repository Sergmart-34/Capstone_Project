# Capstone Project - Ecosistema de Análisis de Marketing y Satisfacción

**Proyecto final**: Sistema integral de análisis de marketing, satisfacción de alumnos y segmentación de usuarios para **IMMUNE Technology Institute**.

---

## 🎯 Objetivo

Desarrollar un **pipeline end-to-end** que integra:
1. **Extracción y generación de datos** mediante web scraping y LLMs
2. **Análisis exploratorio (EDA)** con visualizaciones y detección de patrones
3. **Clustering de usuarios** con K-Means para segmentación de audiencias
4. **Dashboard interactivo** en Power BI para visualización de KPIs
5. **Agente conversacional inteligente** para consulta natural de datos

---

## 📁 Estructura del Proyecto

```
Capstone/
├── EDA y clustering/
│   └── Proyecto_Capstone.ipynb        # EDA completo + Clustering K-Means
│
├── metricas_immune/
│   ├── generar_df_immune_metricas.py  # Generación de métricas de tráfico
│   └── generar_feedbacks_sinteticos.py # Generación de encuestas
│
├── immune_agent/
│   ├── agent.py                       # Sistema multi-agente (Router + Analista)
│   ├── secrets.env                    # Configuración API Keys
│   └── fallbacks.txt                  # Frases de manejo de errores
│
├── cursos_immune/
│   └── cursos_immune_agente.xlsx      # Catálogo de 31 programas
│
├── feedbacks/
│   └── Feedbacks.csv                  # Dataset de encuestas (500 registros)
│
├── formularios/
│   └── formularios.xlsx               # Perfiles de usuarios (700 registros)
│
├── Arquitectura.md                    # Documentación técnica completa
└── README.md                          # Este archivo
```

---

## 🔧 Componentes del Pipeline

### 1️⃣ Extracción y Generación de Datos

#### **Web Scraping de Cursos**
- **Fuente**: https://immune.institute/programas/
- **Tecnología**: GPT-4o-mini para parsing inteligente de HTML
- **Output**: Catálogo de 31 programas con características técnicas y comerciales
- **Script**: `EDA y clustering/Proyecto_Capstone.ipynb` (Sección 1.1)

#### **Generación de Datos Sintéticos**
Dado que no existen datos reales, se generan datasets coherentes con LLMs:

| Dataset | Registros | Descripción | Script |
|---------|-----------|-------------|--------|
| **Formularios** | 700 | Perfiles demográficos, académicos y laborales | `Proyecto_Capstone.ipynb` (Sección 1.2) |
| **Immune_metricas** | 3000 | Sesiones web con seguimiento cross-device | `generar_df_immune_metricas.py` |
| **Feedbacks** | 500 | Encuestas de satisfacción post-curso | `generar_feedbacks_sinteticos.py` |

**Coherencia garantizada**:
- IDs de usuario normalizados (`U####`) compartidos entre datasets
- Relaciones Ciudad-País, Edad-Experiencia, Formación-Sector laboral validadas
- Modalidades de curso alineadas con catálogo oficial

---

### 2️⃣ Análisis Exploratorio de Datos (EDA)

**Notebook**: `EDA y clustering/Proyecto_Capstone.ipynb` (Sección 2)

#### **Análisis de Métricas Web** (`Immune_metricas_PBI.xlsx`)
- Distribución de `tiempo_en_pagina`: Identificación de outliers (>800s)
- Creación de columna `solicita_informacion` (conversión binaria)
- Análisis temporal: Pico de consultas en **sábados a las 13:00h**
- Origen de tráfico: 4 canales (LinkedIn, Instagram, Google, Google Ads)
- Cobertura geográfica: 9 países, 26 ciudades

#### **Análisis de Formularios** (`formularios_PBI.xlsx`)
- **Edad**: μ=30, σ=8, rango [18, 50] sin outliers
- **Experiencia laboral**: μ=6 años, correlación lineal positiva con edad
- Variables cualitativas: País, género, titulación, sector laboral, motivación

#### **Análisis de Feedbacks** (`feedbacks_PBI.csv`)
- Segmentación por año, edición, tipo de programa y modalidad
- Identificación de variables de profesor vs. infraestructura
- Análisis de evolución temporal de satisfacción

---

### 3️⃣ Clustering de Usuarios (K-Means)

**Notebook**: `EDA y clustering/Proyecto_Capstone.ipynb` (Secciones 3-4)

#### **Metodología**
1. **Preprocesamiento**: StandardScaler + One-hot encoding
2. **Reducción dimensional**: PCA (2 componentes) para visualización
3. **Optimización**: Método del codo + Coeficiente de silueta → **K=5 óptimo**

#### **Perfiles de Clusters**

| Cluster | Perfil | Comportamiento | Tasa de Matriculación |
|---------|--------|----------------|----------------------|
| **0** | Graduados en transición | Múltiples consultas, exploran sectores | Media |
| **1** | Profesionales tech | Búsqueda dirigida, match con Immune | ⭐ **Alta** |
| **2** | Profesionales senior | Pocas consultas, alta intención | Media-Alta |
| **3** | Jóvenes sin experiencia | Alta exploración, bajo match | Baja |
| **4** | Recualificación profesional | Cambio de sector, buscan conocimiento | ⭐ **Alta** |

**Insights de negocio**:
- Priorizar campañas para clusters 1 y 4 (mayor ROI)
- Cluster 3 requiere contenido educativo pre-matrícula
- Cluster 2: Estrategia de remarketing directo

---

### 4️⃣ Dashboard Power BI

#### **Modelo de Datos**
Arquitectura en **estrella** con relaciones copo de nieve:

```
         Cursos_immune (31 programas)
                  |
     +------------+------------+
     |                         |
Immune_metricas_PBI      Feedbacks_PBI
     |                         |
     +------------+------------+
                  |
         Formularios_PBI
                  |
     +------------+------------+
     |                         |
Radar_Feedbacks_Profesor  Radar_Feedbacks_Clases
```

#### **Páginas del Dashboard**

1. **Feedbacks**: KPIs de satisfacción, desglose por modalidad/tipo/edad, evolución temporal
2. **KPIs Feedbacks**: Gráficos radar de evaluación de profesor y clases
3. **Immune**: Métricas de marketing (visitas, conversiones, canales, geografía)
4. **Páginas de detalle**: Drill-through para análisis específicos

#### **Preguntas de Negocio Resueltas**
✅ Distribución temporal de visitas y matriculaciones  
✅ Impacto de canales de adquisición en conversión  
✅ Análisis geográfico de interesados  
✅ Ranking de programas más/menos visitados  
✅ Evolución de valoraciones en el tiempo  
✅ Identificación de evaluaciones positivas (>3.5/5) vs. negativas  
✅ Comparativa de satisfacción por modalidad y tipo de programa  
✅ Análisis de causas: profesor vs. contenidos/infraestructura  

---

### 5️⃣ Immune Agent (Sistema Conversacional)

**Script**: `immune_agent/agent.py`

#### **Arquitectura**
Sistema multi-agente basado en **Google ADK** y **Gemini 2.5 Flash**:
- **Router Agent**: Filtrado de cursos por sector, modalidad, precio o nombre
- **Analista Agent**: Análisis de feedbacks, cálculo de KPIs, generación de informes

#### **Capacidades**
- 🔍 Consulta natural sobre catálogo de 31 cursos
- 📊 Análisis de satisfacción por programa específico
- 📈 Rankings de cursos basados en valoraciones
- 📄 Generación de informes ejecutivos con fortalezas y debilidades
- 🛡️ Manejo de ambigüedad con fallbacks contextuales

---

## 🚀 Instalación y Uso

### **Requisitos**
```bash
pip install pandas numpy matplotlib seaborn scikit-learn
pip install openai unidecode beautifulsoup4 requests
pip install google-adk google-generativeai python-dotenv
```

### **1. Ejecutar EDA y Clustering**
Abre el notebook en Google Colab o Jupyter:
```bash
jupyter notebook "EDA y clustering/Proyecto_Capstone.ipynb"
```

### **2. Generar Datasets Sintéticos**
```bash
python metricas_immune/generar_df_immune_metricas.py
python metricas_immune/generar_feedbacks_sinteticos.py
```

### **3. Ejecutar Immune Agent**
1. Configura `immune_agent/secrets.env` con tu `GOOGLE_API_KEY`
2. Ejecuta:
```bash
python immune_agent/agent.py
```

### **4. Abrir Dashboard Power BI**
Importa los archivos `.xlsx` y `.csv` generados en Power BI Desktop.

---

## 📊 Resultados y Métricas

- **31 cursos analizados** (bootcamps, másteres, cursos, especializaciones)
- **700 usuarios segmentados** en 5 clusters
- **3000 sesiones web** analizadas (enero 2024 - noviembre 2025)
- **500 encuestas de satisfacción** procesadas
- **8 preguntas de negocio** respondidas con visualizaciones interactivas

---

## 📖 Documentación Adicional

- **`Arquitectura.md`**: Documentación técnica completa con diccionario de variables, metodología de clustering y arquitectura del dashboard
- **Resumen Visual**: [Diagrama en Excalidraw](https://excalidraw.com/#room=b2f4fb4c0ce095979505,gzZQ7jnj6MIlwEKvtgGA0g)

---

## 👥 Autor

**Proyecto Capstone** - Análisis de Marketing y Satisfacción para IMMUNE Technology Institute

---

## 📝 Licencia

Este proyecto es parte del programa académico de IMMUNE Technology Institute.
