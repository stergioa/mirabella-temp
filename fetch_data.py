import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pandas as pd
import os
import pytz
import time

# path to save the CSV file
CSV_FILE = 'temperature_data.csv'

# Get timezone of Athens
ATHENS_TZ = pytz.timezone('Europe/Athens')

# Retry strategy for failed requests
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)


# Fetch temperature data from URLs
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

            # Parsing XML response
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
        print(f"Error fetching data: {e}")
        return None


# Append new temperature data to the CSV file
def save_to_csv(data):
    timestamp = datetime.now(pytz.utc).astimezone(ATHENS_TZ)
    data['timestamp'] = timestamp.isoformat()

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=['timestamp', 'temp_1', 'temp_2', 'temp_3', 'temp_4', 'temp_5', 'temp_6'])

    # Convert the new data to a DataFrame for concatenation
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)


# Remove data older than a week
def clear_old_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        one_week_ago = datetime.now(ATHENS_TZ) - timedelta(days=7)
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, format='ISO8601')
        df = df[df['timestamp'] > one_week_ago]
        df.to_csv(CSV_FILE, index=False)


# Main loop to fetch and save data every 2 minutes
def main():
    while True:
        temps = fetch_temperatures()
        if temps:
            save_to_csv(temps)
            clear_old_data()
        time.sleep(120)  # Wait for 2 minutes before fetching again


if __name__ == "__main__":
    main()
