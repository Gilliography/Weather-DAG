from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys

# Fix import path
sys.path.append('/opt/airflow')

from scripts.extract import extract_weather
from scripts.transform import transform_weather
from scripts.load import load_weather


def extract_task(**context):
    data = extract_weather()
    context['ti'].xcom_push(key='raw_data', value=data)


def transform_task(**context):
    raw_data = context['ti'].xcom_pull(key='raw_data')
    df = transform_weather(raw_data)
    context['ti'].xcom_push(key='df', value=df.to_json())


def load_task(**context):
    import pandas as pd
    df_json = context['ti'].xcom_pull(key='df')
    df = pd.read_json(df_json)
    load_weather(df)


default_args = {
    "start_date": datetime(2024, 1, 1),
    "retries": 2,
}

with DAG(
    dag_id="modular_weather_etl",
    schedule_interval="@hourly",
    default_args=default_args,
    catchup=False,
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_task
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_task
    )

    load = PythonOperator(
        task_id="load",
        python_callable=load_task
    )

    extract >> transform >> load