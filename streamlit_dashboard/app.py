import streamlit as st
import pandas as pd
from config.redis_config import get_redis_connection
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objs as go
from streamlit_shadcn_ui import metric_card
import plotly.graph_objects as go

st.set_page_config(page_title="📟 IoT Monitoring Dashboard", layout="wide")

st.title("IoT Monitoring Dashboard")

# === FILTER TANGGAL DI BAGIAN ATAS ===
today = datetime.now().date()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Dari Tanggal", today - timedelta(days=7), key="start_date")
with col2:
    end_date = st.date_input("Sampai Tanggal", today, key="end_date")

redis_conn = get_redis_connection()

def fetch_redis_data(count=100):
    messages = redis_conn.xrevrange("iot_stream", count=count)
    data_list = []
    for message_id, data in reversed(messages):
        try:
            data_list.append({
                'id': message_id,
                'sensor_id': data.get('sensor_id'),
                'temperature': float(data.get('temperature')),
                'humidity': float(data.get('humidity')),
                'soil_moisture': float(data.get('soil_moisture', 0)),
                'rainfall': float(data.get('rainfall', 0)),
                'light_intensity': float(data.get('light_intensity', 0)),
                'co2': float(data.get('co2', 0)),
                'timestamp': datetime.fromtimestamp(float(data.get('timestamp')))
            })
        except Exception:
            continue
    return pd.DataFrame(data_list)

def predict_irrigation_need(soil_moisture, rainfall):
    if soil_moisture < 30 and rainfall < 2:
        return "🚨 Needs Irrigation"
    elif soil_moisture < 40:
        return "⚠️ Monitor Soil"
    else:
        return "✅ Adequate"

# Ambil data & filter berdasarkan tanggal
df = fetch_redis_data()
df = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]

if df.empty or len(df) < 2:
    st.warning("Tidak ada data yang ditemukan dalam rentang tanggal yang dipilih.")
    st.stop()

# Metrics comparison
latest = df.iloc[-1]
previous = df.iloc[-2]

metrics = [
    ("🌡️ Temperature (°C)", "temperature", "temperature_card"),
    ("💧 Humidity (%)", "humidity", "humidity_card"),
    ("☀️ Light Intensity (lux)", "light_intensity", "light_intensity_card"),
    ("🌧️ Rainfall (mm)", "rainfall", "rainfall_card"),
    ("🪨 Soil Moisture (%)", "soil_moisture", "soil_moisture_card"),
    ("🫁 CO₂ (ppm)", "co2", "co2_card")
]

st.subheader("Environmental Metrics")
cols = st.columns(6)

for col, (label, col_name, key) in zip(cols, metrics):
    curr = latest[col_name]
    prev = previous[col_name]
    arrow = "↑" if curr > prev else "↓" if curr < prev else "→"
    desc = f"{arrow} Prev: {prev:.2f}"
    with col:
        metric_card(
            title=label,
            content=f"{curr:.2f}",
            description=desc,
            key=key
        )

st.markdown("---")

# === Prediksi Kebutuhan Irigasi ===
st.subheader("Prediksi Kebutuhan Irigasi")

latest_soil_moisture = latest['soil_moisture']
latest_rainfall = latest['rainfall']
prediction = predict_irrigation_need(latest_soil_moisture, latest_rainfall)

col1, col2 = st.columns([1, 2])

with col1:
    st.info(f"Soil Moisture: {latest_soil_moisture:.2f}%, Rainfall: {latest_rainfall:.2f} mm")
    st.markdown(f"**Status:** {prediction}")

st.markdown("---")

# Chart suhu & kelembaban
st.subheader("Temperature & Humidity Over Time")
chart_data = df.set_index('timestamp')[['temperature', 'humidity']]
fig1 = px.line(chart_data, x=chart_data.index, y=['temperature', 'humidity'],
               labels={"value": "Value", "timestamp": "Waktu", "variable": "Metric"},
               title="Temperature & Humidity")
fig1.update_traces(mode="lines+markers")
fig1.update_layout(template="plotly_white")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# Chart tambahan
# Chart tambahan dengan warna pastel modern
pastel_colors = {
    "Soil Moisture (%)": ("soil_moisture", "#75D6DA"),       # pastel teal
    "Rainfall (mm)": ("rainfall", "#8AC9FF"),                # pastel blue
    "Light Intensity (lux)": ("light_intensity", "#FFC57E"), # pastel orange
    "CO2 (ppm)": ("co2", "#FF8787"),                         # pastel pink
}

st.subheader("Additional Environmental Metrics")
cols2 = st.columns(2)

for i, (label, (col_name, color)) in enumerate(pastel_colors.items()):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df[col_name],
        mode='lines+markers',
        line=dict(color=color, width=2),
        marker=dict(size=6)
    ))
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=300,
        title=label,
        xaxis_title="Time",
        yaxis_title=label,
        template="plotly_white",
    )
    cols2[i % 2].plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Tampilkan data mentah
with st.expander("📋 Show Raw Data"):
    st.dataframe(
        df[['timestamp', 'sensor_id', 'temperature', 'humidity',
            'soil_moisture', 'rainfall', 'light_intensity', 'co2']]
        .sort_values(by='timestamp', ascending=False),
        use_container_width=True
    )
