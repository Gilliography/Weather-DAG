import json
import pandas as pd

def transform_weather(input_path, output_path):
    """Transform raw JSON into CSV with first 24 hours of weather data."""
    with open(input_path, "r") as f:
        data = json.load(f)

    times = data["hourly"]["time"]
    temps = data["hourly"]["temperature_2m"]

    df = pd.DataFrame({
        "time": times,
        "temperature": temps
    })

    df["time"] = pd.to_datetime(df["time"])

    # Only first 24 hours
    df = df.head(24)

    df.to_csv(output_path, index=False)
    return output_path