#!/usr/bin/env python
# coding: utf-8

"""
Immune Agent - Sistema de agentes secuenciales para consulta de cursos
Basado en Google ADK y arquitectura de agentes secuenciales
"""

# ============================================================================
# IMPORTS
# ============================================================================

import os
import io
from dotenv import load_dotenv
import pandas as pd
from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.function_tool import FunctionTool
from google.genai import types
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Cargar variables de entorno desde .env (opcional)
# Intenta primero .env en cwd y luego secrets.env en este directorio
load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "secrets.env"))

# Verificar API key
try:
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    if GOOGLE_API_KEY:
        print("✅ Gemini API key found in environment.")
    else:
        print("⚠️ GOOGLE_API_KEY not set. Please add it to .env o exportarla antes de ejecutar `adk web`.")
except Exception as e:
    print(f"⚠️ Error reading GOOGLE_API_KEY from environment: {e}")

# Configurar opciones de retry
retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,  # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504]  # Retry on these HTTP errors
)
API_KEY = GOOGLE_API_KEY

# ============================================================================
# CARGA DE DATOS
# ============================================================================

# 1) Cursos (prioriza archivo local, luego fallback al Google Sheet; si falla, DF vacío)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
default_cursos_path = os.path.join(project_root, "cursos_immune", "cursos_immune.xlsx")
cursos_path = os.environ.get("COURSES_PATH", default_cursos_path)
cursos_df = None

def _load_cursos(path: str):
    """Carga cursos desde XLSX o CSV."""
    try:
        return pd.read_excel(path)
    except Exception:
        return pd.read_csv(path)

try:
    if cursos_path and os.path.exists(cursos_path):
        cursos_df = _load_cursos(cursos_path)
        print(f"✅ Cursos cargados desde archivo local: {len(cursos_df)} registros")
    else:
        cursos_url = "https://docs.google.com/spreadsheets/d/1oegyMA1i4nxlA3QAfdNy9zO__1Xd-ZmP/export?format=csv"
        cursos_df = pd.read_csv(cursos_url)
        print(f"✅ Cursos cargados desde Google Sheet: {len(cursos_df)} registros")
except Exception as e:
    print(
        "⚠️ No se pudieron cargar cursos; usando DataFrame vacío. "
        "Define COURSES_PATH con un XLSX/CSV local."
    )
    cursos_df = pd.DataFrame(
        columns=[
            "id_curso",
            "nombre",
            "tipo_de_programa",
            "sector",
            "modalidad",
            "inicio",
            "precio",
            "duracion",
            "horas_totales",
            "salidas_profesionales",
            "financiacion",
            "descripcion",
            "años_ofertado",
        ]
    )

# 2) Feedbacks
# Prioridad: archivo local (FEEDBACKS_PATH). Si no, Drive con FILE_ID_FEEDBACKS y credenciales ADC.
feedbacks_df = None
default_feedbacks_path = os.path.join(project_root, "feedbacks", "Feedbacks.csv")
feedbacks_path = os.environ.get("FEEDBACKS_PATH", default_feedbacks_path)
file_id = os.environ.get("FILE_ID_FEEDBACKS", "1K0bkoBxOsQW_CF8w2kvWOZZTTwVx00cD")

def _load_feedbacks_from_buffer(buf: io.BytesIO):
    """Carga feedbacks intentando autodetectar separador y formato."""
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
        # En entorno sin credenciales ni archivo local, degradar a DataFrame vacío
        print(
            "⚠️ No se pudo cargar feedbacks; usando DataFrame vacío. "
            "Define FEEDBACKS_PATH o FILE_ID_FEEDBACKS con credenciales ADC."
        )
        feedbacks_df = pd.DataFrame(
            columns=[
                "Id_curso",
                "fecha",
                "Tipo_clase",
                "satisfaccion_general",
                "comentarios",
                "dominio_materia",
                "mantiene_atencion",
                "fomenta_colaboracion",
                "puntualidad",
            ]
        )

# ============================================================================
# CUSTOM TOOLS
# ============================================================================

# Tool 1: Obtener valores únicos de una columna
def get_unique_values(column_name: str):
    """Devuelve los valores únicos de una columna del dataframe de cursos (ej: sector, tipo_de_programa, modalidad, nombre)."""
    df = cursos_df
    if column_name not in df.columns:
        return [f"Columna '{column_name}' no encontrada. Disponibles: {list(df.columns)}"]
    
    unique_vals = df[column_name].dropna().unique().tolist()
    # Si son muchos, devolver solo los primeros 20 o resumir
    return unique_vals[:20]

unique_tool = FunctionTool(get_unique_values)

# Tool 2: Filtrado de cursos por texto/modalidad/precio (Legacy, mantenida por compatibilidad)
def filtrar_cursos(query: str = "", modalidad: str = "", precio_max: float = None, top: int = 10):
    """Filtra cursos según criterios de búsqueda."""
    df = cursos_df
    cols = [
        "id_curso", "nombre", "tipo_de_programa", "sector",
        "modalidad", "inicio", "precio", "duracion", "horas_totales",
        "salidas_profesionales", "financiacion", "descripcion", "años_ofertado"
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

# Tool 3: Filtrado de feedbacks (Legacy)
def filtrar_feedbacks(id_curso: str = "", texto: str = "", top: int = 20):
    """Filtra feedbacks según Id_curso y texto en comentarios."""
    df = feedbacks_df
    cols = [
        "Id_curso", "fecha", "Tipo_clase",
        "satisfaccion_general", "comentarios",
        "dominio_materia", "mantiene_atencion",
        "fomenta_colaboracion", "puntualidad"
    ]
    mask = True
    if id_curso:
        mask &= df["Id_curso"].astype(str).str.contains(id_curso, case=False, na=False)
    if texto:
        mask &= df["comentarios"].astype(str).str.contains(texto, case=False, na=False)
    result = df.loc[mask, cols].head(top)
    if result.empty:
        return [{"resultado": "sin resultados"}]
    return result.to_dict(orient="records")

feedbacks_tool = FunctionTool(filtrar_feedbacks)

# Tool 4: Analiza el curso seleccionado (Lógica completa de análisis)
def analyze_course_logic(course_name: str):
    """
    Recibe el nombre exacto de un curso, busca sus feedbacks y genera un análisis de marketing.
    Devuelve el análisis en texto.
    """
    # 1. Filtrar feedbacks para este curso (por nombre o ID aproximado)
    df = feedbacks_df
    if df is None or df.empty:
        return "No hay datos de feedback disponibles para analizar."

    mask = df["Id_curso"].astype(str).str.contains(course_name, case=False, na=False)
    course_feedbacks = df[mask]
    
    if course_feedbacks.empty:
        return f"No se encontraron feedbacks para el curso '{course_name}'."
    
    # 2. Tomar una muestra de comentarios
    sample_size = 30
    comments = course_feedbacks["comentarios"].dropna().astype(str).tolist()
    comments_sample = comments[:sample_size]
    comments_text = "\n- ".join(comments_sample)
    
    # 3. Generar análisis con Gemini
    model = Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
        api_key=API_KEY
    )
    
    prompt = f"""
    Eres un experto en análisis de calidad formativa. Analiza los siguientes comentarios de alumnos del curso '{course_name}':
    
    {comments_text}
    
    Genera un reporte conciso con:
    - Puntos fuertes (Fortalezas)
    - Puntos débiles (Debilidades)
    - Sugerencias de mejora
    
    No inventes información. Si los comentarios son insuficientes, dilo.
    """
    
    try:
        response = model.client.models.generate_content(
            model=model.model,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error al generar análisis con el modelo: {e}"

analysis_tool = FunctionTool(analyze_course_logic)

import random

# Cargar frases aleatorias de fallback
try:
    with open(os.path.join(os.path.dirname(__file__), "fallbacks.txt"), "r", encoding="utf-8") as f:
        fallback_phrases = [line.strip() for line in f if line.strip()]
except Exception:
    fallback_phrases = [
        "Hola, soy Immune Agent. Por favor, elige una opción: A, B, C o D.",
        "Necesito que me indiques si prefieres buscar por Sector, Tipo o Precio.",
    ]

def get_random_fallback():
    """Devuelve una frase aleatoria para cuando el usuario se desvía."""
    return random.choice(fallback_phrases)

fallback_tool = FunctionTool(get_random_fallback)

print("✅ Custom tools creados")


# Agent 1: Buscador (Orchestrator) - Guía al usuario y llama al análisis al final
buscador_agent = Agent(
    name="BuscadorAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
        api_key=API_KEY,
    ),
    description="Agente principal que guía la búsqueda de cursos y solicita análisis.",
    instruction="""
    Preséntate SIEMPRE así: "Hola, soy Immune Agent y estoy aquí para ayudarte a interpretar la satisfacción de los alumnos en las diferentes formaciones que imparte Immune."
    
    Tu flujo de trabajo es:
    1. Pregunta al usuario cómo quiere empezar la búsqueda ofreciendo estas opciones explícitas:
       A) Tipo de formación (usa get_unique_values('tipo_de_programa'))
       B) Modalidad (usa get_unique_values('modalidad'))
       C) Precio (lista 3 grupos aproximados: -3000, 3000-5000, +5000)
       D) Nombre de la formación (usa get_unique_values('nombre'))
    
    2. Conversa con el usuario para filtrar opciones hasta identificar UN curso específico.
       - Si el usuario responde algo que no entiendes o se desvía del tema, USA la tool `get_random_fallback()` para obtener una frase y úsala para reencauzar la conversación. NO inventes tu propia respuesta de error repetitiva.
       - Si elige A, B o D, usa get_unique_values para mostrar las opciones disponibles.
       - TU OBJETIVO es obtener el NOMBRE EXACTO de la formación.
    
    3. Una vez confirmado el nombre del curso:
       - Di algo como: "Perfecto, voy a analizar los comentarios para el curso [Nombre]..."
       - LLAMA a la tool `analyze_course_logic(course_name="...")`.
       - Muestra el resultado del análisis que te devuelva la tool.
       - Pregunta si quiere analizar otro curso.
    """,
    tools=[unique_tool, analysis_tool, fallback_tool],
    output_key="session_output",
)

print("✅ Agentes individuales creados")


# ============================================================================
# EXPOSICIÓN DEL AGENTE
# ============================================================================

# Exponer el agente para la UI de ADK
agent = buscador_agent
root_agent = buscador_agent

print("✅ Agente listo para usar. Ejecuta: adk web immune_agent")
