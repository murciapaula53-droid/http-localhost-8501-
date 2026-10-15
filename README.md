# CompeteTrack | Alquimia LF — v7 Inteligencia competitiva

## Objetivo
Herramienta para observar la actividad digital pública de competidores: redes sociales, publicaciones, tono de comunicación, anuncios, noticias y métricas visibles.

## Módulos
- **Buscador gratuito:** prepara consultas para encontrar empresas y fuentes públicas.
- **Directorio:** conserva empresas, sitios, productos, cobertura y estado de validación.
- **Redes sociales:** registra plataformas, publicaciones, temas, tono, objetivos, visualizaciones, alcance y engagement cuando esos datos están disponibles.
- **Publicidad digital:** organiza anuncios observados, plataformas, formatos, mensajes, tono, objetivo, CTA, visualizaciones, alcance e interacciones. Permite ordenar anuncios por señales observables, sin afirmar que eso pruebe impacto causal o inversión.
- **Noticias y medios:** registra menciones y publicaciones en prensa.
- **Comparativos:** compara Alquimia LF con competidores seleccionados.
- **Oportunidades:** identifica vacíos de información y líneas de producto compartidas.

## Fuentes públicas recomendadas
- Meta Ad Library: https://www.facebook.com/ads/library/
- Google Ads Transparency Center: https://adstransparency.google.com/
- Búsqueda web, Google Noticias, LinkedIn y páginas oficiales de cada empresa.
- Canales oficiales de Instagram, Facebook, TikTok, LinkedIn y YouTube.

## Limitaciones importantes
No se promete acceso automático a todas las redes ni a métricas privadas. Visualizaciones, alcance, gasto, segmentación y resultados pueden no ser públicos. Registra la URL y fecha de consulta y utiliza el estado del dato para distinguir información verificada, estimada o no disponible. El orden de anuncios destacados es una señal orientativa basada en datos introducidos, no una medición causal del impacto.

## Instalación
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Actualización en GitHub
Sube y reemplaza `app.py` y `README.md` por los de esta versión. Conserva `requirements.txt` y los CSV existentes dentro de `data` para mantener tu directorio. Las columnas nuevas se rellenan vacías al leer archivos CSV anteriores; descarga una copia de tus datos antes de actualizar.
