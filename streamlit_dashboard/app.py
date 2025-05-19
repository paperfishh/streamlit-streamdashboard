import streamlit as st
import pandas as pd
from config.redis_config import get_redis_connection
from datetime import datetime
import plotly.express as px
import plotly.graph_objs as go

st.set_page_config(page_title="📟 IoT Monitoring Dashboard", layout="wide")
st.title("📟 IoT Monitoring Dashboard")

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

# Initialize dropdown state
if "metric_option" not in st.session_state:
    st.session_state.metric_option = "Soil Moisture"

df = fetch_redis_data()

if df.empty:
    st.warning("No data found in Redis stream 'iot_stream'.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("🌡️ Temperature (°C)", f"{df['temperature'].iloc[-1]:.2f}")
col2.metric("💧 Humidity (%)", f"{df['humidity'].iloc[-1]:.2f}")
col3.metric("☀️ Light Intensity", f"{df['light_intensity'].iloc[-1]:.0f} lux")

col4, col5, col6 = st.columns(3)
col4.metric("🌧️ Rainfall (mm)", f"{df['rainfall'].iloc[-1]:.2f}")
col5.metric("🪨 Soil Moisture (%)", f"{df['soil_moisture'].iloc[-1]:.2f}")
col6.metric("🫁 CO₂ (ppm)", f"{df['co2'].iloc[-1]:.0f}")

st.markdown("---")

# === Prediksi Kebutuhan Irigasi berdasarkan data terbaru ===
latest_soil_moisture = df['soil_moisture'].iloc[-1]
latest_rainfall = df['rainfall'].iloc[-1]
prediction = predict_irrigation_need(latest_soil_moisture, latest_rainfall)

st.subheader("💧 Prediksi Kebutuhan Irigasi")
st.info(f"Soil Moisture: {latest_soil_moisture:.2f}%, Rainfall: {latest_rainfall:.2f} mm")
st.markdown(f"**Status:** {prediction}")

st.markdown("---")

st.subheader("📈 Temperature & Humidity Over Time")
chart_data = df.set_index('timestamp')[['temperature', 'humidity']]
fig1 = px.line(chart_data, x=chart_data.index, y=['temperature', 'humidity'],
               labels={"value": "Value", "timestamp": "Waktu", "variable": "Metric"},
               title="Temperature & Humidity")
fig1.update_traces(mode="lines+markers")
fig1.update_layout(template="plotly_white")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

metrics_info = {
    "Soil Moisture (%)": ("soil_moisture", "green"),
    "Rainfall (mm)": ("rainfall", "blue"),
    "Light Intensity (lux)": ("light_intensity", "orange"),
    "CO2 (ppm)": ("co2", "red"),
}

st.subheader("🌱 Additional Environmental Metrics")

cols = st.columns(2)

for i, (label, (col_name, color)) in enumerate(metrics_info.items()):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df[col_name], mode='lines+markers', line=dict(color=color)))
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=300,
        title=label,
        xaxis_title="Time",
        yaxis_title=label,
        template="plotly_white",
    )
    cols[i % 2].plotly_chart(fig, use_container_width=True)

st.markdown("---")

with st.expander("📋 Show Raw Data"):
    st.dataframe(
        df[['timestamp', 'sensor_id', 'temperature', 'humidity',
            'soil_moisture', 'rainfall', 'light_intensity', 'co2']]
        .sort_values(by='timestamp', ascending=False),
        use_container_width=True
    )
