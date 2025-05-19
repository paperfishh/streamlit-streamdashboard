import streamlit as st
import pandas as pd
from config.pg_config import get_pg_engine
from config.redis_config import get_redis_connection

st.title("📟 IoT Monitoring Dashboard")

# PostgreSQL: show latest 100 records
pg_engine = get_pg_engine()
df = pd.read_sql("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 100", pg_engine)
st.subheader("📊 Latest Sensor Readings (from PostgreSQL)")
st.dataframe(df)

# Redis: show last real-time data
redis_conn = get_redis_connection()
latest = redis_conn.xrevrange("iot_stream", count=1)
if latest:
    data = latest[0][1]
    st.subheader("📡 Real-time Sensor Data (from Redis)")
    st.write(data)
