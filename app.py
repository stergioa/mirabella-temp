import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objs as go
import pytz
import os

# path to the CSV file
CSV_FILE = 'temperature_data.csv'

# Get timezone of Athens
ATHENS_TZ = pytz.timezone('Europe/Athens')


def load_data():
    # Always load the full dataset (no filtering yet)
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, format='ISO8601')
        df['timestamp'] = df['timestamp'].dt.tz_convert(ATHENS_TZ)  # Convert UTC to Athens time
        return df
    else:
        return pd.DataFrame(columns=['timestamp', 'temp_1', 'temp_2', 'temp_3', 'temp_4', 'temp_5', 'temp_6'])


# Filter data based on the selected time range
def filter_data(df, time_range):
    now = datetime.now(ATHENS_TZ)

    if time_range == 'Past Week':
        return df[df['timestamp'] >= (now - timedelta(days=7))]
    elif time_range == 'Past 3 Days':
        return df[df['timestamp'] >= (now - timedelta(days=3))]
    elif time_range == 'Past Day':
        return df[df['timestamp'] >= now.replace(hour=0, minute=0, second=0, microsecond=0)]  # From midnight
    else:
        return df

# Plot temperature data with dynamic width
def plot_temperatures(df):
    if not df.empty:
        # Define layout properties with centering for legends
        common_layout = dict(
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
            font=dict(size=12),             # Responsive font size
            showlegend=True,                # Enable legends for each plot
            legend=dict(
                orientation="h",            # Horizontal legend
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(title_font=dict(size=14), automargin=True),  # X-axis title with auto margins
            yaxis=dict(title_font=dict(size=14), automargin=True),  # Y-axis title with auto margins
            margin=dict(l=20, r=20, t=40, b=40),  # Tighter margins
        )

        # First plot: Rooms 11-12 (Red) & 13-14 (Blue)
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_1'], mode='lines', name='Rooms 11-12', line=dict(color='red')))
        fig1.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_2'], mode='lines', name='Rooms 13-14', line=dict(color='blue')))
        fig1.update_layout(
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            **common_layout  # No 'title' specified
        )

        # Second plot: Rooms 15-16 (Red) & 17-18 (Blue)
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_3'], mode='lines', name='Rooms 15-16', line=dict(color='red')))
        fig2.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_4'], mode='lines', name='Rooms 17-18', line=dict(color='blue')))
        fig2.update_layout(
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            **common_layout  # No 'title' specified
        )

        # Third plot: Rooms 21-23 (Red) & 24-28 (Blue)
        fig3 = go.Figure()
        fig3.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_5'], mode='lines', name='Rooms 21-23', line=dict(color='red')))
        fig3.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_6'], mode='lines', name='Rooms 24-28', line=dict(color='blue')))
        fig3.update_layout(
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            **common_layout  # No 'title' specified
        )

        # Plotly chart configuration to hide toolbar and disable zoom on mobile
        config = {
            'displayModeBar': False,  # Disable the toolbar
            'scrollZoom': False,      # Disable zoom on scroll or pinch on mobile
            'staticPlot': False,       # Completely disable all interactions
            'responsive': True        # Make charts responsive to screen size
        }

        # Display the three plots with legends instead of titles
        with st.expander("Rooms 11-12 & 13-14"):
            st.plotly_chart(fig1, use_container_width=True, config=config)
        with st.expander("Rooms 15-16 & 17-18"):
            st.plotly_chart(fig2, use_container_width=True, config=config)
        with st.expander("Rooms 21-23 & 24-28"):
            st.plotly_chart(fig3, use_container_width=True, config=config)
    else:
        st.write("No data available.")



def main():
    st.title("Boiler Temperature Monitoring")

    # Always load the full dataset first
    df = load_data()

    # Select time range
    time_range = st.selectbox(
        "Select Time Range",
        ['Past Week', 'Past 3 Days', 'Past Day']
    )

    # Filter data based on the selected time range
    filtered_df = filter_data(df, time_range)

    # Plot the filtered data
    plot_temperatures(filtered_df)


if __name__ == "__main__":
    main()
