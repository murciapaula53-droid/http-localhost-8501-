# CompeteTrack | Alquimia LF — versión gratuita sin API

Prototipo interactivo en Streamlit para organizar y analizar información pública de competidores.

## Qué incluye
- Resumen del directorio.
- Buscador gratuito que prepara enlaces de búsqueda para Google, Bing, Google Noticias, LinkedIn y centros públicos de transparencia de anuncios.
- Registro manual de competidores encontrados y guardado en CSV.
- Directorio editable de empresas.
- Módulos de redes sociales, publicidad digital, noticias, comparativos y oportunidades.
- Importación de datos desde CSV/Excel en los módulos que la admiten.

## Importante sobre el modo sin API
Esta versión no consulta automáticamente ni extrae todos los resultados de Google/Bing. Abre enlaces de búsqueda para que la persona revise las fuentes y registre los competidores pertinentes. Tampoco puede garantizar métricas completas de anuncios, seguidores o visualizaciones, ya que parte de esos datos no es pública o requiere herramientas específicas.

## Instalación local
1. Instala Python 3.10 o superior.
2. Descomprime el ZIP.
3. Abre una terminal dentro de la carpeta del proyecto.
4. Ejecuta:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Publicación
Se puede subir el proyecto a GitHub y desplegarlo en Streamlit Community Cloud. Los archivos CSV locales pueden no persistir de forma permanente en algunos despliegues; descarga copias periódicas o conecta un almacenamiento persistente si se necesita conservar datos en la nube.

## Uso responsable
Verifica cada empresa y cada dato en su fuente original. Respeta las condiciones de uso de los sitios consultados y no interpretes candidatos encontrados como competidores confirmados.
