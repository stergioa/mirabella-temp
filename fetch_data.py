import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pandas as pd
import os
import pytz
import time
from dotenv import load_dotenv

# load environment variables
load_dotenv()
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# constants
LATITUDE = 35.2146968
LONGITUDE = 25.7094369
ATHENS_TZ = pytz.timezone('Europe/Athens')
CSV_FILE = 'temperature_data.csv'
WEATHER_CURRENT_URL = 'https://api.openweathermap.org/data/2.5/weather'
WEATHER_FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast'

# configure retry strategy for requests
retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
http = requests.Session()
http.mount("http://", HTTPAdapter(max_retries=retry_strategy))


# fetch temperature data from specified URLs - based on boards with thermometers
def fetch_temperatures():
    urls = {
        'Board 1': 'http://mirabella.gotdns.com:81/status.xml',
        'Board 2': 'http://mirabella.gotdns.com:83/status.xml',
        'Board 3': 'http://mirabella.gotdns.com:82/status.xml'
    }
    temperatures = {}

    try:
        for board, url in urls.items():
            response = http.get(url, timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.content)

            if board == 'Board 1':
                temperatures['temp_1'] = float(root.find('Temperature1').text.replace('°C', ''))
                temperatures['temp_2'] = float(root.find('Temperature2').text.replace('°C', ''))
            elif board == 'Board 2':
                temperatures['temp_3'] = float(root.find('Temperature1').text.replace('°C', ''))
                temperatures['temp_4'] = float(root.find('Temperature2').text.replace('°C', ''))
            elif board == 'Board 3':
                temperatures['temp_5'] = float(root.find('Temperature2').text.replace('°C', ''))
                temperatures['temp_6'] = float(root.find('Temperature1').text.replace('°C', ''))

        return temperatures
    except requests.exceptions.RequestException as e:
        print(f"Error fetching temperature data: {e}")
        return None


# fetch current weather data from openweathermap API
def get_weather_data():
    params = {
        'lat': LATITUDE,
        'lon': LONGITUDE,
        'appid': WEATHER_API_KEY,
        'units': 'metric'
    }
    try:
        response = http.get(WEATHER_CURRENT_URL, params=params)
        response.raise_for_status()
        weather_data = response.json()

        current_temp = weather_data['main']['temp']
        current_humidity = weather_data['main']['humidity']
        current_cloudiness = weather_data['clouds']['all']
        sunrise_utc = datetime.fromtimestamp(weather_data['sys']['sunrise'], pytz.utc)
        sunset_utc = datetime.fromtimestamp(weather_data['sys']['sunset'], pytz.utc)

        return {
            'current_temp': current_temp,
            'current_humidity': current_humidity,
            'current_cloudiness': current_cloudiness,
            'current_sunrise': sunrise_utc.astimezone(ATHENS_TZ).isoformat(),
            'current_sunset': sunset_utc.astimezone(ATHENS_TZ).isoformat()
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None


# fetch average cloudiness from openweathermap during daylight hours for the next 3 days
def fetch_average_cloudiness():
    params = {
        'lat': LATITUDE,
        'lon': LONGITUDE,
        'appid': WEATHER_API_KEY,
        'units': 'metric'
    }
    try:
        # Requesting forecast data
        response = http.get(WEATHER_FORECAST_URL, params=params)
        response.raise_for_status()
        forecast_data = response.json()

        now = datetime.now(pytz.utc).astimezone(ATHENS_TZ)
        three_days_later = now + timedelta(days=3)
        cloudiness_values = []

        # Retrieving city-wide sunrise and sunset timestamps for the location
        city_sunrise = datetime.fromtimestamp(forecast_data['city']['sunrise'], pytz.utc).astimezone(ATHENS_TZ)
        city_sunset = datetime.fromtimestamp(forecast_data['city']['sunset'], pytz.utc).astimezone(ATHENS_TZ)

        # Loop through forecast data entries
        for entry in forecast_data['list']:
            forecast_time = datetime.fromtimestamp(entry['dt'], pytz.utc).astimezone(ATHENS_TZ)

            # Include forecast only if within the next 3 days and during daylight hours
            if now <= forecast_time <= three_days_later:
                if city_sunrise.time() <= forecast_time.time() <= city_sunset.time():
                    cloudiness_values.append(entry['clouds']['all'])

        # Return average cloudiness or None if no values were found
        return {'three_day_forecast_avg': sum(cloudiness_values) / len(cloudiness_values)} if cloudiness_values else None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching cloudiness forecast data: {e}")
        return None


# append new data to CSV file
def save_to_csv(data):
    timestamp = datetime.now(pytz.utc).astimezone(ATHENS_TZ).isoformat()
    data['timestamp'] = timestamp

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=['timestamp', 'temp_1', 'temp_2', 'temp_3', 'temp_4', 'temp_5', 'temp_6',
                                   'current_cloudiness', 'current_temp', 'current_humidity',
                                   'current_sunrise', 'current_sunset', 'three_day_forecast_avg'])

    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)


# main loop to fetch and save data every 2 minutes
def main():
    while True:
        temps = fetch_temperatures()
        if temps:
            weather_data = get_weather_data()
            forecast = fetch_average_cloudiness()
            if weather_data and forecast:
                combined_data = {**temps, **weather_data, **forecast}
                save_to_csv(combined_data)
        time.sleep(300)


if __name__ == "__main__":
    main()
