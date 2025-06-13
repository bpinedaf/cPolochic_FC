# Demo Interactivo – Pronóstico de Caudales en la Cuenca del Polochic

Este proyecto es una demostración funcional del potencial para **visualizar, estimar y pronosticar caudales** en las subcuencas del sistema hídrico **Cahabón–Polochic** (Guatemala), combinando datos satelitales, modelos matemáticos y visualización interactiva.

---

##Funcionalidades principales

- Mapa interactivo con:
  - Límites administrativos
  - Cuenca Polochic
  - Puntos de interés (hidroeléctricas)
- Cálculo de caudal mensual estimado con base en:
  - Precipitación mensual satelital (CHIRPS)
  - Coeficiente de escorrentía ajustable
- Pronóstico automático hasta 12 meses usando Prophet
- Exportación a PDF con resumen ejecutivo por subcuenca

---

##Tecnologías utilizadas

- Python (Pandas, Plotly, Prophet, Folium, Streamlit)
- Google Earth Engine (extracción de datos climáticos)
- Streamlit Cloud (para despliegue web)
- FPDF (para generación de reportes ejecutivos)

---

##Estructura de archivos

| Archivo | Descripción |
|--------|-------------|
| `main.py` | Aplicación principal de Streamlit |
| `pronostico.py` | Funciones para cálculo y exportación de pronóstico |
| `Precipitacion_Subcuencas_Polochic_limpio.csv` | Datos de entrada optimizados (ver nota abajo) |
| `Cuenca_Polochic.geojson` | Geometría de la cuenca |
| `AOI_Polochic.geojson` | Puntos de interés (hidroeléctricas) |
| `World_Administrative.geojson` | Límites internacionales |

---

##Consideraciones técnicas

- El archivo original de precipitación generado desde Google Earth Engine incluía una columna `.geo` con geometría completa, lo cual **inflaba el tamaño del archivo a más de 600 MB**.
- Para facilitar su uso en GitHub y Streamlit Cloud, se eliminó esa columna, lo que redujo el peso a **solo 118 KB**.
- Las geometrías necesarias para visualización se mantienen en archivos `.geojson`, separados y ligeros.

---

##Despliegue en línea

Una vez desplegada en [Streamlit Community Cloud](https://streamlit.io/cloud), la aplicación puede ser accedida desde este enlace:

 **[https://cpolochicfc-5qsnq8ubrqhlheyyglxpum.streamlit.app](https://cpolochicfc-5qsnq8ubrqhlheyyglxpum.streamlit.app)** 
---

##Próximos pasos sugeridos

- Agregar resumen automatizado por subcuenca en PDF
- Incorporar alertas por exceso o déficit de caudal
- Desarrollar módulo de comparación histórica contra eventos críticos
- Explorar integración de NDVI o humedad superficial

---

## ✉ Contacto

Este demo fue desarrollado como parte de una propuesta técnica para evaluación de soluciones hidroclimáticas en el contexto energético de Guatemala.  
Para más información técnica o licenciamiento de uso, contactar a:

**Billy Pineda**  
🌐 GitHub: [@bpinedaf](https://github.com/bpinedaf)

---
