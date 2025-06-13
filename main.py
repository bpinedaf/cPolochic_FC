import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium
import json
from pronostico import generar_pronostico, exportar_pdf


# Configuración inicial
st.set_page_config(page_title="Demo Caudal Polochic", layout="wide")
st.title("Dashboard de Caudal Estimado - Cuenca Polochic")

st.subheader("Mapa de la Cuenca del Polochic")

# Cargar el GeoJSON
with open("Cuenca_Polochic.geojson", "r", encoding="utf-8") as f:
    cuenca_geojson = json.load(f)

# Extraer coordenadas centrales (simple aproximación)
coords = cuenca_geojson["features"][0]["geometry"]["coordinates"][0]
center_lat = sum(p[1] for p in coords) / len(coords)
center_lon = sum(p[0] for p in coords) / len(coords)

tiles_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

# Crear mapa sin tiles para control personalizado
m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles=None)

# Agregar capa base satelital como tile layer con nombre
folium.TileLayer(
    tiles=tiles_url,
    attr="Esri World Imagery",
    name="Satélite"
).add_to(m)


# Cargar capa de límites administrativos desde tu geojson
with open("World_Administrative.geojson", "r", encoding="utf-8") as f:
    admin_geojson = json.load(f)

folium.GeoJson(
    admin_geojson,
    name="Límites administrativos",
    style_function=lambda x: {
        "color": "#888888",
        "weight": 1,
        "fillOpacity": 0  # solo bordes
    }
).add_to(m)

# Capa de cuenca
folium.GeoJson(
    cuenca_geojson,
    name="Cuenca Polochic",
    style_function=lambda x: {
        "fillColor": "#0099cc",
        "color": "#003366",
        "weight": 2,
        "fillOpacity": 0.3
    }
).add_to(m)

# Cargar puntos de interés (hidroeléctricas u otras)
with open("AOI_Polochic.geojson", "r", encoding="utf-8") as f:
    puntos_geojson = json.load(f)

# Crear grupo de capa para los puntos de interés
hidro_group = folium.FeatureGroup(name="Hidroeléctricas")

# Agregar los puntos al grupo
for feature in puntos_geojson["features"]:
    coords = feature["geometry"]["coordinates"]
    props = feature["properties"]
    nombre = props.get("Name", "Punto de interés")
    
    folium.Marker(
        location=[coords[1], coords[0]],
        popup=nombre,
        icon=folium.Icon(color="green", icon="bolt", prefix="fa")
    ).add_to(hidro_group)

# Agregar grupo al mapa
hidro_group.add_to(m)


# Control de capas (al final)
folium.LayerControl().add_to(m)

# Mostrar mapa
st_data = st_folium(m, width=1200, height=500)

# Cargar datos
@st.cache_data
def cargar_datos():
    #df = pd.read_csv("Precipitacion_Mensual_Polochic.csv")
    df = pd.read_csv("C:\Polochic_Basin\Precipitacion_Subcuencas_Polochic.csv")
    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)
    df["precip_m"] = df["precip_mm"] / 1000  # mm a mst
    df["area_km2"] = df["HECTARES"] * 0.01
    df["area_m2"] = df["HECTARES"] * 1e4

    #df["area_m2"] = df["area_km2"] * 1e6
    return df

df = cargar_datos()

# Sidebar
subcuencas = df["SUBCUENCA"].unique().tolist()
subcuenca_seleccionada = st.sidebar.selectbox("Seleccionar subcuenca", subcuencas)

coef_c = st.sidebar.slider("Coeficiente de escorrentía (C)", 0.05, 1.0, 0.3, step=0.05)

meses_pronostico = st.sidebar.slider("Meses a pronosticar", 1, 12, 3)


# Filtrar por subcuenca
df_sub = df[df["SUBCUENCA"] == subcuenca_seleccionada].copy()
#df_sub["Q_m3_mes"] = coef_c * df_sub["precip_m"] * df_sub["area_m2"]
df_sub["precip_m"] = df_sub["precip_mm"] / 1000
df_sub["area_m2"] = df_sub["HECTARES"] * 1e4
df_sub["Q_m3_mes"] = coef_c * df_sub["precip_m"] * df_sub["area_m2"]
df_sub["fecha"] = pd.to_datetime(df_sub[["year", "month"]].assign(day=1))

# Visualización
st.subheader(f"📈 Caudal estimado en: {subcuenca_seleccionada}")
fig = px.line(df_sub, x="fecha", y="Q_m3_mes", title="Caudal mensual estimado (m³/mes)")
st.plotly_chart(fig, use_container_width=True)

# Mostrar tabla de datos
with st.expander("📄 Ver datos crudos"):
    st.dataframe(df_sub[["fecha", "precip_mm", "area_km2", "Q_m3_mes"]])

# --- Generar y mostrar pronóstico con función externa ---
modelo, forecast, fig = generar_pronostico(df_sub, meses_pronostico)
st.plotly_chart(fig, use_container_width=True)


# -- RESUMEN EJECUTIVO --
# Mostrar resumen ejecutivo en tarjetas
ultimo_mes = forecast["ds"].iloc[-meses_pronostico]
caudal_estimado = forecast["yhat"].iloc[-meses_pronostico]
promedio_historico = df_sub["Q_m3_mes"].mean()
delta_pct = ((caudal_estimado - promedio_historico) / promedio_historico) * 100

col1, col2, col3 = st.columns(3)
col1.metric("🗓️ Próximo mes", ultimo_mes.strftime("%B %Y"))
col2.metric("📊 Caudal estimado", f"{int(round(caudal_estimado)):,} m³".replace(",", " "))
col3.metric("📈 Comparado al promedio histórico", f"{delta_pct:+.1f}%", delta=f"{delta_pct:+.1f}%")

# Tabla de pronóstico
st.markdown("#### Pronóstico próximo:")
tabla = forecast[["ds", "yhat"]].tail(meses_pronostico).copy()
tabla["yhat"] = tabla["yhat"].apply(lambda x: f"{int(round(x)):,}".replace(",", " "))
tabla.rename(columns={"ds": "Fecha", "yhat": "Caudal pronosticado (m³/mes)"}, inplace=True)
st.dataframe(tabla)


if st.button("📤 Exportar reporte PDF"):
    nombre_pdf = exportar_pdf(subcuenca_seleccionada, coef_c, forecast)
    st.success(f"PDF generado: {nombre_pdf}")
    with open(nombre_pdf, "rb") as f:
        st.download_button("Descargar PDF", f, file_name=nombre_pdf)
