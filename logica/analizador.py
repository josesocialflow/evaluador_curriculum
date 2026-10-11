"""Lógica de análisis de candidatos con el modelo de IA y selección del top N."""

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config.settings import (
    DEFICIENTE,
    EXCELENTE,
    INDIFERENTE,
    MODELO_IA,
    TEMPERATURA,
    TOP_N_CANDIDATOS,
    UMBRAL_EXCELENTE,
    UMBRAL_INDIFERENTE,
)
from logica.lector_cv import LecturaCV, imagen_a_data_uri
from logica.modelo_cv import AnalisisCV
from logica.prompts import (
    CABECERA_IMAGEN_CV,
    CABECERA_TEXTO_CV,
    SISTEMA_PROMPT,
    construir_instrucciones,
)


def clasificar_resultado(porcentaje: int) -> str:
    """Traduce el porcentaje de ajuste a una de las tres categorías."""
    if porcentaje >= UMBRAL_EXCELENTE:
        return EXCELENTE
    if porcentaje >= UMBRAL_INDIFERENTE:
        return INDIFERENTE
    return DEFICIENTE


def _construir_mensajes(lectura: LecturaCV, descripcion_puesto: str) -> list:
    """Crea los mensajes del modelo, en modo texto o en modo visión."""
    instrucciones = construir_instrucciones(descripcion_puesto)

    if lectura.texto:
        contenido = f"{instrucciones}\n\n{CABECERA_TEXTO_CV}\n\n{lectura.texto}"
        return [
            SystemMessage(content=SISTEMA_PROMPT),
            HumanMessage(content=contenido),
        ]

    bloques: list[str | dict[str, Any]] = [
        {"type": "text", "text": f"{instrucciones}\n\n{CABECERA_IMAGEN_CV}"}
    ]
    for png in lectura.imagenes_png:
        bloques.append(
            {"type": "image_url", "image_url": {"url": imagen_a_data_uri(png)}}
        )
    return [
        SystemMessage(content=SISTEMA_PROMPT),
        HumanMessage(content=bloques),
    ]


def analizar_candidato(lectura: LecturaCV, descripcion_puesto: str) -> AnalisisCV:
    """Analiza un único currículum y devuelve el resultado estructurado."""
    modelo = ChatOpenAI(
        model=MODELO_IA,
        temperature=TEMPERATURA,
    ).with_structured_output(AnalisisCV)

    mensajes = _construir_mensajes(lectura, descripcion_puesto)
    return modelo.invoke(mensajes)  # type: ignore[return-value]


def seleccionar_top(
    resultados: dict[str, AnalisisCV],
    n: int = TOP_N_CANDIDATOS,
) -> list[str]:
    """Devuelve las claves de los `n` candidatos con mayor porcentaje de ajuste."""
    ordenados = sorted(
        resultados.items(),
        key=lambda item: item[1].porcentaje_ajuste,
        reverse=True,
    )
    return [clave for clave, _ in ordenados[:n]]


def seleccionar_alternativos(
    resultados: dict[str, AnalisisCV],
    seleccionados: set[str],
    n: int,
) -> list[str]:
    """Devuelve los `n` candidatos con mayor ajuste que NO estén seleccionados."""
    ordenados = sorted(
        resultados.items(),
        key=lambda item: item[1].porcentaje_ajuste,
        reverse=True,
    )
    return [clave for clave, _ in ordenados if clave not in seleccionados][:n]
