# CompeteTrack — Alquimia LF

Prototipo de inteligencia competitiva en Python + Streamlit, sin Apify.

## Incluye
- Dashboard inicial.
- Lista precargada de 11 empresas candidatas, con segmentos, URLs y estado de validación.
- Importación CSV/Excel y normalización de nombres frecuentes de columnas de comercio exterior.
- Observatorio digital y menciones en medios mediante importación de archivos.
- Comparativos básicos y exportación CSV/Excel.
- Plantillas descargables.

## Importante
- Los competidores precargados son candidatos de investigación a partir de información pública, no un ranking de mercado.
- La aplicación no se conecta directamente a Legiscomex; permite cargar reportes que el usuario esté autorizado a exportar.
- No requiere ni utiliza Apify.
- No obtiene automáticamente todos los anuncios ni métricas privadas de redes sociales.
- Los valores, ventas o participación de mercado no deben inferirse si la fuente no los proporciona.

## Instalación
Requiere Python 3.10+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Formatos recomendados
Comercio exterior: `fecha, empresa, producto, subpartida, pais_origen, valor_usd, peso_neto_kg, fuente`
Redes y pauta: `fecha_observacion, empresa, plataforma, tipo_contenido, url, reproducciones, interacciones, seguidores, fuente, notas`
Medios: `fecha, empresa, medio, titular, url, tema, fuente`

La app intenta mapear algunos encabezados frecuentes a campos normalizados, pero se debe validar con la exportación real.
