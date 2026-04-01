import requests
import json


def extract_weather(api_url, output_path):
    response = requests.get(api_url)
    response.raise_for_status()

    data = response.json()

    with open(output_path, 'w') as f:
        json.dump(data, f)

    
    return output_path