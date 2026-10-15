import io
import os
import re
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="CompeteTrack | Alquimia LF", page_icon="📊", layout="wide")

ROOT = os.path.dirname(os.path.abspath(__file__))
COMPETITORS_PATH = os.path.join(ROOT, "data", "competidores.csv")
PINK = "#D783A3"

st.markdown("""
<style>
.block-container {padding-top: 1.35rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background:#fff7fa; border:1px solid #f0dce4; padding:13px; border-radius:12px;}
h1 {letter-spacing:-.03em;}
.small-note {font-size:.88rem;color:#777;}
</style>
""", unsafe_allow_html=True)

def read_upload(file):
    if file is None:
        return None
    name = file.name.lower()
    if name.endswith(".csv"):
        try:
            file.seek(0)
            return pd.read_csv(file)
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(file, encoding="latin-1")
    file.seek(0)
    return pd.read_excel(file)

def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")

def xlsx_bytes(df, sheet="datos"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet[:31])
    return buffer.getvalue()

def clean_col(name):
    s = str(name).strip().lower()
    s = (s.replace("á","a").replace("é","e").replace("í","i")
          .replace("ó","o").replace("ú","u").replace("ñ","n"))
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s

def normalize_trade_columns(df):
    """Mapea nombres frecuentes de reportes; conserva columnas originales no reconocidas."""
    out = df.copy()
    out.columns = [clean_col(c) for c in out.columns]
    aliases = {
        "fecha": ["fecha", "fecha_declaracion", "fecha_embarque", "periodo", "mes"],
        "empresa": ["empresa", "importador", "razon_social_importador", "nombre_importador",
                    "exportador", "razon_social", "declarante"],
        "producto": ["producto", "descripcion", "descripcion_arancelaria", "mercancia",
                     "descripcion_producto", "nombre_producto"],
        "subpartida": ["subpartida", "subpartida_arancelaria", "posicion_arancelaria",
                       "codigo_arancelario", "hs_code", "partida"],
        "pais_origen": ["pais_origen", "pais_de_origen", "origen", "pais_procedencia",
                        "pais", "pais_exportador"],
        "valor_usd": ["valor_usd", "fob_usd", "valor_fob_usd", "valor_fob", "cif_usd",
                      "valor_cif_usd", "valor_cif", "valor_dolares", "valor_us"],
        "peso_neto_kg": ["peso_neto_kg", "peso_neto", "kilos_netos", "kg_netos", "peso_kg",
                         "cantidad_kg", "cantidad_neta"],
        "fuente": ["fuente", "source", "origen_dato"]
    }
    rename = {}
    for target, options in aliases.items():
        if target in out.columns:
            continue
        for opt in options:
            if opt in out.columns:
                rename[opt] = target
                break
    out = out.rename(columns=rename)
    return out

TRADE_TEMPLATE = pd.DataFrame(columns=[
    "fecha","empresa","producto","subpartida","pais_origen","valor_usd","peso_neto_kg","fuente"
])
SOCIAL_TEMPLATE = pd.DataFrame(columns=[
    "fecha_observacion","empresa","plataforma","tipo_contenido","url","reproducciones",
    "interacciones","seguidores","fuente","notas"
])
MEDIA_TEMPLATE = pd.DataFrame(columns=["fecha","empresa","medio","titular","url","tema","fuente"])

if "competitors" not in st.session_state:
    try:
        st.session_state.competitors = pd.read_csv(COMPETITORS_PATH)
    except Exception:
        st.session_state.competitors = pd.DataFrame(columns=["empresa","sitio_web","lineas_coincidentes","segmento","prioridad","estado_validacion","fuente"])
for key, default in [
    ("trade_data", TRADE_TEMPLATE.copy()),
    ("social_data", SOCIAL_TEMPLATE.copy()),
    ("media_data", MEDIA_TEMPLATE.copy()),
]:
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.markdown("## CompeteTrack")
    st.caption("Inteligencia competitiva · Alquimia LF")
    page = st.radio("Navegación", [
        "Inicio", "Competidores", "Inteligencia comercial",
        "Redes y pauta", "Medios y noticias", "Comparativos", "Plantillas y exportación"
    ])
    st.divider()
    st.caption("Versión inicial · Sin Apify")
    st.caption("Los datos externos requieren fuentes autorizadas y fecha de consulta.")

st.title("CompeteTrack")
st.caption("Monitoreo y análisis competitivo para Alquimia LF")

if page == "Inicio":
    st.info("Las empresas y categorías precargadas son candidatos de investigación basados en información pública. No son un ranking confirmado de mercado. Carga datos verificables para calcular resultados.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Empresas candidatas", len(st.session_state.competitors))
    c2.metric("Registros comerciales", len(st.session_state.trade_data))
    c3.metric("Observaciones digitales", len(st.session_state.social_data))
    c4.metric("Menciones en medios", len(st.session_state.media_data))
    st.subheader("Resumen de líneas competitivas")
    if not st.session_state.competitors.empty and "segmento" in st.session_state.competitors:
        counts = st.session_state.competitors["segmento"].fillna("Sin clasificar").value_counts().rename_axis("segmento").reset_index(name="empresas")
        st.plotly_chart(px.bar(counts, x="segmento", y="empresas", title="Candidatos por segmento"), use_container_width=True)
    st.subheader("Cómo alimentar el monitor")
    st.markdown("""
    1. **Competidores:** revisa empresas y confirma qué productos compiten con Alquimia.
    2. **Inteligencia comercial:** carga CSV/Excel de Legiscomex si tu licencia permite exportarlos, o estadísticas oficiales.
    3. **Redes y pauta:** importa observaciones públicas con URL, fecha y fuente.
    4. **Medios y noticias:** registra titulares y enlaces verificables.
    5. **Comparativos:** analiza solo las métricas que existan en los archivos cargados.
    """)

elif page == "Competidores":
    st.subheader("Empresas candidatas")
    st.write("Edita esta lista para confirmar competidores directos. Las prioridades son preliminares y se deben validar por producto, cobertura y actualidad.")
    edited = st.data_editor(st.session_state.competitors, num_rows="dynamic", use_container_width=True, key="competitors_editor")
    st.session_state.competitors = edited
    query = st.text_input("Buscar empresa o línea de producto")
    if query:
        mask = edited.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
        st.dataframe(edited[mask], use_container_width=True)
    st.download_button("Exportar competidores CSV", csv_bytes(edited), "competidores_alquimia.csv", "text/csv")
    st.download_button("Exportar competidores Excel", xlsx_bytes(edited, "competidores"), "competidores_alquimia.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif page == "Inteligencia comercial":
    st.subheader("Datos comerciales integrados")
    st.write("Carga reportes de comercio exterior exportados legalmente desde tus fuentes. La aplicación no presenta Legiscomex como módulo ni se conecta directamente a su sistema.")
    st.caption("No se requiere Apify. La conexión directa a Legiscomex dependerá de que el proveedor habilite una API o integración para tu suscripción.")
    st.download_button("Descargar plantilla Excel", xlsx_bytes(TRADE_TEMPLATE, "comercio_exterior"),
                       "plantilla_comercio_exterior.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    upload = st.file_uploader("Cargar reporte CSV o Excel", type=["csv","xlsx","xls"], key="trade_upload")
    if upload:
        raw = read_upload(upload)
        normalized = normalize_trade_columns(raw)
        st.write("Vista previa normalizada")
        st.dataframe(normalized.head(30), use_container_width=True)
        st.caption("Verifica la correspondencia de columnas antes de utilizar los datos. Las columnas no reconocidas se conservan.")
        if st.button("Guardar datos en esta sesión", type="primary"):
            st.session_state.trade_data = normalized.copy()
            st.success(f"{len(normalized):,} filas cargadas en la sesión.")
    df = st.session_state.trade_data.copy()
    if not df.empty:
        st.subheader("Datos cargados")
        st.dataframe(df, use_container_width=True)
        if "valor_usd" in df:
            values = pd.to_numeric(df["valor_usd"].astype(str).str.replace(",","",regex=False).str.replace("$","",regex=False), errors="coerce")
            st.metric("Suma de valor comercial reportado (USD)", f"${values.sum():,.2f}" if values.notna().any() else "No disponible")
        if "peso_neto_kg" in df:
            kg = pd.to_numeric(df["peso_neto_kg"], errors="coerce")
            st.metric("Suma de peso neto reportado (kg)", f"{kg.sum():,.2f}" if kg.notna().any() else "No disponible")
        if "empresa" in df.columns and "valor_usd" in df.columns:
            plot = df.copy()
            plot["valor_usd"] = pd.to_numeric(plot["valor_usd"].astype(str).str.replace(",","",regex=False).str.replace("$","",regex=False), errors="coerce")
            agg = plot.groupby("empresa", dropna=False)["valor_usd"].sum().reset_index().sort_values("valor_usd", ascending=False).head(20)
            st.plotly_chart(px.bar(agg, x="empresa", y="valor_usd", title="Valor reportado por empresa (según archivo cargado)"), use_container_width=True)
        st.download_button("Descargar datos normalizados CSV", csv_bytes(df), "datos_comerciales_normalizados.csv", "text/csv")
    else:
        st.info("Aún no hay datos. Descarga la plantilla o carga un reporte real.")

elif page == "Redes y pauta":
    st.subheader("Observatorio de redes y publicidad")
    st.write("Sin Apify: la primera versión admite registro manual o importación de observaciones desde fuentes públicas y autorizadas.")
    st.caption("No se extraen automáticamente todas las campañas ni métricas privadas. Registra URL y fecha para que los hallazgos puedan verificarse.")
    st.download_button("Descargar plantilla Excel", xlsx_bytes(SOCIAL_TEMPLATE, "observaciones_digitales"),
                       "plantilla_redes_pauta.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    upload = st.file_uploader("Cargar observaciones CSV/Excel", type=["csv","xlsx","xls"], key="social_upload")
    if upload:
        df = read_upload(upload)
        st.dataframe(df.head(30), use_container_width=True)
        if st.button("Guardar observaciones en esta sesión", type="primary"):
            st.session_state.social_data = df.copy()
            st.success(f"{len(df):,} observaciones cargadas.")
    df = st.session_state.social_data
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        if "plataforma" in df:
            counts = df["plataforma"].fillna("Sin dato").value_counts().rename_axis("plataforma").reset_index(name="observaciones")
            st.plotly_chart(px.bar(counts, x="plataforma", y="observaciones", title="Observaciones por plataforma"), use_container_width=True)
        st.download_button("Exportar observaciones CSV", csv_bytes(df), "observaciones_digitales.csv", "text/csv")
    else:
        st.info("Sin observaciones cargadas todavía.")

elif page == "Medios y noticias":
    st.subheader("Cobertura en medios")
    st.download_button("Descargar plantilla Excel", xlsx_bytes(MEDIA_TEMPLATE, "medios"),
                       "plantilla_medios_noticias.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    upload = st.file_uploader("Cargar noticias/menciones CSV o Excel", type=["csv","xlsx","xls"], key="media_upload")
    if upload:
        df = read_upload(upload)
        st.dataframe(df.head(30), use_container_width=True)
        if st.button("Guardar menciones en esta sesión", type="primary"):
            st.session_state.media_data = df.copy()
            st.success(f"{len(df):,} menciones cargadas.")
    df = st.session_state.media_data
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.download_button("Exportar menciones CSV", csv_bytes(df), "menciones_medios.csv", "text/csv")
    else:
        st.info("Sin menciones cargadas. Puedes registrar titulares, fecha, medio, empresa, URL y fuente.")

elif page == "Comparativos":
    st.subheader("Comparativos con datos disponibles")
    trade = st.session_state.trade_data.copy()
    social = st.session_state.social_data.copy()
    media = st.session_state.media_data.copy()
    if not trade.empty and "empresa" in trade:
        st.markdown("#### Comercio exterior")
        st.dataframe(trade, use_container_width=True)
    else:
        st.info("Carga datos comerciales para habilitar comparaciones de comercio exterior.")
    if not social.empty and "empresa" in social:
        st.markdown("#### Actividad digital observada")
        st.dataframe(social, use_container_width=True)
    else:
        st.info("Carga observaciones digitales para comparar empresas y plataformas.")
    if not media.empty and "empresa" in media:
        st.markdown("#### Menciones en medios")
        st.dataframe(media, use_container_width=True)
    st.warning("No se calculan participación de mercado, ventas ni inversión publicitaria estimada si las fuentes no proporcionan datos suficientes.")

elif page == "Plantillas y exportación":
    st.subheader("Plantillas y exportación")
    st.write("Descarga las plantillas para preparar tus datos sin cambiar los originales.")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Plantilla comercio exterior", xlsx_bytes(TRADE_TEMPLATE), "plantilla_comercio_exterior.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.download_button("Plantilla redes y pauta", xlsx_bytes(SOCIAL_TEMPLATE), "plantilla_redes_pauta.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with c2:
        st.download_button("Plantilla medios", xlsx_bytes(MEDIA_TEMPLATE), "plantilla_medios.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.download_button("Base de competidores", csv_bytes(st.session_state.competitors), "competidores_alquimia.csv", "text/csv")
    st.subheader("Próximas mejoras")
    st.markdown("""
    - Adaptar el importador a las columnas exactas del archivo de Legiscomex.
    - Conectar fuentes de noticias RSS/API autorizadas.
    - Añadir filtros por fecha, producto, subpartida, país y empresa.
    - Añadir informes PDF/Excel y alertas programadas.
    - Integrar APIs oficiales de redes/publicidad si son compatibles con el alcance y los permisos.
    """)

st.divider()
st.caption("CompeteTrack · Prototipo de trabajo. Verifica fuentes, fechas y permisos antes de tomar decisiones comerciales.")
