import pandas as pd


def transform_weather(data):
    hourly = data["hourly"]

    df = pd.DataFrame(hourly)

    return df