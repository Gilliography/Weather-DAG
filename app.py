"""Weather Analytics Dashboard.

Run:
    pip install -r requirements.txt
    streamlit run streamlit_app.py

Set DATABASE_URL to your PostgreSQL connection string if the default Docker
connection below is not appropriate for your environment.
"""

import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

st.set_page_config(page_title="Weather Analytics Dashboard", page_icon="🌦️", layout="wide")
st.title("🌦️ Weather Analytics Dashboard")
st.caption("Explore historical weather observations stored in PostgreSQL.")

DEFAULT_DATABASE_URL = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

PREFERRED_METRICS = [
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
]


@st.cache_data(ttl=300, show_spinner="Loading weather data from PostgreSQL...")
def load_weather_data(database_url: str) -> pd.DataFrame:
    """Load weather data and normalize its timestamp column."""
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM weather_data"))
            rows = result.fetchall()
            columns = list(result.keys())
        data = pd.DataFrame(rows, columns=columns)
    finally:
        engine.dispose()

    if data.empty:
        return data
    if "time" not in data.columns:
        raise ValueError("The weather_data table must contain a 'time' column.")
    data["time"] = pd.to_datetime(data["time"], errors="coerce")
    data = data.dropna(subset=["time"]).sort_values("time").reset_index(drop=True)
    return data


with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    refresh = st.button("🔄 Refresh data", use_container_width=True)

if refresh:
    load_weather_data.clear()

try:
    df = load_weather_data(DATABASE_URL)
except (SQLAlchemyError, ValueError, OSError) as exc:
    st.error("Could not load weather data from PostgreSQL.")
    st.code(str(exc))
    st.info(
        "Check DATABASE_URL, confirm PostgreSQL is reachable, and ensure the "
        "weather_data table exists and includes a time column."
    )
    st.stop()

if df.empty:
    st.warning("The weather_data table contains no valid weather observations.")
    st.stop()

numeric_columns = df.select_dtypes(include="number").columns.tolist()
weather_metrics = [column for column in PREFERRED_METRICS if column in numeric_columns]
if not weather_metrics:
    weather_metrics = [
        column for column in numeric_columns
        if column.lower() not in {"id", "weather_id", "record_id"}
    ]
if not weather_metrics:
    st.error("No numeric weather metrics were found in the weather_data table.")
    st.stop()

min_date = df["time"].min().date()
max_date = df["time"].max().date()

with st.sidebar:
    start_date = st.date_input(
        "📅 Start date", value=min_date, min_value=min_date, max_value=max_date
    )
    end_date = st.date_input(
        "📅 End date", value=max_date, min_value=min_date, max_value=max_date
    )
    metric = st.selectbox("📊 Select metric", weather_metrics)

if start_date > end_date:
    st.error("Start date must be on or before end date.")
    st.stop()

# Exclusive upper bound includes all observations throughout the selected end date.
start_datetime = pd.Timestamp(start_date)
end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1)
filtered_df = df.loc[
    (df["time"] >= start_datetime) & (df["time"] < end_datetime)
].copy()

if filtered_df.empty:
    st.warning("No observations were found for the selected date range.")
    st.stop()

metric_values = pd.to_numeric(filtered_df[metric], errors="coerce").dropna()
if metric_values.empty:
    st.warning(f"The selected metric '{metric}' has no numeric values in this date range.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Observations", f"{len(filtered_df):,}")
col2.metric(f"Average {metric}", f"{metric_values.mean():.2f}")
col3.metric(f"Maximum {metric}", f"{metric_values.max():.2f}")
col4.metric(f"Minimum {metric}", f"{metric_values.min():.2f}")

st.divider()
st.subheader(f"📈 {metric.replace('_', ' ').title()} over time")

time_series = filtered_df[["time", metric]].copy()
time_series[metric] = pd.to_numeric(time_series[metric], errors="coerce")
time_series = time_series.dropna(subset=[metric]).sort_values("time")
if not time_series.empty:
    fig = px.line(
        time_series,
        x="time",
        y=metric,
        markers=True,
        labels={"time": "Time", metric: metric.replace("_", " ").title()},
        title=f"{metric.replace('_', ' ').title()} by observation time",
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No valid values are available to plot for this metric.")

comparison_metrics = [
    name for name in ("temperature_2m", "apparent_temperature")
    if name in filtered_df.columns
]
if comparison_metrics:
    st.subheader("🌡️ Temperature comparison")
    temperature_df = filtered_df[["time", *comparison_metrics]].melt(
        id_vars="time", value_vars=comparison_metrics,
        var_name="Metric", value_name="Temperature"
    )
    temperature_df["Temperature"] = pd.to_numeric(
        temperature_df["Temperature"], errors="coerce"
    )
    temperature_df = temperature_df.dropna(subset=["Temperature"])
    if not temperature_df.empty:
        temperature_df["Metric"] = temperature_df["Metric"].str.replace(
            "_", " ", regex=False
        ).str.title()
        temperature_fig = px.line(
            temperature_df, x="time", y="Temperature", color="Metric",
            labels={"time": "Time", "Temperature": "Temperature"}
        )
        temperature_fig.update_layout(hovermode="x unified")
        st.plotly_chart(temperature_fig, use_container_width=True)
    else:
        st.info("No temperature values are available for comparison.")

available_multi_metrics = [
    column for column in weather_metrics if filtered_df[column].notna().any()
]
if len(available_multi_metrics) > 1:
    st.subheader("📊 Compare weather metrics")
    selected_metrics = st.multiselect(
        "Choose metrics to compare",
        options=available_multi_metrics,
        default=available_multi_metrics[: min(3, len(available_multi_metrics))],
    )
    if selected_metrics:
        multi_df = filtered_df[["time", *selected_metrics]].melt(
            id_vars="time", value_vars=selected_metrics,
            var_name="Metric", value_name="Value"
        )
        multi_df["Value"] = pd.to_numeric(multi_df["Value"], errors="coerce")
        multi_df = multi_df.dropna(subset=["Value"])
        multi_df["Metric"] = multi_df["Metric"].str.replace(
            "_", " ", regex=False
        ).str.title()
        multi_fig = px.line(
            multi_df, x="time", y="Value", color="Metric",
            labels={"time": "Time", "Value": "Value"}
        )
        multi_fig.update_layout(hovermode="x unified")
        st.plotly_chart(multi_fig, use_container_width=True)

st.subheader("🗃️ Raw weather data")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
st.caption(
    f"Showing {len(filtered_df):,} observations from "
    f"{start_date.isoformat()} through {end_date.isoformat()}."
)
