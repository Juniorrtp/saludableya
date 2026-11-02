"""
Dashboard interactivo - Caso SaludableYa
Muestra KPIs, filtros y gráficos del análisis exploratorio.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="SaludableYa - Dashboard",
    page_icon="🥗",
    layout="wide"
)

# ============================================================
# CARGA DE DATOS
# ============================================================
import os

@st.cache_data
def cargar_datos():
    # Construye la ruta absoluta al CSV usando la ubicación de app.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(base_dir, "dataset_unificado_saludableya.csv")
    df = pd.read_csv(ruta_csv, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df["Fecha_Pedido"] = pd.to_datetime(df["Fecha_Pedido"])
    return df

df = cargar_datos()

# ============================================================
# TÍTULO
# ============================================================
st.title("🥗 SaludableYa - Dashboard de Análisis Exploratorio")
st.markdown("**Caso:** Conectando datos y decisiones — el futuro de la startup saludable")
st.markdown("---")

# ============================================================
# FILTROS LATERALES
# ============================================================
st.sidebar.header("🔍 Filtros")

zonas = st.sidebar.multiselect(
    "Zona de entrega",
    options=sorted(df["Zona_Entrega"].unique()),
    default=sorted(df["Zona_Entrega"].unique())
)

categorias = st.sidebar.multiselect(
    "Categoría de producto",
    options=sorted(df["Categoria"].unique()),
    default=sorted(df["Categoria"].unique())
)

fecha_min = df["Fecha_Pedido"].min().date()
fecha_max = df["Fecha_Pedido"].max().date()
rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# Aplicar filtros
df_f = df[
    (df["Zona_Entrega"].isin(zonas)) &
    (df["Categoria"].isin(categorias))
]
if len(rango_fechas) == 2:
    df_f = df_f[
        (df_f["Fecha_Pedido"].dt.date >= rango_fechas[0]) &
        (df_f["Fecha_Pedido"].dt.date <= rango_fechas[1])
    ]

# ============================================================
# KPIs EN TARJETAS
# ============================================================
st.subheader("📌 Indicadores clave")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Ticket promedio", f"S/ {df_f['Total_Venta'].mean():.2f}")
col2.metric("Pedidos", f"{len(df_f):,}")
col3.metric("Calificación", f"{df_f['Calificacion_Estrellas'].mean():.2f} ★")
col4.metric("NPS promedio", f"{df_f['Puntaje_NPS'].mean():.1f}")
col5.metric("Tiempo promedio", f"{df_f['Tiempo_Entrega_Min'].mean():.1f} min")

st.markdown("---")

# ============================================================
# GRÁFICO 1: VENTAS POR ZONA
# ============================================================
st.subheader("💰 Ventas totales por zona")

ventas_zona = df_f.groupby("Zona_Entrega")["Total_Venta"].sum().sort_values(ascending=False).reset_index()
fig1 = px.bar(
    ventas_zona, x="Zona_Entrega", y="Total_Venta",
    text="Total_Venta", color="Zona_Entrega",
    labels={"Total_Venta": "Ventas (S/)", "Zona_Entrega": "Zona"}
)
fig1.update_traces(texttemplate="S/ %{text:,.2f}", textposition="outside")
fig1.update_layout(showlegend=False, height=400)
st.plotly_chart(fig1, use_container_width=True)

# ============================================================
# GRÁFICO 2: TIEMPO PROMEDIO POR ZONA (con SLA)
# ============================================================
st.subheader("⏱️ Tiempo promedio de entrega por zona (SLA = 45 min)")

tiempo_zona = df_f.groupby("Zona_Entrega")["Tiempo_Entrega_Min"].mean().sort_values(ascending=False).reset_index()
fig2 = px.bar(
    tiempo_zona, x="Zona_Entrega", y="Tiempo_Entrega_Min",
    text="Tiempo_Entrega_Min", color="Zona_Entrega",
    labels={"Tiempo_Entrega_Min": "Tiempo (min)", "Zona_Entrega": "Zona"}
)
fig2.add_hline(y=45, line_dash="dash", line_color="red",
               annotation_text="SLA 45 min", annotation_position="top right")
fig2.update_traces(texttemplate="%{text:.1f} min", textposition="outside")
fig2.update_layout(showlegend=False, height=400)
st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# GRÁFICO 3: TICKET PROMEDIO POR ZONA
# ============================================================
st.subheader("🎟️ Ticket promedio por zona")

ticket_zona = df_f.groupby("Zona_Entrega")["Total_Venta"].mean().sort_values(ascending=False).reset_index()
fig3 = px.bar(
    ticket_zona, x="Zona_Entrega", y="Total_Venta",
    text="Total_Venta", color="Zona_Entrega",
    labels={"Total_Venta": "Ticket promedio (S/)", "Zona_Entrega": "Zona"}
)
fig3.update_traces(texttemplate="S/ %{text:.2f}", textposition="outside")
fig3.update_layout(showlegend=False, height=400)
st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# GRÁFICO 4: CALIFICACIÓN PROMEDIO POR ZONA
# ============================================================
st.subheader("⭐ Calificación promedio por zona")

calif_zona = df_f.groupby("Zona_Entrega")["Calificacion_Estrellas"].mean().sort_values(ascending=False).reset_index()
fig4 = px.bar(
    calif_zona, x="Zona_Entrega", y="Calificacion_Estrellas",
    text="Calificacion_Estrellas", color="Zona_Entrega",
    labels={"Calificacion_Estrellas": "Calificación (★)", "Zona_Entrega": "Zona"}
)
fig4.update_traces(texttemplate="%{text:.2f} ★", textposition="outside")
fig4.update_yaxes(range=[0, 5.5])
fig4.update_layout(showlegend=False, height=400)
st.plotly_chart(fig4, use_container_width=True)

# ============================================================
# GRÁFICO 5: PEDIDOS POR DÍA DE LA SEMANA
# ============================================================
st.subheader("📅 Pedidos por día de la semana")

orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia = df_f["Dia_Semana"].value_counts().reindex(orden_dias).reset_index()
dia.columns = ["Día", "Pedidos"]
fig5 = px.bar(
    dia, x="Día", y="Pedidos", text="Pedidos", color="Día",
    labels={"Pedidos": "N° de pedidos"}
)
fig5.update_traces(texttemplate="%{text}", textposition="outside")
fig5.update_layout(showlegend=False, height=400)
st.plotly_chart(fig5, use_container_width=True)

# ============================================================
# GRÁFICO 6: PEDIDOS POR MES
# ============================================================
st.subheader("📈 Evolución mensual de pedidos")

mes = df_f.groupby("Mes").size().reset_index(name="Pedidos")
fig6 = px.line(
    mes, x="Mes", y="Pedidos", markers=True,
    labels={"Mes": "Mes", "Pedidos": "N° de pedidos"}
)
fig6.update_layout(height=400)
st.plotly_chart(fig6, use_container_width=True)

# ============================================================
# GRÁFICO 7: SENTIMIENTO DE COMENTARIOS
# ============================================================
st.subheader("💬 Distribución de sentimiento en comentarios")

sent = df_f["Sentimiento"].value_counts().reset_index()
sent.columns = ["Sentimiento", "Comentarios"]
fig7 = px.pie(
    sent, names="Sentimiento", values="Comentarios",
    color="Sentimiento", hole=0.4,
    color_discrete_map={"Positivo": "#2ecc71", "Neutro": "#f1c40f", "Negativo": "#e74c3c"}
)
fig7.update_layout(height=400)
st.plotly_chart(fig7, use_container_width=True)

# ============================================================
# GRÁFICO 8: TIPOS DE QUEJA
# ============================================================
st.subheader("⚠️ Tipos de queja más frecuentes")

quejas = df_f[df_f["Tipo_Queja"] != "Sin Queja"]["Tipo_Queja"].value_counts().reset_index()
quejas.columns = ["Tipo_Queja", "Casos"]
fig8 = px.bar(
    quejas, x="Casos", y="Tipo_Queja", orientation="h", text="Casos",
    color="Tipo_Queja", labels={"Casos": "N° de casos", "Tipo_Queja": "Tipo de queja"}
)
fig8.update_traces(texttemplate="%{text}", textposition="outside")
fig8.update_layout(showlegend=False, height=400)
st.plotly_chart(fig8, use_container_width=True)

# ============================================================
# TABLA DE DATOS FILTRABLES
# ============================================================
st.subheader("📋 Datos filtrados")
st.markdown(f"**{len(df_f):,}** pedidos cumplen los filtros seleccionados.")
st.dataframe(
    df_f[["ID_Pedido", "Fecha_Pedido", "Zona_Entrega", "Categoria",
          "Producto", "Total_Venta", "Tiempo_Entrega_Min",
          "Calificacion_Estrellas", "Sentimiento", "Tipo_Queja"]]
    .sort_values("Fecha_Pedido", ascending=False)
    .head(200),
    use_container_width=True
)

