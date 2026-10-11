"""Modelo de datos con la estructura del análisis de un currículum."""

from pydantic import BaseModel, Field


class AnalisisCV(BaseModel):
    """Resultado estructurado del análisis de un candidato."""

    nombre_completo: str = Field(
        description="Nombre y apellidos completos del candidato."
    )
    educacion: str | None = Field(
        default=None,
        description=(
            "Nivel educativo más alto y especialización principal. "
            "Usa null si no aparece en el CV."
        ),
    )
    telefono: str | None = Field(
        default=None,
        description="Teléfono de contacto del candidato tal como aparece en el CV. Usa null si no aparece.",
    )
    email: str | None = Field(
        default=None,
        description="Correo electrónico de contacto del candidato. Usa null si no aparece.",
    )
    anios_experiencia: int | None = Field(
        default=None,
        description=(
            "Años totales de experiencia laboral relevante (número entero). "
            "Usa null si no se puede determinar."
        ),
    )
    resumen_experiencia: str = Field(
        description="Resumen breve (2-3 frases) de la experiencia profesional del candidato."
    )
    habilidades_clave: list[str] = Field(
        description="Entre 5 y 7 habilidades clave del candidato relevantes para el puesto."
    )
    fortalezas: list[str] = Field(
        description="Entre 3 y 5 fortalezas principales del candidato."
    )
    areas_mejora: list[str] = Field(
        description="Entre 2 y 4 habilidades o áreas a desarrollar en el candidato."
    )
    porcentaje_ajuste: int = Field(
        ge=0,
        le=100,
        description=(
            "Porcentaje de ajuste del candidato al puesto (0-100), ponderando "
            "experiencia (40%), habilidades técnicas (35%), formación (15%) "
            "y coherencia profesional (10%)."
        ),
    )
