import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
from datetime import datetime, timezone
import urllib.parse
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="CompeteTrack | Alquimia LF", page_icon="📊", layout="wide")
DATA = Path("data")
DATA.mkdir(exist_ok=True)

COMP_COLS = ["empresa","sitio_web","ciudad_base","cobertura","tipo","prioridad","lineas","estado","fuente","notas"]
SOCIAL_COLS = ["fecha","empresa","plataforma","tipo_contenido","tema","tono_comunicacion","objetivo","url","seguidores","alcance","me_gusta","comentarios","compartidos","visualizaciones","engagement_pct","fuente","estado_dato","notas"]
ADS_COLS = ["fecha_inicio","fecha_fin","empresa","plataforma","formato","mensaje","tono_comunicacion","objetivo","cta","url","visualizaciones","alcance","interacciones","estado_anuncio","fuente","estado_dato","notas"]
NEWS_COLS = ["fecha","empresa","medio","titular","url","tema","fuente","estado_dato","notas"]
SEARCH_COLS = ["fecha_busqueda","producto_busqueda","empresa","sitio_web","resumen","score_relevancia","ubicacion","lineas_detectadas","fuente","estado_validacion"]

def load(path, cols):
    if path.exists():
        try:
            df = pd.read_csv(path).fillna("")
            for c in cols:
                if c not in df.columns: df[c] = ""
            return df[cols]
        except Exception:
            pass
    return pd.DataFrame(columns=cols)

def save(df, path):
    df.to_csv(path, index=False, encoding="utf-8-sig")

def num(s):
    return pd.to_numeric(s, errors="coerce")

def tokens(value):
    return {x.strip().casefold() for x in str(value).replace(",", ";").split(";") if x.strip()}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_google_news(query, limit=30):
    """Fetch public Google News RSS results; no API key required."""
    url = "https://news.google.com/rss/search?q=" + urllib.parse.quote_plus(query) + "&hl=es-419&gl=CO&ceid=CO:es-419"
    headers = {"User-Agent": "CompeteTrack/1.0 (public RSS reader)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    items = []
    for item in root.findall("./channel/item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        source_node = item.find("source")
        source = (source_node.text or "Google News") if source_node is not None else "Google News"
        try:
            from email.utils import parsedate_to_datetime
            date = parsedate_to_datetime(pub).date().isoformat() if pub else datetime.now().date().isoformat()
        except Exception:
            date = datetime.now().date().isoformat()
        if title and link:
            items.append({"fecha": date, "empresa": "", "medio": source, "titular": title, "url": link,
                          "tema": "Mención web detectada automáticamente", "fuente": "Google News RSS",
                          "estado_dato": "Detectado automáticamente; revisar relevancia", "notas": "Resultado público RSS; confirmar que la mención corresponde a la empresa."})
    return items


comp_path, social_path, ads_path, news_path, search_path = (
    DATA/"competidores.csv", DATA/"redes_sociales.csv", DATA/"publicidad.csv",
    DATA/"noticias.csv", DATA/"busquedas_competidores.csv"
)
competitors = load(comp_path, COMP_COLS)
social = load(social_path, SOCIAL_COLS)
ads = load(ads_path, ADS_COLS)
news = load(news_path, NEWS_COLS)
search_history = load(search_path, SEARCH_COLS)

st.markdown("""
<style>
:root { --ct-navy:#102A43; --ct-blue:#176B87; --ct-teal:#28B6A8; --ct-pale:#EAF5F7; --ct-ink:#203040; }
.block-container {padding-top:1.35rem;padding-bottom:2.2rem; max-width:1500px;}
h1,h2,h3 {color:var(--ct-navy);}
p, label, [data-testid="stMarkdownContainer"] {color:var(--ct-ink);}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#102A43 0%,#174A63 100%);}
[data-testid="stSidebar"] * {color:#F4FAFC !important;}
[data-testid="stSidebar"] [data-testid="stRadio"] label {padding:0.32rem 0.45rem;border-radius:8px;}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {background:#23627A;}
div[data-testid="stMetric"] {background:linear-gradient(135deg,#F1FAFB 0%,#FFFFFF 100%);border:1px solid #C9E7EA;padding:15px 16px;border-radius:14px;box-shadow:0 3px 12px rgba(16,42,67,.06);}
div[data-testid="stMetric"] label {color:#176B87 !important;font-weight:600;}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {color:#102A43;}
.stButton>button, .stDownloadButton>button, button[kind="primary"] {border-radius:9px;border:0;background:#176B87;color:white;font-weight:600;}
.stButton>button:hover, .stDownloadButton>button:hover {background:#28B6A8;color:#102A43;border:0;}
div[data-testid="stDataFrame"], div[data-testid="stTable"] {border:1px solid #D6E6EA;border-radius:10px;overflow:hidden;}
input, textarea, [data-baseweb="select"] > div {border-radius:8px !important;}
.ct-brand {display:flex;align-items:center;gap:14px;padding:17px 20px;border-radius:18px;background:linear-gradient(120deg,#102A43 0%,#176B87 68%,#28B6A8 100%);margin-bottom:18px;box-shadow:0 8px 22px rgba(16,42,67,.15);}
.ct-mark {width:49px;height:49px;border:1px solid rgba(255,255,255,.5);border-radius:14px;display:flex;align-items:center;justify-content:center;color:white;font-size:27px;font-weight:800;background:rgba(255,255,255,.13);}
.ct-brand-name {font-size:26px;font-weight:800;color:#FFFFFF;letter-spacing:.2px;line-height:1.15;}
.ct-brand-sub {font-size:13px;color:#DDF5F6;margin-top:5px;}
.ct-section {background:#F0F8FA;border-left:4px solid #28B6A8;padding:12px 15px;border-radius:7px;margin:8px 0 18px 0;color:#203040;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ct-brand">
  <div class="ct-mark">C</div>
  <div>
    <div class="ct-brand-name">CompeteTrack</div>
    <div class="ct-brand-sub">INTELIGENCIA COMPETITIVA · ALQUIMIA LF · COLOMBIA</div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ◈ CompeteTrack")
    st.caption("Inteligencia competitiva")
    st.divider()
    page = st.radio("NAVEGACIÓN", ["Centro de monitoreo", "Perfil de Alquimia", "Competidores", "Redes sociales", "Publicidad digital", "Noticias y medios", "Comparativos", "Oportunidades", "Buscador de competidores"])
    st.divider()
    st.markdown("**MODO GRATUITO**")
    st.caption("Sin API externa. Las búsquedas se abren en fuentes públicas y puedes registrar los competidores que valides.")

if page == "Centro de monitoreo":
    st.subheader("Centro de monitoreo competitivo")
    st.markdown('<div class="ct-section">Seguimiento de competidores de Alquimia LF. Revisa fuentes públicas, registra evidencias y compara actividad observada. Las métricas solo se muestran cuando cuentan con datos registrados.</div>', unsafe_allow_html=True)
    # Summary metrics
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Empresas en seguimiento", max(0, len(competitors)-1))
    k2.metric("Perfiles sociales", len(social))
    k3.metric("Anuncios registrados", len(ads))
    k4.metric("Noticias registradas", len(news))
    st.markdown("### Actualización automática desde fuentes web gratuitas")
    st.caption("Consulta Google News RSS para encontrar menciones recientes de las empresas en seguimiento. No requiere Excel ni una API key. Los resultados se guardan al pulsar el botón y deben revisarse para descartar homónimos o menciones irrelevantes.")
    if st.button("🔄 Buscar novedades de todos los competidores", type="primary", key="auto_news_all"):
        fresh = []
        tracked = competitors[competitors["empresa"].astype(str).str.strip().ne("")]
        progress = st.progress(0, text="Consultando fuentes públicas…")
        for idx, (_, cr) in enumerate(tracked.iterrows()):
            cname = str(cr.get("empresa", "")).strip()
            if not cname:
                continue
            query = f'"{cname}" (químicos OR resinas OR industria OR productos)'
            try:
                found = fetch_google_news(query, limit=12)
                for item in found:
                    item["empresa"] = cname
                fresh.extend(found)
            except Exception:
                pass
            progress.progress((idx + 1) / max(1, len(tracked)), text=f"Consultando: {cname}")
        progress.empty()
        if fresh:
            new_df = pd.DataFrame(fresh, columns=NEWS_COLS)
            existing_urls = set(news["url"].astype(str)) if not news.empty else set()
            new_df = new_df[~new_df["url"].astype(str).isin(existing_urls)]
            if not new_df.empty:
                news = pd.concat([news, new_df], ignore_index=True).drop_duplicates(subset=["url"], keep="first")
                save(news, news_path)
                st.success(f"Se guardaron {len(new_df)} nuevas menciones públicas. Revisa su relevancia antes de usarlas en el análisis.")
            else:
                st.info("No se encontraron enlaces nuevos respecto a los ya registrados.")
            st.dataframe(pd.DataFrame(fresh)[["fecha","empresa","medio","titular","url"]], use_container_width=True, hide_index=True)
        else:
            st.warning("No fue posible recuperar resultados en esta consulta. Puede ser una interrupción temporal de la fuente o de la conexión del servidor.")
    st.markdown("### Actividad reciente registrada")
    activity=[]
    if not social.empty:
        for _,r in social.iterrows():
            if str(r.get("tipo_contenido", "")).lower().find("perfil corporativo") >= 0:
                continue
            activity.append({"Fecha":r.get("fecha",""),"Empresa":r.get("empresa",""),"Tipo":"Publicación social","Canal":r.get("plataforma",""),"Detalle":r.get("tema", ""),"Estado":r.get("estado_dato", ""),"Fuente":r.get("url", "")})
    if not ads.empty:
        for _,r in ads.iterrows(): activity.append({"Fecha":r.get("fecha_inicio",""),"Empresa":r.get("empresa",""),"Tipo":"Publicidad","Canal":r.get("plataforma",""),"Detalle":r.get("mensaje", ""),"Estado":r.get("estado_dato", ""),"Fuente":r.get("url", "")})
    if not news.empty:
        for _,r in news.iterrows(): activity.append({"Fecha":r.get("fecha",""),"Empresa":r.get("empresa",""),"Tipo":"Noticia","Canal":r.get("medio", ""),"Detalle":r.get("titular", ""),"Estado":r.get("estado_dato", ""),"Fuente":r.get("url", "")})
    if activity:
        act=pd.DataFrame(activity).sort_values("Fecha",ascending=False)
        st.dataframe(act,use_container_width=True,hide_index=True)
    else:
        st.info("Aún no hay publicaciones individuales, anuncios ni noticias verificadas. Los perfiles y empresas iniciales sí están cargados. Usa las búsquedas de fuentes públicas de abajo para comenzar el monitoreo y registra solo hallazgos comprobables.")
    st.markdown("### Búsquedas rápidas de inteligencia competitiva")
    import urllib.parse
    companies = [x for x in competitors["empresa"].astype(str).tolist() if x and x != "Alquimia LF"]
    focus = st.selectbox("Empresa a investigar", companies, index=0 if companies else None, placeholder="Selecciona una empresa")
    if focus:
        row=competitors[competitors["empresa"].astype(str)==focus]
        website=str(row.iloc[0]["sitio_web"]) if len(row) else ""
        q=urllib.parse.quote_plus(f'"{focus}"')
        qnews=urllib.parse.quote_plus(f'"{focus}" (resinas OR químicos OR industria)')
        st.markdown(f"- [Buscar noticias recientes de {focus}](https://news.google.com/search?q={qnews})")
        st.markdown(f"- [Buscar publicaciones y menciones web](https://www.google.com/search?q={q})")
        st.markdown(f"- [Buscar perfiles en redes sociales](https://www.google.com/search?q={q}+Instagram+Facebook+LinkedIn+TikTok)")
        st.markdown(f"- [Buscar anuncios en Meta Ad Library](https://www.facebook.com/ads/library/)")
        st.markdown(f"- [Consultar anuncios en Google Ads Transparency Center](https://adstransparency.google.com/)")
        if website and website.startswith("http"): st.markdown(f"- [Abrir sitio web oficial](<{website}>)")
    st.caption("Modo gratuito: los enlaces abren fuentes públicas para consultar. No se afirma monitoreo automático ni se inventan publicaciones o métricas.")

elif page == "Perfil de Alquimia":
    st.subheader("Perfil de empresa base · Alquimia LF Chemicals")
    st.markdown("### Insumos químicos industriales de alta calidad")
    st.write("Alquimia LF se presenta como proveedor de insumos químicos industriales, con soluciones especializadas para moldes, resinas y limpieza industrial avanzada.")
    a,b,c=st.columns(3)
    a.metric("Ciudad publicada", "Bogotá")
    b.metric("Líneas principales", "3")
    c.metric("Perfiles sociales", "3")
    st.markdown("#### Portafolio identificado en el sitio web")
    portfolio=pd.DataFrame([
        {"Línea": "Resinas de alta calidad", "Descripción": "Resinas para aplicaciones industriales exigentes", "Estado": "Identificado en la web"},
        {"Línea": "Insumos para moldes", "Descripción": "Desmoldantes, selladores y productos para procesos de moldeo", "Estado": "Identificado en la web"},
        {"Línea": "Limpieza industrial", "Descripción": "Soluciones para limpieza y mantenimiento de equipos", "Estado": "Identificado en la web"},
        {"Línea": "Otros insumos químicos", "Descripción": "Bicarbonato de sodio, cloro, siliconas, alcohol industrial, desengrasantes, oxígeno activo y productos de aseo", "Estado": "Mencionado en la web; catálogo por validar"},
    ])
    st.dataframe(portfolio,use_container_width=True,hide_index=True)
    st.markdown("#### Datos corporativos publicados")
    st.markdown("- **Sitio web:** [alquimialf.com](https://alquimialf.com/)\n- **Dirección publicada:** Cra. 25 #67-86, Bogotá\n- **Teléfono publicado:** +57 311 666 9223\n- **Horario publicado:** 9:00 a. m. – 5:00 p. m.")
    st.markdown("#### Redes sociales oficiales compartidas")
    st.markdown("- [Instagram · @alquimiachemicals](https://instagram.com/alquimiachemicals)\n- [Facebook · Alquimia LF](https://www.facebook.com/share/1M7fodJNYA/)\n- [TikTok · @alquimialf](https://www.tiktok.com/@alquimialf)")
    st.info("Este perfil funciona como referencia para el benchmarking. La comparación por producto específico requiere validar el catálogo detallado y las referencias comerciales.")

if page == "Buscador de competidores":
    st.subheader("Encuentra nuevos competidores")
    st.markdown('<div class="ct-section">Escribe un producto, materia prima o categoría y el mercado que quieres investigar. CompeteTrack preparará búsquedas en fuentes públicas para encontrar empresas, revisar sus sitios y registrar las que compitan con Alquimia LF.</div>', unsafe_allow_html=True)
    with st.form("competitor_search_form"):
        product = st.text_input("Producto o categoría", placeholder="Ej. resinas de poliéster, siliconas para moldes")
        country = st.selectbox("Mercado", ["Colombia","Bogotá, Colombia","Medellín, Colombia","Cali, Colombia","Barranquilla, Colombia","Latinoamérica"])
        submitted = st.form_submit_button("Generar búsquedas", type="primary")
    if submitted:
        if not product.strip():
            st.warning("Escribe primero un producto o categoría.")
        else:
            import urllib.parse
            term = product.strip()
            market = country
            q = urllib.parse.quote_plus(f"empresas proveedores fabricantes {term} {market}")
            q_sites = urllib.parse.quote_plus(f"{term} {market} fabricantes proveedores empresas")
            q_news = urllib.parse.quote_plus(f"{term} {market} industria noticias")
            q_linkedin = urllib.parse.quote_plus(f"{term} {market}")
            links = [
                ("Google: empresas y proveedores", f"https://www.google.com/search?q={q}"),
                ("Bing: empresas y proveedores", f"https://www.bing.com/search?q={q}"),
                ("Google: páginas y catálogos", f"https://www.google.com/search?q={q_sites}+site%3A.com.co+OR+site%3A.com"),
                ("Google Noticias: sector y empresas", f"https://news.google.com/search?q={q_news}"),
                ("LinkedIn: empresas y perfiles", f"https://www.linkedin.com/search/results/companies/?keywords={q_linkedin}"),
                ("Meta Ad Library: anuncios públicos", "https://www.facebook.com/ads/library/"),
                ("Google Ads Transparency Center", "https://adstransparency.google.com/"),
            ]
            st.session_state["free_search_links"] = links
            st.session_state["free_search_query"] = term
            st.session_state["free_search_market"] = market
            hist_row = pd.DataFrame([{
                "fecha_busqueda":datetime.now().strftime("%Y-%m-%d %H:%M"),
                "producto_busqueda":term,
                "empresa":"",
                "sitio_web":"",
                "resumen":f"Búsqueda preparada en modo gratuito para {market}",
                "score_relevancia":"",
                "ubicacion":market,
                "lineas_detectadas":term,
                "fuente":"Google/Bing/Google News/LinkedIn/centros de transparencia",
                "estado_validacion":"Enlaces generados; resultados por revisar"
            }], columns=SEARCH_COLS)
            save(pd.concat([search_history, hist_row], ignore_index=True), search_path)
            st.success("Listo. Abre los enlaces, revisa los resultados y registra los competidores que confirmes.")
    if "free_search_links" in st.session_state:
        st.markdown(f"### Búsquedas para: {st.session_state.get('free_search_query','')}")
        st.caption(f"Mercado: {st.session_state.get('free_search_market','')}")
        for label, url in st.session_state["free_search_links"]:
            st.markdown(f"- [{label}]({url})")
        st.divider()
        st.markdown("### Registrar un competidor encontrado")
        with st.form("add_candidate_free"):
            candidate = st.text_input("Nombre de la empresa")
            website = st.text_input("Sitio web")
            city = st.text_input("Ciudad base (si la encuentras)")
            lines = st.text_input("Productos o líneas relacionadas", value=st.session_state.get("free_search_query",""))
            source = st.text_input("Enlace donde encontraste la empresa")
            notes = st.text_area("Observaciones / evidencia")
            add_candidate = st.form_submit_button("Guardar competidor")
        if add_candidate:
            if not candidate.strip():
                st.warning("Ingresa el nombre de la empresa.")
            else:
                current = load(comp_path, COMP_COLS)
                same = current["empresa"].astype(str).str.casefold().eq(candidate.strip().casefold()).any()
                if same:
                    st.warning("Esta empresa ya aparece en el directorio. Puedes editar su registro en el módulo Competidores.")
                else:
                    new = pd.DataFrame([{
                        "empresa":candidate.strip(),"sitio_web":website.strip(),"ciudad_base":city.strip() or "Por validar",
                        "cobertura":st.session_state.get("free_search_market","Por validar"),
                        "tipo":"Candidato encontrado en fuente pública","prioridad":"Por evaluar",
                        "lineas":lines.strip(),"estado":"Pendiente de validación",
                        "fuente":source.strip() or "Búsqueda pública","notas":notes.strip()
                    }], columns=COMP_COLS)
                    save(pd.concat([current,new], ignore_index=True), comp_path)
                    st.success(f"{candidate.strip()} se guardó en el directorio. Verifica sus datos antes de clasificarlo.")
    if not search_history.empty:
        with st.expander("Historial de búsquedas"):
            st.dataframe(search_history, use_container_width=True, hide_index=True)
            st.download_button("Descargar historial CSV", search_history.to_csv(index=False).encode("utf-8-sig"), "historial_busquedas.csv", "text/csv")

elif page == "Competidores":
    st.subheader("Directorio de competidores")
    q = st.text_input("Buscar por empresa, producto, ciudad o estado")
    view = competitors.copy()
    if q.strip():
        view = view[view.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)]
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.markdown("### Editar / validar empresas")
    edited = st.data_editor(competitors, num_rows="dynamic", use_container_width=True, key="competitor_editor")
    if st.button("Guardar directorio"):
        save(edited[COMP_COLS], comp_path)
        st.success("Directorio guardado.")
    st.download_button("Descargar directorio CSV", competitors.to_csv(index=False).encode("utf-8-sig"), "competidores_alquimia.csv", "text/csv")

elif page == "Redes sociales":
    st.subheader("Monitoreo de redes sociales y publicaciones")
    st.markdown('<div class="ct-section">Identifica en qué plataformas está presente cada competidor, revisa sus publicaciones, analiza el tono de comunicación y compara las visualizaciones y la interacción observadas.</div>', unsafe_allow_html=True)
    if social.empty:
        st.info("Aún no hay publicaciones registradas. Usa la plantilla o registra observaciones de fuentes públicas para comenzar el análisis.")
    else:
        f1, f2 = st.columns(2)
        companies = f1.multiselect("Empresas", sorted(social["empresa"].astype(str).unique()), key="social_companies")
        platforms = f2.multiselect("Redes sociales", sorted(social["plataforma"].astype(str).unique()), key="social_platforms")
        view = social.copy()
        if companies: view = view[view["empresa"].isin(companies)]
        if platforms: view = view[view["plataforma"].isin(platforms)]
        k1,k2,k3,k4 = st.columns(4)
        k1.metric("Publicaciones registradas", len(view))
        k2.metric("Redes observadas", view["plataforma"].nunique() if len(view) else 0)
        k3.metric("Visualizaciones registradas", f"{int(num(view['visualizaciones']).sum()) if num(view['visualizaciones']).notna().any() else 0:,}")
        k4.metric("Engagement promedio", f"{num(view['engagement_pct']).mean():.2f}%" if num(view['engagement_pct']).notna().any() else "Sin datos")
        st.markdown("#### ¿En qué redes se mueve cada competidor?")
        presence = view.groupby(["empresa","plataforma"], as_index=False).size().rename(columns={"size":"Publicaciones observadas"})
        if len(presence):
            st.dataframe(presence, use_container_width=True, hide_index=True)
            st.plotly_chart(px.bar(presence, x="empresa", y="Publicaciones observadas", color="plataforma", barmode="group", title="Actividad observada por red social"), use_container_width=True)
        st.markdown("#### Publicaciones y tono de comunicación")
        cols_show = [c for c in ["fecha","empresa","plataforma","tipo_contenido","tema","tono_comunicacion","objetivo","url","visualizaciones","alcance","engagement_pct","fuente","estado_dato"] if c in view.columns]
        st.dataframe(view[cols_show], use_container_width=True, hide_index=True)
        if num(view["visualizaciones"]).notna().any():
            ranked = view.assign(_views=num(view["visualizaciones"])).sort_values("_views", ascending=False).head(10)
            st.markdown("#### Publicaciones con más visualizaciones registradas")
            st.dataframe(ranked[cols_show], use_container_width=True, hide_index=True)
    with st.expander("Registrar / importar publicaciones"):
        st.caption("Registra únicamente métricas visibles en la fuente o reportadas de forma verificable. Marca la fuente y el estado del dato.")
        st.write("Columnas de la plantilla: " + ", ".join(SOCIAL_COLS))
        st.download_button("Descargar plantilla CSV de redes", pd.DataFrame(columns=SOCIAL_COLS).to_csv(index=False).encode("utf-8-sig"), "plantilla_redes_competetrack.csv", "text/csv")
        up = st.file_uploader("Cargar registros desde CSV o Excel", type=["csv","xlsx"], key="social_upload")
        if up:
            incoming = pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
            missing = [x for x in SOCIAL_COLS if x not in incoming.columns]
            if missing: st.error("A la plantilla le faltan columnas: " + ", ".join(missing))
            elif st.button("Guardar publicaciones", key="save_social"):
                save(pd.concat([social,incoming[SOCIAL_COLS]],ignore_index=True),social_path)
                st.success("Publicaciones guardadas. Recarga la aplicación para ver los indicadores.")

elif page == "Publicidad digital":
    st.subheader("Publicidad digital de la competencia")
    st.markdown('<div class="ct-section">Registra anuncios públicos para comparar plataformas, formatos, mensajes, llamadas a la acción y resultados visibles. El rendimiento se estima solo con las métricas disponibles; no equivale al gasto ni al impacto total real.</div>', unsafe_allow_html=True)
    if ads.empty:
        st.info("Aún no hay anuncios registrados. Revisa las bibliotecas públicas de anuncios y agrega los anuncios que puedas verificar.")
    else:
        f1,f2 = st.columns(2)
        companies = f1.multiselect("Empresas", sorted(ads["empresa"].astype(str).unique()), key="ads_companies")
        platforms = f2.multiselect("Plataformas", sorted(ads["plataforma"].astype(str).unique()), key="ads_platforms")
        view = ads.copy()
        if companies: view = view[view["empresa"].isin(companies)]
        if platforms: view = view[view["plataforma"].isin(platforms)]
        a,b,c,d = st.columns(4)
        a.metric("Anuncios observados", len(view))
        b.metric("Plataformas", view["plataforma"].nunique() if len(view) else 0)
        c.metric("Visualizaciones reportadas", f"{int(num(view['visualizaciones']).sum()) if num(view['visualizaciones']).notna().any() else 0:,}")
        d.metric("Interacciones reportadas", f"{int(num(view['interacciones']).sum()) if num(view['interacciones']).notna().any() else 0:,}")
        st.markdown("#### ¿Dónde pauta cada empresa?")
        counts = view.groupby(["empresa","plataforma"], as_index=False).size().rename(columns={"size":"Anuncios observados"})
        if len(counts):
            st.dataframe(counts, use_container_width=True, hide_index=True)
            st.plotly_chart(px.bar(counts, x="empresa", y="Anuncios observados", color="plataforma", barmode="group", title="Anuncios observados por plataforma"), use_container_width=True)
        st.markdown("#### Anuncios y mensajes observados")
        show = [c for c in ["fecha_inicio","fecha_fin","empresa","plataforma","formato","mensaje","tono_comunicacion","objetivo","cta","url","visualizaciones","alcance","interacciones","estado_anuncio","fuente","estado_dato"] if c in view.columns]
        st.dataframe(view[show], use_container_width=True, hide_index=True)
        if num(view["visualizaciones"]).notna().any() or num(view["interacciones"]).notna().any():
            ranked = view.copy()
            ranked["_views"] = num(ranked["visualizaciones"]).fillna(0)
            ranked["_interactions"] = num(ranked["interacciones"]).fillna(0)
            ranked["_observed_signal"] = ranked["_views"] + ranked["_interactions"] * 5
            st.markdown("#### Anuncios destacados por señal de interacción observable")
            st.caption("Orden orientativo basado en visualizaciones e interacciones registradas; no demuestra causalidad ni revela inversión publicitaria.")
            st.dataframe(ranked.sort_values("_observed_signal", ascending=False)[show].head(10), use_container_width=True, hide_index=True)
    with st.expander("Importar anuncios observados"):
        st.caption("Fuentes sugeridas: Meta Ad Library y Google Ads Transparency Center. Registra fecha de consulta y URL de la fuente.")
        st.write("Columnas de la plantilla: " + ", ".join(ADS_COLS))
        st.download_button("Descargar plantilla CSV de anuncios", pd.DataFrame(columns=ADS_COLS).to_csv(index=False).encode("utf-8-sig"), "plantilla_anuncios_competetrack.csv", "text/csv")
        up=st.file_uploader("Cargar anuncios desde CSV o Excel",type=["csv","xlsx"],key="ads_upload")
        if up:
            incoming=pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
            missing=[x for x in ADS_COLS if x not in incoming.columns]
            if missing: st.error("A la plantilla le faltan columnas: "+", ".join(missing))
            elif st.button("Guardar anuncios", key="save_ads"):
                save(pd.concat([ads,incoming[ADS_COLS]],ignore_index=True),ads_path)
                st.success("Anuncios guardados.")

elif page == "Noticias y medios":
    st.subheader("Noticias y medios")
    st.markdown("Consulta menciones públicas sin cargar archivos. Los resultados se guardan automáticamente y se deduplican por enlace.")
    selected_news_companies = st.multiselect("Empresas para consultar", competitors["empresa"].astype(str).tolist(), default=[x for x in competitors["empresa"].astype(str).tolist() if x and x != "Alquimia LF"][:5], key="auto_news_companies")
    if st.button("Buscar noticias automáticamente", type="primary", key="auto_news_selected"):
        found_all=[]
        bar=st.progress(0, text="Buscando noticias públicas…")
        for i, cname in enumerate(selected_news_companies):
            try:
                found=fetch_google_news(f'"{cname}" (químicos OR resinas OR industria OR productos)', limit=15)
                for item in found: item["empresa"] = cname
                found_all.extend(found)
            except Exception:
                pass
            bar.progress((i+1)/max(1,len(selected_news_companies)), text=f"Consultando {cname}")
        bar.empty()
        if found_all:
            incoming=pd.DataFrame(found_all, columns=NEWS_COLS)
            seen=set(news["url"].astype(str)) if not news.empty else set()
            incoming=incoming[~incoming["url"].astype(str).isin(seen)]
            news=pd.concat([news,incoming],ignore_index=True).drop_duplicates(subset=["url"],keep="first")
            save(news,news_path)
            st.success(f"Consulta terminada. {len(incoming)} nuevas menciones guardadas.")
        else:
            st.warning("No se recuperaron resultados esta vez. Intenta de nuevo más tarde.")
    if news.empty: st.info("Todavía no hay noticias cargadas. Puedes importar menciones desde fuentes públicas.")
    else:
        companies=st.multiselect("Empresas",sorted(news["empresa"].astype(str).unique()))
        view=news[news["empresa"].isin(companies)] if companies else news
        st.dataframe(view,use_container_width=True,hide_index=True)
    with st.expander("Importar noticias"):
        st.write("Columnas: "+", ".join(NEWS_COLS))
        st.download_button("Plantilla CSV",pd.DataFrame(columns=NEWS_COLS).to_csv(index=False).encode("utf-8-sig"),"plantilla_noticias.csv","text/csv")
        up=st.file_uploader("Cargar CSV o Excel de noticias",type=["csv","xlsx"],key="news_upload")
        if up:
            incoming=pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
            missing=[x for x in NEWS_COLS if x not in incoming.columns]
            if missing: st.error("Faltan columnas: "+", ".join(missing))
            elif st.button("Guardar noticias"):
                save(pd.concat([news,incoming[NEWS_COLS]],ignore_index=True),news_path); st.success("Noticias guardadas.")

elif page == "Comparativos":
    st.subheader("Comparar Alquimia con la competencia")
    names=competitors["empresa"].astype(str).tolist()
    options=[x for x in names if x!="Alquimia LF"]
    selected=st.multiselect("Selecciona competidores",options,default=options[:3])
    chosen=["Alquimia LF"]+selected
    view=competitors[competitors["empresa"].isin(chosen)]
    st.markdown("#### Comparación de empresas")
    st.dataframe(view[["empresa","ciudad_base","cobertura","tipo","prioridad","lineas","sitio_web","estado"]],use_container_width=True,hide_index=True)
    matrix=[]
    all_lines=sorted(set().union(*(tokens(x) for x in view["lineas"]))) if len(view) else []
    for _,r in view.iterrows():
        d={"Empresa":r["empresa"]}
        for line in all_lines: d[line.title()]="Sí" if line in tokens(r["lineas"]) else "No registrado"
        matrix.append(d)
    if matrix:
        st.markdown("#### Matriz de líneas de producto")
        st.caption("La comparación usa descripciones textuales; «No registrado» no significa que no comercialice ese producto.")
        st.dataframe(pd.DataFrame(matrix),use_container_width=True,hide_index=True)
    rows=[]
    for name in chosen:
        sr=social[social["empresa"].astype(str)==name]
        ar=ads[ads["empresa"].astype(str)==name]
        nr=news[news["empresa"].astype(str)==name]
        rows.append({"Empresa":name,"Publicaciones registradas":len(sr),"Redes observadas":sr["plataforma"].nunique() if len(sr) else 0,"Anuncios registrados":len(ar),"Plataformas con anuncios":ar["plataforma"].nunique() if len(ar) else 0,"Noticias registradas":len(nr),"Visualizaciones reportadas":num(sr["visualizaciones"]).sum(min_count=1) if len(sr) else None,"Engagement promedio (%)":num(sr["engagement_pct"]).mean() if len(sr) else None})
    metrics=pd.DataFrame(rows)
    st.markdown("#### Actividad digital registrada")
    st.dataframe(metrics,use_container_width=True,hide_index=True)
    st.download_button("Descargar comparativo CSV",metrics.to_csv(index=False).encode("utf-8-sig"),"comparativo_alquimia.csv","text/csv")

elif page == "Oportunidades":
    st.subheader("Oportunidades para Alquimia")
    st.write("Las oportunidades son hipótesis de trabajo basadas en los datos disponibles y deben verificarse.")
    if len(competitors):
        tokens_list=[]
        for _,r in competitors.iterrows():
            for line in tokens(r["lineas"]): tokens_list.append({"Línea":line.title(),"Empresa":r["empresa"]})
        if tokens_list:
            counts=pd.DataFrame(tokens_list).groupby("Línea").agg(Empresas=("Empresa","nunique"),Competidores=("Empresa",lambda x:", ".join(sorted(set(x))))).reset_index()
            st.dataframe(counts[counts["Empresas"]>1].sort_values("Empresas",ascending=False),use_container_width=True,hide_index=True)
        observed=set(social["empresa"].astype(str))|set(ads["empresa"].astype(str))|set(news["empresa"].astype(str))
        no_data=[x for x in competitors["empresa"].astype(str) if x not in observed and x!="Alquimia LF"]
        st.write(f"Empresas sin registros sociales, anuncios o noticias: **{len(no_data)}**")
        if no_data: st.caption(", ".join(no_data))
        st.caption("Esto señala vacíos de información en la aplicación, no ausencia de actividad de las empresas.")

st.divider()
st.caption("CompeteTrack · Prototipo gratuito. Usa fuentes públicas, registra la fecha y la URL de cada evidencia, y distingue los datos verificados de los no disponibles.")
