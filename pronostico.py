import pandas as pd
import plotly.graph_objects as go
from prophet import Prophet
from fpdf import FPDF
from datetime import datetime
import matplotlib.pyplot as plt

def generar_pronostico(df_sub, meses_pronostico):
    df_prophet = df_sub[["fecha", "Q_m3_mes"]].rename(columns={"fecha": "ds", "Q_m3_mes": "y"})
    modelo = Prophet()
    modelo.fit(df_prophet)

    futuro = modelo.make_future_dataframe(periods=meses_pronostico, freq="MS")
    pronostico = modelo.predict(futuro)

    ultimos_6m = df_sub[df_sub["fecha"] >= (df_sub["fecha"].max() - pd.DateOffset(months=6))]
    forecast_n = pronostico[pronostico["ds"] > df_sub["fecha"].max()].head(meses_pronostico)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ultimos_6m["fecha"], y=ultimos_6m["Q_m3_mes"],
                             mode="lines+markers", name="Histórico"))
    fig.add_trace(go.Scatter(x=forecast_n["ds"], y=forecast_n["yhat"],
                             mode="lines+markers", name="Pronóstico", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(
        x=list(forecast_n["ds"]) + list(forecast_n["ds"])[::-1],
        y=list(forecast_n["yhat_upper"]) + list(forecast_n["yhat_lower"])[::-1],
        fill="toself", fillcolor="rgba(0,100,80,0.2)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip", showlegend=True, name="Rango de confianza"
    ))

    fig.update_layout(title="Pronóstico de caudal (m³/mes)", xaxis_title="Fecha", yaxis_title="Caudal estimado")
    return modelo, forecast_n, fig

def exportar_pdf(subcuenca, coef_c, forecast_df, imagen_path="grafica_pronostico.png"):
    plt.figure()
    plt.plot(forecast_df["ds"], forecast_df["yhat"], label="Pronóstico")
    plt.fill_between(forecast_df["ds"], forecast_df["yhat_lower"], forecast_df["yhat_upper"], alpha=0.3)
    plt.title("Pronóstico de caudal")
    plt.xlabel("Fecha")
    plt.ylabel("m³/mes")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(imagen_path)
    plt.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Reporte de Pronóstico - Cuenca del Polochic", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Subcuenca: {subcuenca}", ln=True)
    pdf.cell(0, 10, f"Coeficiente de escorrentía: {coef_c:.2f}", ln=True)
    pdf.cell(0, 10, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Pronóstico:", ln=True)
    pdf.set_font("Arial", "", 11)

    for _, row in forecast_df.iterrows():
        incertidumbre = round(row['yhat_upper'] - row['yhat'])
        caudal_fmt = f"{int(round(row['yhat'])):,}".replace(",", " ")
        incertidumbre_fmt = f"{int(round(row['yhat_upper'] - row['yhat'])):,}".replace(",", " ")
        pdf.cell(0, 8, f"{row['ds'].date()}: {caudal_fmt} m³/mes (±{incertidumbre_fmt})", ln=True)



    pdf.ln(10)
    pdf.image(imagen_path, x=10, w=180)

    nombre_archivo = f"Pronostico_{subcuenca.replace(' ', '_')}.pdf"
    pdf.output(nombre_archivo)
    return nombre_archivo
