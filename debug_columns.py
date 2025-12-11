import os
import pandas as pd

# Rutas como en el agente
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
default_cursos_path = os.path.join(project_root, "cursos_immune", "cursos_immune.xlsx")
cursos_path = os.environ.get("COURSES_PATH", default_cursos_path)

print(f"Buscando cursos en: {cursos_path}")

if os.path.exists(cursos_path):
    try:
        # Intentar leer Excel
        df = pd.read_excel(cursos_path)
        print("\n--- Columnas encontradas (Excel local) ---")
        print(df.columns.tolist())
        print("\n--- Primeras filas ---")
        print(df.head(2))
    except Exception as e:
        print(f"Error leyendo Excel: {e}")
        # Intentar CSV
        try:
            df = pd.read_csv(cursos_path)
            print("\n--- Columnas encontradas (CSV local) ---")
            print(df.columns.tolist())
        except Exception as e2:
            print(f"Error leyendo CSV: {e2}")
else:
    print("Archivo local no encontrado. El agente intentaría descargar de Google Sheet.")
    # Url del script original
    url = "https://docs.google.com/spreadsheets/d/1oegyMA1i4nxlA3QAfdNy9zO__1Xd-ZmP/export?format=csv"
    try:
        df = pd.read_csv(url)
        print("\n--- Columnas encontradas (Google Sheet) ---")
        print(df.columns.tolist())
    except Exception as e:
        print(f"Error descargando Sheet: {e}")

