"""Prompts usados para el análisis de currículums con el modelo de IA."""

SISTEMA_PROMPT = """Eres un reclutador senior experto en selección de talento, con más de 15 años \
de experiencia evaluando candidatos de forma objetiva, profesional y constructiva.

Analizas currículums centrándote en la relevancia real para el puesto concreto, \
considerando tanto las fortalezas como las áreas de desarrollo, y justificando \
siempre tus valoraciones."""


CABECERA_TEXTO_CV = "A continuación tienes el TEXTO del currículum del candidato:"

CABECERA_IMAGEN_CV = (
    "Las siguientes IMÁGENES son las páginas del currículum del candidato. "
    "Léelas con atención y extrae toda la información relevante:"
)


def construir_instrucciones(descripcion_puesto: str) -> str:
    """Construye las instrucciones de análisis incluyendo la descripción del puesto."""
    return f"""Analiza el currículum del candidato y evalúa qué tan bien encaja con el puesto descrito.

**DESCRIPCIÓN DEL PUESTO A CUBRIR:**
{descripcion_puesto}

**INSTRUCCIONES:**
1. Extrae el nombre completo, el teléfono, el correo electrónico, la educación y los años \
de experiencia del candidato (usa null en los campos que no aparezcan en el documento).
2. Identifica las habilidades clave del candidato más relevantes para este puesto.
3. Evalúa la experiencia laboral frente a los requisitos solicitados.
4. Señala las fortalezas principales y las áreas donde el candidato podría desarrollarse.
5. Asigna un porcentaje de ajuste realista (0-100) ponderando: experiencia (40%), \
habilidades técnicas (35%), formación (15%) y coherencia profesional (10%).

Sé preciso, objetivo y constructivo en tu análisis."""
