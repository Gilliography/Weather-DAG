from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from scripts.extract import extract_weather
from scripts.transform import transform_weather
from scripts.load import load_weather

API_URL = "https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&hourly=temperature_2m"

RAW_PATH = "/tmp/weather_raw.json"
PROCESSED_PATH = "/tmp/weather_processed.csv"

def extract():
    return extract_weather(API_URL, RAW_PATH)


def transform_task_func(ti):
    input_path = ti.xcom_pull(task_ids='extract_task')
    return transform_weather(input_path, PROCESSED_PATH)


def load_task_func(ti):
    input_path = ti.xcom_pull(task_ids='transform_task')
    return load_weather(input_path)

with DAG(
    dag_id="modular_weather_etl",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    extract_task = PythonOperator(
        task_id= 'extract_task',
        python_callable=extract_task_func
    )

    transform_task = PythonOperator(
        task_id= 'transform_task',
        python_callable=transform_task_func
    )

    load_task = PythonOperator(
        task_id= 'load_task',
        python_callable=load_task_func
    )

    extract_task >> transform_task >> load_task