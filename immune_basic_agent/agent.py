#!/usr/bin/env python
# coding: utf-8
"""
Agente básico ADK para buscar cursos de Immune Institute en Google.
Estructura siguiendo el ejemplo 1-basic-agent del crash course.
"""

import os
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types

# -----------------------------------------------------------------------------
# Configuración
# -----------------------------------------------------------------------------

# Cargar variables de entorno desde .env en cwd y en este directorio
load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY no está definida. Añádela a .env o al entorno.")

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# -----------------------------------------------------------------------------
# Definición de agente único
# -----------------------------------------------------------------------------

root_agent = Agent(
    name="immune_basic_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
        api_key=GOOGLE_API_KEY,
    ),
    description="Busca en Google los cursos disponibles del instituto de tecnología Immune.",
    instruction="""
    Saluda brevemente. Luego usa google_search para encontrar los cursos ofrecidos
    por el instituto de tecnología Immune (immune.institute). Devuélvelos en una lista
    concisa con título y enlace si está disponible.
    """,
    tools=[google_search],
)

# Alias opcional que algunas guías usan, pero ADK busca root_agent
agent = root_agent

print("Agente básico listo. Ejecuta: adk web immune_basic_agent")

