import pandas as pd

def load_weather(input_path):
    """Load the processed CSV (currently just prints it)."""
    df = pd.read_csv(input_path)
    print("Final Weather Data:")
    print(df.head())