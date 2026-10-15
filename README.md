# CompeteTrack | Alquimia LF — v10 Centro de monitoreo

Aplicación Streamlit para benchmarking e inteligencia competitiva con Alquimia LF como empresa base.

## Incluye
- Centro de monitoreo como pantalla inicial: actividad registrada, indicadores y búsquedas rápidas de fuentes públicas.
- Perfil de Alquimia LF con líneas de negocio, datos publicados en su web y enlaces sociales compartidos.
- Directorio inicial de competidores candidatos con fuentes corporativas.
- Módulos para redes/publicaciones, publicidad, noticias, comparativos y oportunidades.
- CSV para registrar e importar hallazgos con fecha, fuente y estado de validación.

## Importante sobre el monitoreo
Esta versión es gratuita y no usa API externa. Los enlaces a buscadores, Google News y bibliotecas de anuncios ayudan a investigar, pero no extraen automáticamente todos los resultados. No se inventan noticias, campañas, visualizaciones ni métricas. Los perfiles sociales precargados son perfiles, no publicaciones individuales.

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Community Cloud
Sube `app.py`, `README.md` y la carpeta `data` a tu repositorio. Conserva `requirements.txt`. En Streamlit, el archivo principal debe ser `app.py`.

**Antes de reemplazar CSV en GitHub, descarga una copia de los que ya tengas si has añadido registros manuales.**


## Monitoreo automático gratuito de noticias

En el Centro de monitoreo o en Noticias y medios, usa el botón de búsqueda automática para consultar Google News RSS por cada empresa. No requiere Excel, API key ni servicio de pago. Los resultados se guardan en `data/noticias.csv` y se deduplican por URL.

**Limitaciones:** RSS devuelve menciones web/noticias, no todas las publicaciones de redes sociales. Los resultados requieren revisión de relevancia; la aplicación no inventa métricas de alcance ni visualizaciones. Para redes y anuncios, abre las fuentes públicas enlazadas y solo registra métricas que estén realmente visibles o accesibles. El monitoreo de noticias es bajo demanda (al pulsar el botón), con caché de una hora; no es una alerta en tiempo real.
