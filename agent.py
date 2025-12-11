#!/usr/bin/env python
# coding: utf-8

"""
Immune Agent - Sistema de agentes para consulta de cursos
Basado en Google ADK y arquitectura de agentes con tools
"""

# ============================================================================
# IMPORTS
# ============================================================================

import os
import io
from dotenv import load_dotenv
import pandas as pd
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.function_tool import FunctionTool
from google.genai import types
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import random

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Cargar variables de entorno
load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "secrets.env"))

# Verificar API key
try:
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    if GOOGLE_API_KEY:
        print("✅ Gemini API key found in environment.")
    else:
        print("⚠️ GOOGLE_API_KEY not set. Please add it to .env o exportarla.")
except Exception as e:
    print(f"⚠️ Error reading GOOGLE_API_KEY from environment: {e}")

# Configurar opciones de retry
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)
API_KEY = GOOGLE_API_KEY

# ============================================================================
# CARGA DE DATOS
# ============================================================================

# 1) Cursos
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
default_cursos_path = os.path.join(project_root, "cursos_immune", "cursos_immune_agente.xlsx")
cursos_path = os.environ.get("COURSES_PATH", default_cursos_path)
cursos_df = None

def _load_cursos(path: str):
    try:
        return pd.read_excel(path)
    except Exception:
        return pd.read_csv(path)

try:
    print("🔄 Intentando descargar cursos de Google Sheet...")
    cursos_url = "https://docs.google.com/spreadsheets/d/1oegyMA1i4nxlA3QAfdNy9zO__1Xd-ZmP/export?format=csv"
    cursos_df = pd.read_csv(cursos_url)
    print(f"✅ Cursos cargados desde Google Sheet: {len(cursos_df)} registros")
except Exception as e_sheet:
    print(f"⚠️ Falló carga de Google Sheet: {e_sheet}")
    if cursos_path and os.path.exists(cursos_path):
        try:
            cursos_df = _load_cursos(cursos_path)
            print(f"✅ Cursos cargados desde archivo local (fallback): {len(cursos_df)} registros")
        except Exception as e_local:
             print(f"⚠️ Falló carga local: {e_local}")

if cursos_df is None:
    print("⚠️ No se pudieron cargar cursos. Usando DataFrame vacío.")
    cursos_df = pd.DataFrame(columns=["id_curso", "nombre", "tipo_de_programa", "sector", "modalidad", "inicio", "precio"])

# 2) Feedbacks
feedbacks_df = None
default_feedbacks_path = os.path.join(project_root, "feedbacks", "Feedbacks.csv")
feedbacks_path = os.environ.get("FEEDBACKS_PATH", default_feedbacks_path)
file_id = os.environ.get("FILE_ID_FEEDBACKS", "1K0bkoBxOsQW_CF8w2kvWOZZTTwVx00cD")

def _load_feedbacks_from_buffer(buf: io.BytesIO):
    buf.seek(0)
    try:
        return pd.read_csv(buf, sep=None, engine="python")
    except Exception:
        buf.seek(0)
        try:
            return pd.read_csv(buf, sep=";", engine="python")
        except Exception:
            buf.seek(0)
            return pd.read_excel(buf)

if feedbacks_path and os.path.exists(feedbacks_path):
    with open(feedbacks_path, "rb") as fh_local:
        buf = io.BytesIO(fh_local.read())
    feedbacks_df = _load_feedbacks_from_buffer(buf)
    print(f"✅ Feedbacks cargados desde FEEDBACKS_PATH: {len(feedbacks_df)} registros")
else:
    try:
        drive_service = build("drive", "v3")
        req = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, req)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        feedbacks_df = _load_feedbacks_from_buffer(fh)
        print(f"✅ Feedbacks cargados desde Drive: {len(feedbacks_df)} registros")
    except Exception as e:
        print("⚠️ No se pudo cargar feedbacks; usando DataFrame vacío.")
        feedbacks_df = pd.DataFrame(columns=["Id_curso", "fecha", "comentarios"])

# ============================================================================
# CUSTOM TOOLS
# ============================================================================

def get_unique_values(column_name: str):
    """Devuelve los valores únicos de una columna del dataframe de cursos."""
    print(f"🔎 DEBUG: get_unique_values llamado para '{column_name}'")
    df = cursos_df
    if df is None or df.empty:
        return "Error: No se han cargado datos de cursos."
        
    if column_name not in df.columns:
        return [f"Error: Columna '{column_name}' no encontrada."]
    
    unique_vals = df[column_name].dropna().unique().tolist()
    result = [str(val) for val in unique_vals[:30]]
    return result

unique_tool = FunctionTool(get_unique_values)

def filtrar_cursos(query: str = "", modalidad: str = "", precio_max: float = None, top: int = 10):
    """Filtra cursos según criterios de búsqueda."""
    df = cursos_df
    cols = [
        "id_curso", "nombre", "tipo_de_programa", "sector",
        "modalidad", "inicio", "precio", "duracion",
        "salidas_profesionales", "financiacion"
    ]
    mask = True
    if query:
        mask &= (
            df["nombre"].astype(str).str.contains(query, case=False, na=False)
            | df["tipo_de_programa"].astype(str).str.contains(query, case=False, na=False)
            | df["sector"].astype(str).str.contains(query, case=False, na=False)
        )
    if modalidad:
        mask &= df["modalidad"].astype(str).str.contains(modalidad, case=False, na=False)
    if precio_max is not None and "precio" in df.columns:
        mask &= pd.to_numeric(df["precio"], errors="coerce") <= precio_max

    result = df.loc[mask, cols].head(top)
    if result.empty:
        return [{"resultado": "sin resultados"}]
    return result.to_dict(orient="records")

cursos_tool = FunctionTool(filtrar_cursos)

def analyze_course_logic(course_name: str):
    """
    Recibe el nombre exacto de un curso, busca sus feedbacks y genera un análisis de marketing.
    """
    # 0. Buscar Id_curso
    course_id = None
    try:
        matches = cursos_df[cursos_df["nombre"].astype(str).str.contains(course_name, case=False, na=False)]
        if not matches.empty:
            course_id = matches.iloc[0]["id_curso"]
    except Exception:
        pass

    # 1. Filtrar feedbacks
    df_fb = feedbacks_df
    if df_fb is None or df_fb.empty:
        return "No hay datos de feedback disponibles."

    if course_id:
        mask = df_fb["Id_curso"].astype(str).str.contains(str(course_id), case=False, na=False)
    else:
        mask = df_fb["Id_curso"].astype(str).str.contains(course_name, case=False, na=False)

    course_feedbacks = df_fb[mask]
    
    if course_feedbacks.empty:
        if course_id:
            return f"No se encontraron feedbacks para el curso '{course_name}' (Id_curso={course_id})."
        return f"No se encontraron feedbacks para el curso '{course_name}'."
    
    # 2. Muestra comentarios
    sample_size = 30
    comments = course_feedbacks["comentarios"].dropna().astype(str).tolist()
    comments_sample = comments[:sample_size]
    comments_text = "\n- ".join(comments_sample)
    
    # 2.1 Calcular Métricas Específicas del Curso
    try:
        cols_metrics = ["satisfaccion_general", "recomendaria_profesor", "contenidos_adecuados", "dominio_materia"]
        for col in cols_metrics:
            if col in course_feedbacks.columns:
                course_feedbacks.loc[:, col] = pd.to_numeric(course_feedbacks[col], errors='coerce')
        
        avg_sat = course_feedbacks["satisfaccion_general"].mean()
        avg_prof = course_feedbacks["recomendaria_profesor"].mean()
        avg_cont = course_feedbacks["contenidos_adecuados"].mean()
        total_fb = len(course_feedbacks)
        
        metrics_text = f"""
        DATOS CUANTITATIVOS (Media sobre 5):
        - Satisfacción General: {avg_sat:.2f}
        - Calidad Profesorado: {avg_prof:.2f}
        - Calidad Contenidos: {avg_cont:.2f}
        - Total de opiniones: {total_fb}
        """
    except Exception as e:
        metrics_text = "No se pudieron calcular las métricas específicas."

    # 3. Generar análisis con Gemini
    from google import genai
    prompt = f"""
    Eres un experto analista. Analiza los datos y comentarios del curso '{course_name}':
    
    {metrics_text}
    
    COMENTARIOS (Muestra):
    {comments_text}
    
    Genera un reporte estructurado así:
    ### 📊 Métricas Clave del Curso
    (Presenta aquí los datos cuantitativos calculados de forma clara)
    
    ### Fortalezas
    ### Debilidades
    ### Sugerencias de Mejora
    """
    
    try:
        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generando análisis: {e}"

analysis_tool = FunctionTool(analyze_course_logic)

# NUEVA TOOL: Análisis de Métricas
def analyze_metrics_logic(analysis_type: str = "general"):
    """
    Calcula métricas agregadas y rankings de los feedbacks.
    analysis_type puede ser:
    - 'general': Resumen global (medias generales de satisfacción y profesor).
    - 'ranking': Ranking de los 3 cursos mejor y peor valorados.
    - 'profesorado': Datos específicos sobre la calidad docente.
    """
    df = feedbacks_df
    if df is None or df.empty:
        return "No hay datos de feedback cargados para calcular métricas."
    
    # Asegurar numéricos
    cols_to_numeric = ["satisfaccion_general", "recomendaria_profesor"]
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if analysis_type == "general":
        total = len(df)
        sat_mean = df["satisfaccion_general"].mean()
        prof_mean = df["recomendaria_profesor"].mean() if "recomendaria_profesor" in df.columns else 0
        
        return f"""### 📊 Resumen de Métricas Globales
- **Total de Feedbacks analizados**: {total}
- **Satisfacción General Media**: {sat_mean:.2f} / 5.0
- **Recomendación Profesor Media**: {prof_mean:.2f} / 5.0
"""

    elif analysis_type == "ranking":
        if "Id_curso" not in df.columns:
            return "No se encuentra columna 'Id_curso' en los feedbacks."
            
        # Agrupar por curso y calcular media
        ranking = df.groupby("Id_curso")["satisfaccion_general"].mean().sort_values(ascending=False)
        
        # Mapear IDs a Nombres usando cursos_df
        course_map = {}
        if cursos_df is not None and not cursos_df.empty:
            # Detectar columna ID en cursos_df (puede ser id_curso o Id_curso)
            id_col = "id_curso" if "id_curso" in cursos_df.columns else "Id_curso"
            if id_col in cursos_df.columns and "nombre" in cursos_df.columns:
                course_map = pd.Series(cursos_df["nombre"].values, index=cursos_df[id_col].astype(str)).to_dict()
        
        top_3 = ranking.head(3)
        bottom_3 = ranking.tail(3)
        
        res = "### 🏆 Ranking de Cursos (Satisfacción)\n\n**TOP 3 MEJORES VALORADOS:**\n"
        for cid, score in top_3.items():
            name = course_map.get(str(cid), f"ID: {cid}")
            res += f"1. **{name}**: {score:.2f}/5\n"
            
        res += "\n**TOP 3 MENOS VALORADOS:**\n"
        for cid, score in bottom_3.items():
            name = course_map.get(str(cid), f"ID: {cid}")
            res += f"1. **{name}**: {score:.2f}/5\n"
            
        return res

    elif analysis_type == "profesorado":
         if "recomendaria_profesor" not in df.columns:
             return "No hay datos de recomendación de profesor."
         prof_mean = df["recomendaria_profesor"].mean()
         return f"### 👨‍🏫 Calidad Docente\nLa valoración media del profesorado es de **{prof_mean:.2f}/5**."
         
    return "Opción de métricas no reconocida. Prueba 'general', 'ranking' o 'profesorado'."

metrics_tool = FunctionTool(analyze_metrics_logic)


# Fallbacks
try:
    path_fallbacks = os.path.join(os.path.dirname(__file__), "fallbacks.txt")
    with open(path_fallbacks, "r", encoding="utf-8") as f:
        fallback_phrases = [line.strip() for line in f if line.strip()]
except Exception:
    fallback_phrases = ["Por favor, elige una opción: A, B, C o D."]

def get_random_fallback():
    return random.choice(fallback_phrases)

fallback_tool = FunctionTool(get_random_fallback)

# ============================================================================
# DEFINICIÓN DE AGENTES
# ============================================================================

# Tool Wrapper para análisis
def consultar_analista(course_name: str):
    print(f"🔄 Transfiriendo consulta al Analista para: {course_name}")
    return analyze_course_logic(course_name)

consultar_analista_tool = FunctionTool(consultar_analista)

# Agent 1: Buscador (Router)
buscador_agent = Agent(
    name="BuscadorAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config,
        api_key=API_KEY,
    ),
    description="Agente que busca el curso correcto.",
    instruction="""
    Preséntate SIEMPRE con esta frase exacta:  
    "Hola, soy Immune Agent y estoy aquí para ayudarte a interpretar la satisfacción de los alumnos en las diferentes formaciones que imparte Immune."

    REGLAS GENERALES (OBLIGATORIAS)
    - Nunca ignores al usuario. Siempre debes responder.
    - Tu único objetivo es guiar la conversación hasta obtener un NOMBRE DE CURSO que exista en la columna "nombre" del archivo cursos_immune_agente.xlsx.
    - No generes inventos, no crees nombres de cursos, no asumas nada. Siempre valida con las tools.
    - Si el usuario dice algo ambiguo, irrelevante, se desvía, saluda de nuevo o no responde a lo que preguntas:
        → DEBES llamar a la tool `get_random_fallback()`
        → Debes responder EXACTAMENTE la frase que devuelva. No añadas nada más.

    FLUJO DE TRABAJO

    1) INICIO: Pregunta al usuario cómo quiere empezar la búsqueda, ofreciendo EXACTAMENTE estas opciones:
    A) Sector  → usa get_unique_values('sector')
    B) Tipo de formación → usa get_unique_values('tipo_de_programa')
    C) Precio → muestra tres grupos fijos: "<3000", "3000–5000", ">5000"
    D) Nombre de la formación → usa get_unique_values('nombre')
    (Opcional: Si el usuario pide métricas globales, usa analyze_metrics_logic)

    2) INTERACCIÓN PARA REDUCIR OPCIONES:
    - Si elige A, B o D → DEBES llamar a `get_unique_values` primero.
    - [PENSAMIENTO OBLIGATORIO] Antes de responder, di para ti mismo: "Voy a llamar a la tool get_unique_values para mostrar las opciones reales".
    - Si el usuario selecciona una categoría específica o escribe una palabra clave (ej: "Master", "Data"), USA `cursos_tool(query='termino', top=20)` para listar SOLO los cursos que coincidan.
    - IMPORTANTE (OBLIGATORIO):
      * Si llamas a una tool, SIEMPRE debes usar su resultado para responder al usuario.
      * Muestra la lista de opciones que te devolvió la tool en formato de lista (bullets).
      * NUNCA te quedes en silencio después de llamar a una tool.
      * Si la tool devuelve ['Opción 1', 'Opción 2'], tu respuesta debe ser:
        "Aquí tienes las opciones de [categoría]:
         - Opción 1
         - Opción 2
         ¿Cuál prefieres?"
    - Si elige C → Muestra los tres rangos fijos.
    - Después de mostrar opciones, PREGUNTA SIEMPRE por el siguiente filtro lógico hasta que el usuario proporcione un nombre exacto.
    - En cada paso, valida que la respuesta del usuario sea interpretable. Si no, usa get_random_fallback().

     OBJETIVO IRREVOCABLE:
     → Obtener un nombre exacto de la formación que esté presente en get_unique_values('nombre').
     → Si el usuario dice "tipo de formación" o una categoría, NO es un nombre de curso. Debes listar los cursos dentro de esa categoría y pedirle que elija uno.
 
     3) CUANDO EL USUARIO DICE UN NOMBRE DE CURSO VÁLIDO:
     - Confirma: "Perfecto, transfiero la consulta al Analista para el curso [Nombre]..."
     - Llama obligatoriamente a:
             consultar_analista(course_name="[Nombre]")
     - IMPORTANTE: Muestra COMPLETO el texto que devuelva la tool. No lo resumas ni lo ocultes.
     - Finaliza preguntando: "¿Quieres analizar otro curso o prefieres ver un resumen de las métricas globales y rankings?"

    REGLAS CRÍTICAS:
    - Nunca te detengas hasta obtener un nombre válido.
    - Nunca permitas que el flujo se salga de este proceso.
    - Nunca inventes interpretaciones. Si hay duda → get_random_fallback().
    - Tus respuestas deben ser siempre breves, claras y orientadas a completar el flujo.
    """,
    tools=[unique_tool, cursos_tool, fallback_tool, consultar_analista_tool, metrics_tool],
)

print("✅ Agentes creados (Router -> Analista + Métricas)")

# ============================================================================
# EXPOSICIÓN
# ============================================================================

agent = buscador_agent
root_agent = buscador_agent