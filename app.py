import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="Weather Dashboard", layout="wide")

st.title("🌦️ Weather Dashboard")

@st.cache_data
def load_data():
    engine = create_engine(
        "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
    )
    df = pd.read_sql("SELECT * FROM weather_data", engine)
    return df


try:
    df = load_data()
except Exception:
    st.error("No data found. Please run the Airflow DAG first.")
    st.stop()

# Convert time column
df["time"] = pd.to_datetime(df["time"])

# Metrics
col1, col2, col3 = st.columns(3)

col1.metric("Avg Temp", f"{df['temperature'].mean():.2f} °C")
col2.metric("Max Temp", f"{df['temperature'].max():.2f} °C")
col3.metric("Min Temp", f"{df['temperature'].min():.2f} °C")

# Chart
st.subheader("Temperature Over Time")
st.line_chart(df.set_index("time")["temperature"])

# Raw data
st.subheader("Raw Data")
st.dataframe(df)

# Refresh button
if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()