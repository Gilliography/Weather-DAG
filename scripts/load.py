from sqlalchemy import create_engine


def load_weather(df):
    engine = create_engine(
        "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
    )
    df.to_sql("weather_data", engine, if_exists="replace", index=False)