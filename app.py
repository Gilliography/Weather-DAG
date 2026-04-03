import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Weather Analytics Dashboard",
    layout="wide"
)

st.title("🌦️ Weather Analytics Dashboard")
st.markdown("Real-time weather insights powered by Airflow ETL pipeline")

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
DB_URI = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    engine = create_engine(DB_URI)
    df = pd.read_sql("SELECT * FROM weather_data", engine)
    
    # Convert time column
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
    
    return df


try:
    df = load_data()
except Exception as e:
    st.error("⚠️ Could not load data from database.")
    st.code(str(e))
    st.stop()

# -----------------------------
# CHECK DATA
# -----------------------------
if df.empty:
    st.warning("No data available. Please run your Airflow DAG.")
    st.stop()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔍 Filters")

# Ensure time exists
if "time" not in df.columns:
    st.error("❌ 'time' column missing in dataset")
    st.stop()

# Date range
min_date = df["time"].min().date()
max_date = df["time"].max().date()

start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)

# Metric selector
numeric_columns = df.select_dtypes(include="number").columns.tolist()

if not numeric_columns:
    st.error("No numeric columns found in dataset")
    st.stop()

metric = st.sidebar.selectbox("📊 Select Metric", numeric_columns)

# -----------------------------
# FILTER DATA
# -----------------------------
filtered_df = df[
    (df["time"] >= pd.to_datetime(start_date)) &
    (df["time"] <= pd.to_datetime(end_date))
]

if filtered_df.empty:
    st.warning("No data for selected date range")
    st.stop()

# -----------------------------
# KPI SECTION
# -----------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric(
    label="Average",
    value=f"{filtered_df[metric].mean():.2f}"
)

col2.metric(
    label="Maximum",
    value=f"{filtered_df[metric].max():.2f}"
)

col3.metric(
    label="Minimum",
    value=f"{filtered_df[metric].min():.2f}"
)

# -----------------------------
# MAIN CHART
# -----------------------------
st.subheader(f"📈 {metric} Over Time")

st.line_chart(
    filtered_df.set_index("time")[metric]
)

# -----------------------------
# COMPARISON CHART
# -----------------------------
st.subheader("🔄 Temperature Comparison")

if "temperature_2m" in filtered_df.columns and "apparent_temperature" in filtered_df.columns:
    st.line_chart(
        filtered_df.set_index("time")[[
            "temperature_2m",
            "apparent_temperature"
        ]]
    )
else:
    st.info("Temperature comparison not available")

# -----------------------------
# MULTI-METRIC VIEW
# -----------------------------
st.subheader("📊 Multi-Metric Overview")

selected_metrics = st.multiselect(
    "Select multiple metrics to compare",
    numeric_columns,
    default=numeric_columns[:3]
)

if selected_metrics:
    st.line_chart(
        filtered_df.set_index("time")[selected_metrics]
    )

# -----------------------------
# RAW DATA TABLE
# -----------------------------
st.subheader("📄 Raw Data")

st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# REFRESH BUTTON
# -----------------------------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()