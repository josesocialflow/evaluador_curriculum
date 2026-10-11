"""Lectura de currículums en PDF.

Estrategia en dos pasos:

1. Se intenta extraer la **capa de texto** del PDF (rápido y gratis).
2. Si el PDF no tiene texto (p. ej. CVs escaneados o "impresos a PDF" con el
   texto vectorizado), se **renderiza cada página a imagen PNG** para poder
   analizarla con un modelo de visión (`gpt-4o-mini` es multimodal).
"""

import base64
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader

from config.settings import MAX_PAGINAS_RENDER, RENDER_DPI


@dataclass
class LecturaCV:
    """Resultado de intentar leer un currículum."""

    ruta: Path
    nombre_archivo: str
    texto: str | None = None
    imagenes_png: list[bytes] = field(default_factory=list)
    error: str | None = None

    @property
    def modo(self) -> str:
        """Indica cómo se ha podido leer el currículum."""
        if self.texto:
            return "texto"
        if self.imagenes_png:
            return "vision"
        return "error"

    @property
    def ok(self) -> bool:
        return self.error is None


def leer_cv(ruta: Path) -> LecturaCV:
    """Lee un PDF intentando primero el texto y, si no hay, renderizando."""
    lectura = LecturaCV(ruta=ruta, nombre_archivo=ruta.name)

    try:
        texto = _extraer_texto(ruta)
    except Exception as e:  # noqa: BLE001 - PDF corrupto, ilegible, etc.
        lectura.error = f"Error al leer el PDF: {e}"
        return lectura

    if texto:
        lectura.texto = texto
        return lectura

    # Sin capa de texto -> intentamos renderizar para usar visión.
    try:
        lectura.imagenes_png = _renderizar_paginas(ruta)
    except Exception as e:  # noqa: BLE001 - fallo al renderizar el PDF
        lectura.error = f"No se pudo extraer texto ni renderizar el PDF: {e}"
        return lectura

    if not lectura.imagenes_png:
        lectura.error = "El PDF no contiene texto ni páginas que se puedan renderizar."

    return lectura


def imagen_a_data_uri(png: bytes) -> str:
    """Convierte bytes PNG en una URL `data:` para enviarla al modelo de visión."""
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


def _extraer_texto(ruta: Path) -> str:
    reader = PdfReader(str(ruta))
    partes: list[str] = []
    for i, pagina in enumerate(reader.pages, 1):
        contenido = pagina.extract_text() or ""
        if contenido.strip():
            partes.append(f"--- PÁGINA {i} ---\n{contenido.strip()}")
    return "\n\n".join(partes).strip()


def _renderizar_paginas(ruta: Path) -> list[bytes]:
    if shutil.which("pdftoppm") is None:
        raise RuntimeError(
            "No se encontró 'pdftoppm' (poppler) para renderizar el PDF a imagen."
        )

    imagenes: list[bytes] = []
    with tempfile.TemporaryDirectory() as tmp:
        prefijo = Path(tmp) / "pagina"
        subprocess.run(
            [
                "pdftoppm",
                "-png",
                "-r", str(RENDER_DPI),
                "-f", "1",
                "-l", str(MAX_PAGINAS_RENDER),
                str(ruta),
                str(prefijo),
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )
        for png in sorted(Path(tmp).glob("pagina-*.png"), key=_numero_pagina):
            imagenes.append(png.read_bytes())

    return imagenes


def _numero_pagina(ruta: Path) -> int:
    digitos = "".join(c for c in ruta.stem if c.isdigit())
    return int(digitos) if digitos else 0
