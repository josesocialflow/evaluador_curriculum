"""Configuración global de ProyectoCV_analyzer2.

Concentra en un único lugar los parámetros del modelo de IA, las rutas de
datos y las constantes que necesitan el resto de módulos de la aplicación.
"""

from pathlib import Path

# --- Rutas -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_CV_DIR = BASE_DIR / "data_cv"

# --- Modelo de IA ----------------------------------------------------------
MODELO_IA = "gpt-4o-mini"
TEMPERATURA = 0.6

# --- Lectura de currículums ------------------------------------------------
# Si un PDF no tiene capa de texto, se renderiza a imagen para usar visión.
RENDER_DPI = 150
MAX_PAGINAS_RENDER = 3

# --- Selección y evaluación ------------------------------------------------
TOP_N_CANDIDATOS = 2        # nº de candidatos que pasan a la entrevista
MAX_ALTERNATIVOS = 2        # nº máximo de candidatos alternativos a mostrar
UMBRAL_EXCELENTE = 80       # >= 80  -> candidato excelente
UMBRAL_INDIFERENTE = 50     # >= 50  -> candidato indiferente ; < 50 -> deficiente

# --- Categorías de resultado -----------------------------------------------
EXCELENTE = "Candidato excelente"
INDIFERENTE = "Candidato indiferente"
DEFICIENTE = "Candidato deficiente"

# Icono y color asociados a cada categoría (para la interfaz)
ICONO_CATEGORIA = {
    EXCELENTE: "✅",
    INDIFERENTE: "⚠️",
    DEFICIENTE: "❌",
}

COLOR_CATEGORIA = {
    EXCELENTE: "#22c55e",
    INDIFERENTE: "#f59e0b",
    DEFICIENTE: "#ef4444",
}
