import random
import pandas as pd

# Parámetros principales (pueden ajustarse según la necesidad del pipeline)
OUTPUT_PATH = "feedbacks/comentarios_sinteticos_1500.csv"
N_OBJETIVO = 1500
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# -----------------------------
# 1. Dominios de cada columna
# -----------------------------

polaridades = ["muy_positivo", "positivo", "neutral", "negativo", "muy_negativo"]
temas = ["profesor", "metodologia", "contenido", "clase", "tecnologia", "soporte", "general"]
tonos = ["formal", "informal", "constructivo", "queja", "elogio", "sugerencia"]
longitudes = ["corto", "medio", "largo"]

# Polaridad -> rango de satisfacción general
satisfaccion_ranges = {
    "muy_positivo": (4, 5),
    "positivo": (3, 5),
    "neutral": (2, 4),
    "negativo": (1, 3),
    "muy_negativo": (1, 2),
}

# Polaridad -> tonos permitidos (para no generar combinaciones incoherentes)
tonos_por_polaridad = {
    "muy_positivo": ["formal", "informal", "elogio"],
    "positivo": ["formal", "informal", "elogio", "constructivo", "sugerencia"],
    "neutral": ["formal", "informal", "constructivo", "sugerencia"],
    "negativo": ["formal", "informal", "queja", "constructivo"],
    "muy_negativo": ["formal", "queja"],
}

# Tema -> posibles variables de aspecto asociadas
aspecto_por_tema = {
    "profesor": [
        "preparado_clases", 
        "dominio_materia", 
        "mantiene_atencion",
        "accesible_y_atiende_consultas",
        "recomendaria_profesor"
    ],
    "metodologia": [
        "organiza_actividades", 
        "contenidos_adecuados",
        "grado_dificultad",
        "conocimientos_utiles_futuro"
    ],
    "contenido": [
        "contenidos_adecuados", 
        "conocimientos_utiles_futuro"
    ],
    "clase": [
        "clase_duracion",
        "clase_horario",
        "clase_conveniencia_dia"
    ],
    "tecnologia": [
        "clase_calidad_conexion",
        "clase_calidad_audio",
        "clase_visibilidad_pantalla"
    ],
    "soporte": [
        "velocidad_respuesta",
        "utilidad_anuncios"
    ],
    "general": ["ninguno"],
}

# Variables que son de tipo texto (matriz de Google Forms)
variables_texto = {
    "clase_duracion", "clase_horario", "clase_conveniencia_dia",
    "clase_calidad_conexion", "clase_calidad_audio", "clase_visibilidad_pantalla"
}

# Mapeo de texto a número para matching (cuando la variable es texto)
matriz_a_numero = {
    "Pésimo": 1,
    "Mal": 2,
    "Regular": 3,
    "Bien": 4,
    "Genial": 5
}

# Polaridad -> rango de aspecto (1–5) coherente con el sentimiento
aspecto_ranges = {
    "muy_positivo": (4, 5),
    "positivo": (3, 5),
    "neutral": (2, 4),
    "negativo": (1, 3),
    "muy_negativo": (1, 2),
}

aperturas_contexto = [
    "Desde mi perspectiva personal considero que",
    "A lo largo de estas semanas he notado que",
    "Tras varias sesiones puedo decir que",
    "Si pienso en el progreso del curso, creo que",
    "Cuando comparo esta formación con otras, percibo que",
    "En mi día a día con el curso observo que",
    "Al repasar mis notas concluyo que",
    "En conversaciones con mis compañeros coincidimos en que",
    "Mirando mi avance hasta ahora entiendo que",
    "Con la mente puesta en mis objetivos profesionales valoro que",
    "Analizando lo que he aprendido siento que",
    "Desde el primer módulo he sentido que",
]

cierre_reflexiones = [
    "Esa impresión se mantiene con el paso de las semanas.",
    "Es algo que impacta en mi motivación diaria.",
    "Creo que resume bien cómo vivo el curso.",
    "Es un aspecto que comparto también con mis compañeros.",
    "Para mí, marca la diferencia respecto a otros programas.",
    "Me ayuda a decidir en qué módulos profundizar.",
    "Define la confianza que tengo en seguir avanzando.",
    "Se refleja en los resultados que obtengo en cada entrega.",
    "Lo tengo muy presente cuando hablo de la escuela.",
    "Siento que el equipo debería tenerlo en cuenta.",
]

variaciones_por_tema = {
    "profesor": [
        "El acompañamiento docente es clave para que avance.",
        "La disponibilidad del profesorado genera mucha confianza.",
        "Me anima a preparar las sesiones con antelación.",
        "Hace que las dudas se resuelvan con rapidez.",
        "Noto que el enfoque del docente está muy actualizado.",
        "La forma en que guía los debates es muy valiosa.",
    ],
    "metodologia": [
        "Las dinámicas se integran bien con los objetivos de cada módulo.",
        "La secuencia de actividades mantiene el interés del grupo.",
        "Se nota que cada bloque responde a un propósito concreto.",
        "Permite que la práctica tenga un peso real en el aprendizaje.",
        "La evolución de la dificultad está bastante cuidada.",
        "Consigue equilibrar teoría y casos reales de forma constante.",
    ],
    "contenido": [
        "Encuentro referencias útiles para seguir investigando por mi cuenta.",
        "Cada unidad conecta con tendencias actuales del sector.",
        "Hay ejemplos que puedo trasladar directamente a mis proyectos.",
        "Aporta claridad sobre temas que antes veía confusos.",
        "Siento que el temario está vivo y se actualiza con frecuencia.",
        "Me da herramientas concretas para actuar en el trabajo.",
    ],
    "clase": [
        "El ambiente que se genera invita a preguntar sin miedo.",
        "Las dinámicas grupales hacen que el tiempo pase rápido.",
        "El equipo docente cuida los ritmos y los descansos.",
        "Las interacciones con los compañeros enriquecen las sesiones.",
        "La organización del aula está pensada para colaborar.",
        "Salgo de cada clase con ideas prácticas para aplicar.",
    ],
    "tecnologia": [
        "El soporte técnico interviene con rapidez cuando hace falta.",
        "Se aprovechan bien las herramientas colaborativas online.",
        "Las grabaciones mantienen una calidad más que correcta.",
        "La plataforma permite seguir la clase incluso desde el móvil.",
        "La parte digital nunca me ha dejado fuera de una actividad.",
        "Se nota que prueban las soluciones antes de cada sesión.",
    ],
    "soporte": [
        "Siempre encontramos a alguien disponible en el campus virtual.",
        "El seguimiento individual ayuda a no perder el ritmo.",
        "Detectan incidencias antes de que se conviertan en un problema.",
        "La comunicación por correo y chat está bien coordinada.",
        "Siento que hacen un esfuerzo genuino por escucharnos.",
        "El feedback que recibo es claro y accionable.",
    ],
    "general": [
        "Veo coherencia entre lo prometido y lo que recibimos.",
        "Es una formación que recomendaría a otros perfiles como el mío.",
        "Me deja con ganas de seguir conectada a la comunidad.",
        "Refuerza mi decisión de apostar por el sector tecnológico.",
        "Es un hito importante dentro de mi itinerario profesional.",
        "Siento que aprovecho cada hora dedicada a este programa.",
    ],
}


def _minuscular_inicio(texto):
    for idx, caracter in enumerate(texto):
        if caracter.isalpha():
            return texto[:idx] + caracter.lower() + texto[idx + 1 :]
    return texto


def _asegurar_punto_final(texto):
    texto = texto.strip()
    if not texto:
        return texto
    if texto[-1] in {".", "!", "?"}:
        return texto
    return texto + "."


# ------------------------------------------------
# 2. Plantillas base de comentario por tema/polaridad
#    (texto en español, variado y coherente)
# ------------------------------------------------

plantillas = {
    "profesor": {
        "muy_positivo": [
            "El profesor explica los conceptos de forma muy clara y estructurada.",
            "Me siento muy acompañado por el profesor durante todo el curso.",
            "La dedicación del profesor marca una diferencia enorme en mi aprendizaje.",
            "El profesor domina el contenido y sabe transmitirlo de manera excelente.",
        ],
        "positivo": [
            "El profesor suele explicar bien, aunque a veces va un poco rápido.",
            "En general estoy satisfecho con cómo el profesor lleva las clases.",
            "El profesor responde a las dudas y facilita el seguimiento del temario.",
            "Las explicaciones del profesor son buenas y ayudan a entender la materia.",
        ],
        "neutral": [
            "El profesor cumple con su función, sin destacar especialmente.",
            "Las explicaciones del profesor son correctas pero podrían ser más dinámicas.",
            "No tengo una opinión muy marcada sobre el profesor, es aceptable.",
            "El profesor mantiene un nivel adecuado, sin puntos muy fuertes ni muy débiles.",
        ],
        "negativo": [
            "A veces el profesor no consigue que los conceptos queden claros.",
            "Me cuesta seguir las explicaciones del profesor en algunas sesiones.",
            "Echo en falta más ejemplos o aclaraciones por parte del profesor.",
            "No siempre el profesor responde de forma clara a las dudas.",
        ],
        "muy_negativo": [
            "El profesor no consigue explicar los contenidos de forma comprensible.",
            "Me siento perdido en las clases por la falta de claridad del profesor.",
            "Las explicaciones del profesor me resultan confusas y poco útiles.",
            "No estoy nada satisfecho con la forma de enseñar del profesor.",
        ],
    },
    "metodologia": {
        "muy_positivo": [
            "La metodología del curso es muy práctica y facilita mucho el aprendizaje.",
            "Me encanta la combinación de teoría y práctica que se utiliza en el curso.",
            "La forma de estructurar las actividades hace que todo sea muy fluido.",
            "La metodología fomenta la participación y me mantiene motivado.",
        ],
        "positivo": [
            "La metodología es adecuada y me ayuda a entender mejor los temas.",
            "Las actividades planteadas encajan bien con los objetivos del curso.",
            "Hay un buen equilibrio entre explicación y ejercicios prácticos.",
            "En general la metodología me parece bastante acertada.",
        ],
        "neutral": [
            "La metodología del curso me resulta correcta, sin destacar demasiado.",
            "Siento que la forma de trabajar es estándar, ni especialmente buena ni mala.",
            "Las actividades son aceptables, aunque podrían ser más variadas.",
            "La estructura de las sesiones es razonable, pero algo predecible.",
        ],
        "negativo": [
            "La metodología a veces hace que las clases se sientan algo monótonas.",
            "Echo en falta más actividades prácticas en esta metodología.",
            "La forma de plantear las tareas no siempre ayuda a consolidar lo aprendido.",
            "Me gustaría que la metodología fuera más interactiva.",
        ],
        "muy_negativo": [
            "La metodología del curso no se adapta nada a mis necesidades.",
            "Las dinámicas de clase me resultan poco útiles y repetitivas.",
            "No veo relación clara entre la metodología y los objetivos del curso.",
            "Siento que la forma de trabajo dificulta mi aprendizaje en lugar de ayudar.",
        ],
    },
    "contenido": {
        "muy_positivo": [
            "El contenido del curso está muy bien seleccionado y actualizado.",
            "Los temas tratados son muy relevantes para mi desarrollo profesional.",
            "El contenido es profundo y a la vez fácil de seguir.",
            "El programa del curso cubre exactamente lo que esperaba aprender.",
        ],
        "positivo": [
            "El contenido es interesante y útil en la mayoría de los temas.",
            "Los materiales del curso aportan valor y complementan bien las clases.",
            "La mayor parte del contenido me resulta aplicable a mi trabajo.",
            "En general estoy satisfecho con el contenido que se ha impartido.",
        ],
        "neutral": [
            "El contenido es correcto, aunque algunos temas me han parecido básicos.",
            "Hay partes del contenido que me interesan y otras que no tanto.",
            "El nivel del contenido me parece adecuado pero no especialmente diferencial.",
            "El temario cumple, sin aportar nada extraordinario.",
        ],
        "negativo": [
            "Algunos temas del contenido me han resultado poco relevantes.",
            "He echado en falta mayor profundidad en ciertos apartados.",
            "El temario no siempre se ajusta a lo que esperaba aprender.",
            "Parte del contenido me ha parecido desactualizado o repetitivo.",
        ],
        "muy_negativo": [
            "El contenido del curso no ha cumplido mis expectativas.",
            "Muchos temas me parecen irrelevantes para mis objetivos.",
            "No he encontrado utilidad real en la mayoría de los contenidos.",
            "Estoy muy decepcionado con el enfoque y selección del temario.",
        ],
    },
    "clase": {
        "muy_positivo": [
            "Las clases se me pasan rápido porque son dinámicas y entretenidas.",
            "El ambiente en clase favorece mucho la participación.",
            "La organización de cada sesión hace que aproveche muy bien el tiempo.",
            "Las clases tienen un ritmo muy bueno y mantienen mi atención.",
        ],
        "positivo": [
            "Las clases suelen tener un ritmo adecuado en la mayoría de los días.",
            "Me siento cómodo participando en las clases.",
            "El formato de las sesiones me ayuda a seguir el hilo del curso.",
            "En general las clases son agradables y productivas.",
        ],
        "neutral": [
            "Las clases son correctas, sin algo especialmente destacable.",
            "A veces las clases son más interesantes y otras más densas.",
            "El ritmo de clase es aceptable, aunque no siempre perfecto.",
            "La experiencia en clase es razonable y estable.",
        ],
        "negativo": [
            "En ocasiones las clases se hacen demasiado largas.",
            "Me cuesta mantener la atención durante toda la clase.",
            "El ritmo de clase no siempre se adapta al grupo.",
            "Algunas sesiones se sienten poco productivas.",
        ],
        "muy_negativo": [
            "Las clases se me hacen muy pesadas y difíciles de seguir.",
            "La mayoría de las sesiones me parecen poco aprovechables.",
            "No disfruto las clases y a menudo desconecto.",
            "Siento que pierdo el tiempo en bastantes sesiones.",
        ],
    },
    "tecnologia": {
        "muy_positivo": [
            "La plataforma funciona de forma muy fluida y sin interrupciones.",
            "La calidad de audio y vídeo en las clases online es excelente.",
            "No he tenido prácticamente ningún problema técnico durante el curso.",
            "La tecnología utilizada facilita mucho el seguimiento de las sesiones.",
        ],
        "positivo": [
            "En general la plataforma responde bien y es estable.",
            "Solo he tenido pequeños problemas técnicos que se han resuelto rápido.",
            "La calidad de la conexión suele ser buena.",
            "La experiencia tecnológica es satisfactoria en la mayoría de las clases.",
        ],
        "neutral": [
            "La tecnología utilizada es correcta, con algún fallo puntual.",
            "He tenido algunas incidencias técnicas, pero nada grave.",
            "La plataforma cumple su función, sin destacar demasiado.",
            "La calidad técnica es aceptable, pero mejorable.",
        ],
        "negativo": [
            "Las conexiones fallan con bastante frecuencia.",
            "La calidad del audio o vídeo a veces dificulta seguir la clase.",
            "He tenido varios problemas técnicos que cortan el ritmo de la sesión.",
            "La plataforma a veces se bloquea o responde lenta.",
        ],
        "muy_negativo": [
            "Los problemas técnicos son constantes y afectan mucho a mi aprendizaje.",
            "La conexión y la plataforma fallan tan a menudo que desmotivan.",
            "La calidad técnica es muy mala y rompe el flujo de las clases.",
            "Estoy muy insatisfecho con la parte tecnológica del curso.",
        ],
    },
    "soporte": {
        "muy_positivo": [
            "El equipo de soporte responde rápido y soluciona los problemas eficazmente.",
            "Siempre que he tenido una duda, el soporte me ha ayudado de inmediato.",
            "Me siento muy acompañado por el soporte académico y técnico.",
            "La atención al alumno es excelente y muy cercana.",
        ],
        "positivo": [
            "El soporte suele responder en un tiempo razonable.",
            "Las respuestas del equipo de soporte son útiles la mayoría de las veces.",
            "Cuando he tenido incidencias, se han resuelto adecuadamente.",
            "La atención al alumno en general es buena.",
        ],
        "neutral": [
            "El soporte responde de forma correcta, sin destacar demasiado.",
            "A veces tardan un poco en contestar, pero termina resolviéndose.",
            "La atención es aceptable pero podría ser más proactiva.",
            "No tengo una opinión muy fuerte sobre el soporte, es razonable.",
        ],
        "negativo": [
            "En varias ocasiones he sentido que el soporte tardaba demasiado en responder.",
            "Las soluciones que me han dado no siempre han sido claras.",
            "He tenido que insistir más de una vez para resolver algunos problemas.",
            "La atención al alumno podría ser bastante más ágil.",
        ],
        "muy_negativo": [
            "El soporte casi nunca responde a tiempo a mis consultas.",
            "No siento que el equipo de soporte se preocupe por mis problemas.",
            "Las incidencias se acumulan sin una solución clara.",
            "Estoy muy insatisfecho con la atención recibida por parte del soporte.",
        ],
    },
    "general": {
        "muy_positivo": [
            "Estoy muy satisfecho con la experiencia global del curso.",
            "El curso ha superado mis expectativas en casi todos los aspectos.",
            "Recomendaría este curso sin dudarlo a otras personas.",
            "La experiencia general ha sido muy positiva para mí.",
        ],
        "positivo": [
            "En general estoy contento con el curso.",
            "La experiencia global ha sido buena, con algunos puntos mejorables.",
            "El balance del curso es claramente positivo para mí.",
            "Repetiría una formación similar con esta escuela.",
        ],
        "neutral": [
            "Mi experiencia general con el curso es correcta, sin ser espectacular.",
            "Ha habido cosas buenas y cosas mejorables, en equilibrio.",
            "El curso ha cumplido, pero no ha destacado demasiado.",
            "Mi valoración global es intermedia, ni muy alta ni muy baja.",
        ],
        "negativo": [
            "En conjunto, el curso no ha cumplido del todo mis expectativas.",
            "La experiencia global ha sido algo decepcionante.",
            "Hay varios aspectos del curso que me han dejado insatisfecho.",
            "No tengo una percepción especialmente buena del curso en general.",
        ],
        "muy_negativo": [
            "Mi experiencia global con el curso ha sido claramente negativa.",
            "Estoy muy decepcionado con el resultado final del curso.",
            "No recomendaría este curso a otras personas.",
            "La experiencia general ha sido peor de lo que esperaba.",
        ],
    },
}

# ------------------------------------------------
# 3. Función para generar un comentario concreto
# ------------------------------------------------

def generar_comentario(polaridad, tema, tono, longitud):
    """
    Genera un comentario en texto plano coherente con polaridad y tema.
    El tono y la longitud pueden matizar el texto con pequeñas variaciones.
    """
    base = random.choice(plantillas[tema][polaridad]).strip()

    if random.random() < 0.65:
        apertura = random.choice(aperturas_contexto)
        comentario = f"{apertura} {_minuscular_inicio(base)}"
    else:
        comentario = base

    tono_extra = ""
    if tono == "constructivo":
        tono_extra = "Creo que aún se podrían mejorar algunos detalles."
    elif tono == "queja":
        tono_extra = "Este punto me genera bastante frustración."
    elif tono == "elogio":
        tono_extra = "Valoro mucho este aspecto del curso."
    elif tono == "sugerencia":
        tono_extra = "Me gustaría que se introdujeran cambios en este sentido."

    if tono_extra:
        comentario = _asegurar_punto_final(comentario)
        comentario += " " + tono_extra

    variaciones = variaciones_por_tema.get(tema, [])
    if variaciones and random.random() < 0.65:
        comentario = _asegurar_punto_final(comentario)
        comentario += " " + random.choice(variaciones)

    if longitud == "corto":
        if random.random() < 0.5:
            comentario = comentario.split(".")[0].strip()
            comentario = _asegurar_punto_final(comentario)
    elif longitud == "medio":
        if random.random() < 0.35:
            comentario = _asegurar_punto_final(comentario)
            comentario += " " + random.choice(cierre_reflexiones[:5])
    elif longitud == "largo":
        comentario = _asegurar_punto_final(comentario)
        comentario += " " + random.choice(cierre_reflexiones)

    comentario = _asegurar_punto_final(comentario)
    return " ".join(comentario.split())


# ------------------------------------------------
# 4. Generación del dataset (1000 filas)
# ------------------------------------------------

rows = []
n_objetivo = N_OBJETIVO

# Para evitar texto idéntico, podemos almacenar comentarios ya usados
comentarios_usados = set()

# Contador para evitar bucles infinitos
intentos_maximos = n_objetivo * 50  # Ampliamos margen para combinaciones únicas
intentos = 0

print(f"Generando {n_objetivo} comentarios únicos...")

while len(rows) < n_objetivo and intentos < intentos_maximos:
    intentos += 1
    
    # Mostrar progreso cada 100 intentos
    if intentos % 100 == 0:
        print(f"  Progreso: {len(rows)}/{n_objetivo} comentarios generados (intentos: {intentos})")
    
    polaridad = random.choice(polaridades)
    tema = random.choice(temas)
    tono = random.choice(tonos_por_polaridad[polaridad])
    longitud = random.choice(longitudes)

    # Generar comentario
    comentario = generar_comentario(polaridad, tema, tono, longitud)

    # Evitar duplicados exactos de texto
    if comentario in comentarios_usados:
        continue
    comentarios_usados.add(comentario)

    # Rango de satisfacción general según polaridad
    sat_min, sat_max = satisfaccion_ranges[polaridad]

    # Aspecto
    posibles_aspectos = aspecto_por_tema[tema]
    aspecto_variable = random.choice(posibles_aspectos)

    if aspecto_variable == "ninguno":
        aspecto_valor_min, aspecto_valor_max = 1, 5
    else:
        # Para todas las variables (numéricas y texto), usamos rangos numéricos
        # En el matching, convertiremos las variables texto a números usando matriz_a_numero
        aspecto_valor_min, aspecto_valor_max = aspecto_ranges[polaridad]

    row = {
        "comentario": comentario,
        "polaridad": polaridad,
        "tema": tema,
        "tono": tono,
        "longitud": longitud,
        "satisfaccion_min": sat_min,
        "satisfaccion_max": sat_max,
        "aspecto_variable": aspecto_variable,
        "aspecto_valor_min": aspecto_valor_min,
        "aspecto_valor_max": aspecto_valor_max,
    }
    rows.append(row)

# Crear DataFrame
df_comentarios = pd.DataFrame(rows)

# Verificar si se generaron todos los comentarios
if len(df_comentarios) < n_objetivo:
    print(f"\n[ADVERTENCIA] Solo se generaron {len(df_comentarios)} comentarios únicos de {n_objetivo} solicitados.")
    print(f"Se agotaron las combinaciones posibles después de {intentos} intentos.")
else:
    print(f"\n[OK] Se generaron exitosamente {len(df_comentarios)} comentarios únicos.")

# Guardar a CSV
df_comentarios.to_csv(OUTPUT_PATH, index=False)
print(f"[OK] Archivo '{OUTPUT_PATH}' guardado con {len(df_comentarios)} filas.")

print("\nPrimeras 5 filas:")
print(df_comentarios.head())
