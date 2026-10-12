"""Aplicación Streamlit de análisis de candidatos (parte visual).

Lee los currículums PDF de `data_cv`, los analiza con IA frente a la
descripción de un puesto y presenta el resultado, seleccionando los 2 mejores
candidatos para la entrevista final.
"""

from collections.abc import Callable
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from config.settings import (
    COLOR_CATEGORIA,
    DATA_CV_DIR,
    EXCELENTE,
    ICONO_CATEGORIA,
    INDIFERENTE,
    MAX_ALTERNATIVOS,
)
from logica.analizador import (
    analizar_candidato,
    clasificar_resultado,
    seleccionar_alternativos,
    seleccionar_top,
)
from logica.lector_cv import LecturaCV, leer_cv
from logica.modelo_cv import AnalisisCV

load_dotenv()

CSS = """
<style>
.hero {
    background: linear-gradient(120deg, rgba(99,102,241,0.18), rgba(14,165,233,0.14));
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 16px;
    padding: 18px 22px;
    margin-bottom: 8px;
}
.pill {
    display: inline-block;
    margin: 4px 6px 4px 0;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.9rem;
    line-height: 1.3;
}
.pill-perfil { background: rgba(59,130,246,0.14); border: 1px solid rgba(59,130,246,0.40); }
.pill-skill  { background: rgba(34,197,94,0.14);  border: 1px solid rgba(34,197,94,0.42); }
.pill-ok     { background: rgba(34,197,94,0.18);  border: 1px solid rgba(34,197,94,0.55); font-weight: 600; }
.pill-mid    { background: rgba(245,158,11,0.18); border: 1px solid rgba(245,158,11,0.55); font-weight: 600; }
.pill-bad    { background: rgba(239,68,68,0.18);  border: 1px solid rgba(239,68,68,0.55);  font-weight: 600; }
.big-score   { font-size: 3.4rem; font-weight: 800; line-height: 1; }
</style>
"""


def _init_estado() -> None:
    """Inicializa las claves de `session_state` que usa la aplicación."""
    st.session_state.setdefault("indice", 0)
    st.session_state.setdefault("descripcion", "")
    st.session_state.setdefault("lecturas", {})
    st.session_state.setdefault("resultados", {})
    st.session_state.setdefault("errores_analisis", {})
    if "candidatos" not in st.session_state:
        st.session_state.candidatos = sorted(DATA_CV_DIR.glob("*.pdf"))


def _obtener_lectura(ruta: Path) -> LecturaCV:
    """Lee un CV (con caché) intentando texto y, si no hay, visión."""
    cache: dict = st.session_state.lecturas
    clave = str(ruta)
    if clave not in cache:
        cache[clave] = leer_cv(ruta)
    return cache[clave]


def _nombre_desde_archivo(ruta: Path) -> str:
    return ruta.stem.replace("_", " ").strip().title()


def _contacto(analisis: AnalisisCV) -> str:
    """Devuelve el teléfono del candidato o, en su defecto, el correo electrónico."""
    if analisis.telefono:
        return f"📞 {analisis.telefono}"
    if analisis.email:
        return f"✉️ {analisis.email}"
    return "📭 Sin datos de contacto"


def _limpiar_descripcion() -> None:
    st.session_state.descripcion = ""


def _siguiente_cv() -> None:
    total = len(st.session_state.candidatos)
    st.session_state.indice = min(st.session_state.indice + 1, total - 1)


def _anterior_cv() -> None:
    st.session_state.indice = max(st.session_state.indice - 1, 0)


def _analizar_todos(
    descripcion: str,
    on_progress: Callable[[float], object] | None = None,
) -> None:
    """Analiza todos los candidatos frente a la descripción dada."""
    resultados: dict[str, AnalisisCV] = {}
    errores: dict[str, str] = {}
    candidatos = st.session_state.candidatos
    total = len(candidatos) or 1
    for i, ruta in enumerate(candidatos, 1):
        lectura = _obtener_lectura(ruta)
        if lectura.error:
            errores[ruta.name] = lectura.error
        else:
            try:
                resultados[str(ruta)] = analizar_candidato(lectura, descripcion)
            except Exception as e:  # noqa: BLE001 - se muestra al usuario
                errores[ruta.name] = str(e)
        if on_progress is not None:
            on_progress(i / total)
    st.session_state.resultados = resultados
    st.session_state.errores_analisis = errores
    st.session_state.descripcion_analizada = descripcion


def _clase_categoria(categoria: str) -> str:
    if categoria == EXCELENTE:
        return "pill-ok"
    if categoria == INDIFERENTE:
        return "pill-mid"
    return "pill-bad"


def _pills(items: list[tuple[str, str]], clase: str) -> str:
    return "".join(
        f"<span class='pill {clase}'>{icono} {texto}</span>" for icono, texto in items
    )


def _render_entrada() -> None:
    st.header("📋 Datos de entrada")

    total = len(st.session_state.candidatos)
    indice = st.session_state.indice
    ruta = st.session_state.candidatos[indice]
    lectura = _obtener_lectura(ruta)
    analisis = st.session_state.resultados.get(str(ruta))

    # --- 1. CV del candidato ---
    st.markdown("**1. CV del candidato**")
    st.markdown(f"📄 `{ruta.name}`")
    if lectura.error:
        st.error(f"❌ {lectura.error}")
    else:
        via = "capa de texto" if lectura.modo == "texto" else "imagen (visión)"
        st.success(f"✅ Leído correctamente · vía {via}")

    nombre = analisis.nombre_completo if analisis else _nombre_desde_archivo(ruta)
    st.markdown(f"**👤 Candidato:** {nombre}")
    st.caption(f"CV {indice + 1} de {total}")
    col_prev, col_next = st.columns(2)
    with col_prev:
        st.button(
            "⬅️ Anterior CV",
            on_click=_anterior_cv,
            disabled=indice <= 0,
            use_container_width=True,
        )
    with col_next:
        st.button(
            "➡️ Siguiente CV",
            on_click=_siguiente_cv,
            disabled=indice >= total - 1,
            use_container_width=True,
        )

    st.divider()

    # --- 2. Descripción del puesto ---
    st.markdown("**2. Descripción del puesto de trabajo**")
    st.text_area(
        "Descripción del puesto",
        key="descripcion",
        height=240,
        label_visibility="collapsed",
        placeholder=(
            "Ej.: Buscamos un/a Analista de Ciberseguridad con 3+ años de "
            "experiencia en seguridad OT, normativa NIS2, ISO 27001..."
        ),
    )
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔍 Analizar candidatos", type="primary", use_container_width=True):
            descripcion = st.session_state.descripcion.strip()
            if not descripcion:
                st.warning("⚠️ Escribe primero la descripción del puesto.")
            else:
                barra = st.progress(0.0, text="Analizando candidatos con IA...")
                _analizar_todos(descripcion, on_progress=barra.progress)
                barra.empty()
                st.toast("Análisis completado ✅")
    with col_b2:
        st.button(
            "🧹 Borrar descripción",
            on_click=_limpiar_descripcion,
            use_container_width=True,
        )

    if st.session_state.errores_analisis:
        with st.expander("⚠️ Incidencias durante el análisis"):
            for nombre_archivo, msg in st.session_state.errores_analisis.items():
                st.write(f"**{nombre_archivo}**: {msg}")

    st.divider()
    st.markdown("**🏆 Candidatos elegidos para la entrevista**")
    resultados: dict[str, AnalisisCV] = st.session_state.resultados
    if not resultados:
        st.caption("Aún no hay candidatos seleccionados. Analiza para verlos aquí.")
    else:
        seleccionados = seleccionar_top(resultados)
        for clave in seleccionados:
            analisis = resultados[clave]
            st.markdown(
                f"👤 **{analisis.nombre_completo}** — "
                f"{_contacto(analisis)} · {analisis.porcentaje_ajuste}%"
            )

        alternativos = seleccionar_alternativos(
            resultados, set(seleccionados), MAX_ALTERNATIVOS
        )
        if alternativos:
            st.divider()
            st.markdown("**🔄 Candidatos alternativos**")
            for clave in alternativos:
                alternativo = resultados[clave]
                st.markdown(
                    f"👤 **{alternativo.nombre_completo}** — "
                    f"{_contacto(alternativo)} · {alternativo.porcentaje_ajuste}%"
                )


def _render_resultado() -> None:
    st.header("📊 Resultado del análisis")

    resultados: dict[str, AnalisisCV] = st.session_state.resultados
    ruta = st.session_state.candidatos[st.session_state.indice]
    analisis = resultados.get(str(ruta))

    if resultados:
        top = seleccionar_top(resultados)
        nombres = ", ".join(resultados[clave].nombre_completo for clave in top)
        st.caption(f"🏆 Seleccionados para la entrevista: {nombres}")

    if analisis is None:
        st.info(
            "👈 Escribe la descripción del puesto y pulsa **Analizar candidatos** "
            "para ver aquí el análisis del CV actual."
        )
        return

    categoria = clasificar_resultado(analisis.porcentaje_ajuste)
    color = COLOR_CATEGORIA[categoria]
    icono = ICONO_CATEGORIA[categoria]

    # --- Evaluación Principal ---
    st.subheader("🎯 Evaluación Principal")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown(
            f"<div class='big-score' style='color:{color}'>"
            f"{analisis.porcentaje_ajuste}%</div>",
            unsafe_allow_html=True,
        )
        st.caption("Ajuste al puesto")
    with col_b:
        st.markdown(
            f"<span class='pill {_clase_categoria(categoria)}'>{icono} {categoria}</span>",
            unsafe_allow_html=True,
        )
        if str(ruta) in seleccionar_top(resultados):
            st.success("✅ Recomendado para la entrevista final")
        else:
            st.error("❌ No seleccionado para la entrevista final")

    st.divider()

    # --- Perfil del Candidato ---
    st.subheader("👤 Perfil del Candidato")
    educacion = analisis.educacion or "No disponible"
    if analisis.anios_experiencia is not None:
        experiencia = f"{analisis.anios_experiencia} años de experiencia"
    else:
        experiencia = "Experiencia no disponible"
    perfil = [
        ("🧑", analisis.nombre_completo),
        ("🎓", educacion),
        ("⏱️", experiencia),
    ]
    st.markdown(_pills(perfil, "pill-perfil"), unsafe_allow_html=True)

    st.divider()

    # --- Resumen de la experiencia ---
    st.subheader("🧠 Resumen de la experiencia")
    st.write(analisis.resumen_experiencia)

    if analisis.habilidades_clave:
        st.markdown(
            _pills([("✅", h) for h in analisis.habilidades_clave], "pill-skill"),
            unsafe_allow_html=True,
        )

    st.write("")
    col_fort, col_mej = st.columns(2)
    with col_fort:
        st.markdown("**💪 Fortalezas**")
        for fortaleza in analisis.fortalezas:
            st.markdown(f"- {fortaleza}")
    with col_mej:
        st.markdown("**📈 Habilidades a desarrollar**")
        for area in analisis.areas_mejora:
            st.markdown(f"- {area}")


def main() -> None:
    st.set_page_config(
        page_title="Analizador de Candidatos",
        page_icon="🧑‍💼",
        layout="wide",
    )
    _init_estado()
    st.markdown(CSS, unsafe_allow_html=True)

    st.markdown(
        "<div class='hero'><h1 style='margin:0'>🧑‍💼 Analizador Inteligente de "
        "Candidatos</h1><p style='margin:6px 0 0'>Sube la descripción del puesto, "
        "analiza todos los CV y descubre los <b>2 mejores candidatos</b> para la "
        "entrevista.</p></div>",
        unsafe_allow_html=True,
    )

    if not st.session_state.candidatos:
        st.error(f"⚠️ No se encontraron currículums PDF en `{DATA_CV_DIR}`.")
        return

    col_izq, col_der = st.columns(2, gap="large")
    with col_izq:
        _render_entrada()
    with col_der:
        _render_resultado()


if __name__ == "__main__":
    main()
