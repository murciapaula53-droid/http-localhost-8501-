import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="CompeteTrack | Alquimia LF", page_icon="📊", layout="wide")
DATA = Path("data")
DATA.mkdir(exist_ok=True)

COMP_COLS = ["empresa","sitio_web","ciudad_base","cobertura","tipo","prioridad","lineas","estado","fuente","notas"]
SOCIAL_COLS = ["fecha","empresa","plataforma","tipo_contenido","url","seguidores","me_gusta","comentarios","compartidos","visualizaciones","engagement_pct","fuente","estado_dato","notas"]
ADS_COLS = ["fecha_inicio","fecha_fin","empresa","plataforma","formato","mensaje","cta","url","estado_anuncio","fuente","estado_dato","notas"]
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
.block-container {padding-top:1.25rem;padding-bottom:2rem;}
h1,h2,h3 {color:#34313A;}
div[data-testid="stMetric"] {background:#FFF4F8;border:1px solid #F0D9E3;padding:12px;border-radius:12px;}
</style>
""", unsafe_allow_html=True)

st.title("CompeteTrack")
st.caption("Inteligencia competitiva interactiva para Alquimia LF · Colombia")
st.info("Los resultados de búsqueda son empresas candidatas encontradas en la web. Revisa las fuentes y confirma ubicación, portafolio y relación competitiva antes de tomar decisiones.")

with st.sidebar:
    st.markdown("## Menú")
    page = st.radio("Módulo", ["Resumen","Buscador automático","Competidores","Redes sociales","Publicidad digital","Noticias y medios","Comparativos","Oportunidades"])
    st.divider()
    st.markdown("**Modo gratuito**")
    st.caption("Sin API key ni servicios de búsqueda pagos. El buscador abre consultas en fuentes públicas; tú eliges los resultados que deseas guardar.")

if page == "Resumen":
    st.subheader("Vista general")
    a,b,c,d = st.columns(4)
    a.metric("Competidores registrados", len(competitors))
    b.metric("Registros sociales", len(social))
    c.metric("Anuncios registrados", len(ads))
    d.metric("Noticias registradas", len(news))
    q = st.text_input("Buscar en el directorio", placeholder="Empresa, producto, ciudad o línea")
    if q.strip():
        mask = competitors.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)
        st.dataframe(competitors[mask], use_container_width=True, hide_index=True)
    st.dataframe(competitors[["empresa","ciudad_base","cobertura","tipo","prioridad","estado"]], use_container_width=True, hide_index=True)
    st.caption("Los conteos muestran registros guardados, no la actividad total del mercado.")

elif page == "Buscador automático":
    st.subheader("Buscador gratuito de competidores")
    st.write("Este modo no utiliza una API externa. Genera búsquedas listas para abrir en buscadores y fuentes públicas. Revisa cada resultado y agrega al directorio solo las empresas relevantes.")
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
    st.subheader("Análisis de redes sociales")
    if social.empty:
        st.info("Aún no hay métricas sociales cargadas. Este módulo permite analizar datos importados; la búsqueda web no proporciona automáticamente métricas privadas de todas las plataformas.")
    else:
        c1,c2 = st.columns(2)
        companies = c1.multiselect("Empresas", sorted(social["empresa"].astype(str).unique()))
        platforms = c2.multiselect("Plataformas", sorted(social["plataforma"].astype(str).unique()))
        view = social.copy()
        if companies: view = view[view["empresa"].isin(companies)]
        if platforms: view = view[view["plataforma"].isin(platforms)]
        st.dataframe(view, use_container_width=True, hide_index=True)
        if num(view["visualizaciones"]).notna().any():
            chart = view.assign(_v=num(view["visualizaciones"])).groupby("empresa",as_index=False)["_v"].sum()
            st.plotly_chart(px.bar(chart,x="empresa",y="_v",title="Visualizaciones registradas"),use_container_width=True)
    with st.expander("Importar datos de redes sociales"):
        st.write("Columnas: " + ", ".join(SOCIAL_COLS))
        st.download_button("Plantilla CSV", pd.DataFrame(columns=SOCIAL_COLS).to_csv(index=False).encode("utf-8-sig"), "plantilla_redes.csv", "text/csv")
        up = st.file_uploader("Cargar CSV o Excel", type=["csv","xlsx"], key="social_upload")
        if up:
            incoming = pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
            missing = [x for x in SOCIAL_COLS if x not in incoming.columns]
            if missing: st.error("Faltan columnas: " + ", ".join(missing))
            elif st.button("Guardar redes"):
                save(pd.concat([social,incoming[SOCIAL_COLS]],ignore_index=True),social_path)
                st.success("Registros guardados. Recarga la aplicación.")

elif page == "Publicidad digital":
    st.subheader("Publicidad digital")
    if ads.empty: st.info("Todavía no hay anuncios registrados. Puedes importar anuncios observados desde fuentes públicas.")
    else:
        companies = st.multiselect("Empresas", sorted(ads["empresa"].astype(str).unique()))
        platforms = st.multiselect("Plataformas", sorted(ads["plataforma"].astype(str).unique()))
        view = ads.copy()
        if companies: view=view[view["empresa"].isin(companies)]
        if platforms: view=view[view["plataforma"].isin(platforms)]
        st.dataframe(view,use_container_width=True,hide_index=True)
    with st.expander("Importar anuncios"):
        st.write("Columnas: " + ", ".join(ADS_COLS))
        st.download_button("Plantilla CSV",pd.DataFrame(columns=ADS_COLS).to_csv(index=False).encode("utf-8-sig"),"plantilla_publicidad.csv","text/csv")
        up=st.file_uploader("Cargar CSV o Excel de anuncios",type=["csv","xlsx"],key="ads_upload")
        if up:
            incoming=pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
            missing=[x for x in ADS_COLS if x not in incoming.columns]
            if missing: st.error("Faltan columnas: "+", ".join(missing))
            elif st.button("Guardar anuncios"):
                save(pd.concat([ads,incoming[ADS_COLS]],ignore_index=True),ads_path); st.success("Anuncios guardados.")

elif page == "Noticias y medios":
    st.subheader("Noticias y medios")
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
        rows.append({"Empresa":name,"Publicaciones registradas":len(sr),"Plataformas":sr["plataforma"].nunique() if len(sr) else 0,"Anuncios registrados":len(ar),"Noticias registradas":len(nr),"Visualizaciones reportadas":num(sr["visualizaciones"]).sum(min_count=1) if len(sr) else None,"Engagement promedio (%)":num(sr["engagement_pct"]).mean() if len(sr) else None})
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
st.caption("CompeteTrack · Prototipo. La búsqueda automática usa Tavily; revisa las fuentes y valida cada candidato antes de considerarlo competidor.")
