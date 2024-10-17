import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import plotly.graph_objs as go
import os
import time

# path to save the CSV file
CSV_FILE = 'temperature_data.csv'

# Automatically fetch new data every 2 minutes
def fetch_temperatures():
    urls = {
        'Board 1': 'http://mirabella.gotdns.com:81/status.xml',
        'Board 2': 'http://mirabella.gotdns.com:83/status.xml',
        'Board 3': 'http://mirabella.gotdns.com:82/status.xml'
    }

    temperatures = {}

    try:
        for board, url in urls.items():
            response = requests.get(url)
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
        st.error(f"Error fetching data: {e}")
        return None


# Append new temperature data to the CSV file
def save_to_csv(data):
    timestamp = datetime.now()
    data['timestamp'] = timestamp

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=['timestamp', 'temp_1', 'temp_2', 'temp_3', 'temp_4', 'temp_5', 'temp_6'])

    # Convert the new data to a DataFrame for concatenation
    new_row = pd.DataFrame([data])

    # Use pd.concat instead of append
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)


# Remove data older than a week (to save resources)
def clear_old_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        one_week_ago = datetime.now() - timedelta(days=7)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df[df['timestamp'] > one_week_ago]
        df.to_csv(CSV_FILE, index=False)


# Load temperature data from CSV for plotting
def load_data(time_range):
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Filter the data based on the selected time range
        if time_range == 'Display Temperatures for the past Week':
            return df[df['timestamp'] >= (datetime.now() - timedelta(days=7))]
        elif time_range == 'Display Temperatures for the past 3 Days':
            return df[df['timestamp'] >= (datetime.now() - timedelta(days=3))]
        elif time_range == 'Display Temperatures for the past Day':
            return df[df['timestamp'] >= (datetime.now() - timedelta(days=1))]
        else:
            return df
    else:
        return pd.DataFrame(columns=['timestamp', 'temp_1', 'temp_2', 'temp_3', 'temp_4', 'temp_5', 'temp_6'])


# Plot temperature data
def plot_temperatures(df):
    if not df.empty:
        # Define common layout properties for the figures
        common_layout = dict(
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
            font=dict(size=16),             # General font size
            title_font=dict(size=20),       # Title font size
            legend=dict(y=0.5, font=dict(size=14)),  # Center the legend vertically and increase font size
            xaxis=dict(title_font=dict(size=18)),  # X-axis title font size
            yaxis=dict(title_font=dict(size=18)),  # Y-axis title font size
            margin=dict(l=40, r=40, t=60, b=40),  # Set margins
            # Adding the border effect
            shapes=[dict(
                type='rect',
                xref='paper', yref='paper',
                x0=0, y0=0, x1=1, y1=1,
                line=dict(color='white', width=1),  # White border color and width
                fillcolor='rgba(0,0,0,0)',          # Transparent fill color
                layer='below'
            )]
        )

        # First plot: Rooms 11-12 & 13-14
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_1'], mode='lines', name='Rooms 11-12', line=dict(color='red')))
        fig1.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_2'], mode='lines', name='Rooms 13-14', line=dict(color='blue')))
        fig1.update_layout(
            title="Rooms 11-12 (Red) & 13-14 (Blue)",
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            title_x=0.25,  # Center the title
            **common_layout
        )

        # Second plot: Rooms 15-16 & 17-18
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_3'], mode='lines', name='Rooms 15-16', line=dict(color='red')))
        fig2.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_4'], mode='lines', name='Rooms 17-18', line=dict(color='blue')))
        fig2.update_layout(
            title="Rooms 15-16 (Red) & 17-18 (Blue)",
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            title_x=0.25,
            **common_layout
        )

        # Third plot: Rooms 21-23 & 24-28
        fig3 = go.Figure()
        fig3.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_5'], mode='lines', name='Rooms 21-23', line=dict(color='red')))
        fig3.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_6'], mode='lines', name='Rooms 24-28', line=dict(color='blue')))
        fig3.update_layout(
            title="Rooms 21-23 (Red) & 24-28 (Blue)",
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            title_x=0.25,
            **common_layout
        )

        # display plots
        st.plotly_chart(fig1)
        st.plotly_chart(fig2)
        st.plotly_chart(fig3)
    else:
        st.write("No data available.")



def main():
    st.title("Boiler Temperature Monitoring")
    _, c, _ = st.columns([2, 7, 3])
    with c:
        time_range = st.selectbox(
            "Non_empty",
            options=[
                'Display Temperatures for the past Week',
                'Display Temperatures for the past 3 Days',
                'Display Temperatures for the past Day',
            ],
            label_visibility='hidden'
        )
    st.write("")

    # Fetch and save new data every 2 minutes
    temps = fetch_temperatures()
    if temps:
        save_to_csv(temps)
        clear_old_data()

    # Load data for plotting
    df = load_data(time_range)
    plot_temperatures(df)

    # Refresh every 2 minutes
    time.sleep(120)
    st.rerun()  # This will rerun the script after the sleep time


if __name__ == "__main__":
    main()
