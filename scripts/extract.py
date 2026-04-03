import requests


def extract_weather():
    url = "https://open-meteo.com/en/docs?hourly=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,precipitation,rain,showers,snowfall,weather_code,pressure_msl,surface_pressure,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,snow_depth,evapotranspiration,et0_fao_evapotranspiration"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()