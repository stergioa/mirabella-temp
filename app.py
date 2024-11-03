import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objs as go
import pytz
import os

CSV_FILE = 'temperature_data.csv'

# Athens timezone
ATHENS_TZ = pytz.timezone('Europe/Athens')


def load_data():
    # load full dataset
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Convert timestamp to datetime, handling ISO8601 automatically
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, format='ISO8601')
        df['timestamp'] = df['timestamp'].dt.tz_convert(ATHENS_TZ)
        return df
    return pd.DataFrame()


def filter_data(df, time_range):
    now = datetime.now(ATHENS_TZ)
    if time_range == 'Past Week':
        return df[df['timestamp'] >= now - timedelta(days=7)]
    elif time_range == 'Past 3 Days':
        return df[df['timestamp'] >= now - timedelta(days=3)]
    elif time_range == 'Past Day':
        return df[df['timestamp'] >= now.replace(hour=0, minute=0, second=0, microsecond=0)]
    return df


# function to check for temperature alarms
def check_temperature_alarms(df):
    alarms = []
    room_pairs = [
        ('temp_1', 'Rooms 11-12'),
        ('temp_2', 'Rooms 13-14'),
        ('temp_3', 'Rooms 15-16'),
        ('temp_4', 'Rooms 17-18'),
        ('temp_5', 'Rooms 21-23'),
        ('temp_6', 'Rooms 24-28')
    ]

    for temp_column, room_name in room_pairs:
        if df[temp_column].max() > 100:
            alarms.append(f"Alarm for {room_name}, temperature exceeds 100°C")
        if df[temp_column].min() < 20:
            alarms.append(f"Alarm for {room_name}, temperature falls below 20°C")

    return alarms


# plot temperature data with dynamic width and annotations
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
            height=300
        )

        # Get the latest temperatures for annotation
        latest_temps = {
            'Rooms 11-12': df['temp_1'].iloc[-1],
            'Rooms 13-14': df['temp_2'].iloc[-1],
            'Rooms 15-16': df['temp_3'].iloc[-1],
            'Rooms 17-18': df['temp_4'].iloc[-1],
            'Rooms 21-23': df['temp_5'].iloc[-1],
            'Rooms 24-28': df['temp_6'].iloc[-1]
        }

        # First plot: Rooms 11-12 (Red) & 13-14 (Blue)
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_1'], mode='lines', name='Rooms 11-12', line=dict(color='red')))
        fig1.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_2'], mode='lines', name='Rooms 13-14', line=dict(color='blue')))

        fig1.update_layout(
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            **common_layout
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
            **common_layout
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
            **common_layout
        )

        # Adjusted annotations to position them to the right of the plot
        fig1.add_annotation(
            x=df['timestamp'].iloc[-1] + pd.Timedelta(minutes=500),  # Shift to the right
            y=latest_temps['Rooms 11-12'],
            text=f"{latest_temps['Rooms 11-12']:.1f} °C", showarrow=False, font=dict(color='red')
        )
        fig1.add_annotation(
            x=df['timestamp'].iloc[-1] + pd.Timedelta(minutes=500),  # Shift to the right
            y=latest_temps['Rooms 13-14'],
            text=f"{latest_temps['Rooms 13-14']:.1f} °C", showarrow=False, font=dict(color='blue')
        )

        fig2.add_annotation(
            x=df['timestamp'].iloc[-1] + pd.Timedelta(minutes=500),  # Shift to the right
            y=latest_temps['Rooms 15-16'],
            text=f"{latest_temps['Rooms 15-16']:.1f} °C", showarrow=False, font=dict(color='red')
        )
        fig2.add_annotation(
            x=df['timestamp'].iloc[-1] + pd.Timedelta(minutes=500),  # Shift to the right
            y=latest_temps['Rooms 17-18'],
            text=f"{latest_temps['Rooms 17-18']:.1f} °C", showarrow=False, font=dict(color='blue')
        )

        fig3.add_annotation(
            x=df['timestamp'].iloc[-1] + pd.Timedelta(minutes=500),  # Shift to the right
            y=latest_temps['Rooms 21-23'],
            text=f"{latest_temps['Rooms 21-23']:.1f} °C", showarrow=False, font=dict(color='red')
        )
        fig3.add_annotation(
            x=df['timestamp'].iloc[-1] + pd.Timedelta(minutes=500),  # Shift to the right
            y=latest_temps['Rooms 24-28'],
            text=f"{latest_temps['Rooms 24-28']:.1f} °C", showarrow=False, font=dict(color='blue')
        )

        # Plotly chart configuration to hide toolbar and disable zoom on mobile
        config = {
            'displayModeBar': False,  # Disable the toolbar
            'scrollZoom': False,      # Disable zoom on scroll or pinch on mobile
            'staticPlot': False,      # Completely disable all interactions
            'responsive': True        # Make charts responsive to screen size
        }

        # create tabs to chose rooms
        tab1, tab2, tab3 = st.tabs(["Rooms 11-14", "15-18", "21-28"])
        with tab1:
            st.plotly_chart(fig1, use_container_width=True, config=config)
        with tab2:
            st.plotly_chart(fig2, use_container_width=True, config=config)
        with tab3:
            st.plotly_chart(fig3, use_container_width=True, config=config)

    else:
        st.write("No data available.")


# function that calculated remaining sunlight in a day
def calculate_sunlight_remaining(sunrise, sunset):
    now = datetime.now(ATHENS_TZ)
    if now < sunrise:
        return 100  # Full sunlight remaining
    elif now > sunset:
        return 0  # No sunlight remaining
    else:
        total_duration = (sunset - sunrise).total_seconds()
        elapsed_duration = (now - sunrise).total_seconds()
        return round(max(0, min(100, 100 * (total_duration - elapsed_duration) / total_duration)), 2)


def main():
    st.set_page_config(page_title="Boiler Temp")
    st.markdown(
        """
        <style>
        /* Hide the header completely */
        header.stAppHeader {
            display: none; /* Completely remove the header */
        }

        /* Remove padding and margin from the main container to eliminate space */
        .stApp {
            padding-top: -3rem !important;  /* Set top padding to zero */
            margin-top: -3rem !important;   /* Set top margin to zero */
        }

        /* Remove padding from the first element inside the main app */
        .stContainer {
            padding-top: 0rem;  /* Ensure no padding is applied */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("Boiler Temperature Monitoring")

    # load data
    df = load_data()

    # display weather data if available
    if not df.empty:
        latest_data = df.iloc[-1]  # most recent data
        current_temp = latest_data['current_temp']
        current_humidity = latest_data['current_humidity']
        current_cloudiness = latest_data['current_cloudiness']
        current_sunrise = pd.to_datetime(latest_data['current_sunrise'])
        current_sunset = pd.to_datetime(latest_data['current_sunset'])
        three_day_forecast_avg = latest_data.get('three_day_forecast_avg', 'N/A')
        sunlight_remaining = calculate_sunlight_remaining(current_sunrise, current_sunset)

        # Move metrics to the sidebar
        with st.sidebar:
            # Current Exterior Temperature
            st.markdown(
                "<h3 style='text-align: center; margin: 0;'>Current Exterior Temperature</h3>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<h3 style='text-align: center; margin: 0;'><span style='font-size: 30px; font-weight: bold;'>{current_temp:.1f} °C</span></h3>",
                unsafe_allow_html=True,
            )

            # Separator for Cloudiness metrics
            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

            # Cloud Coverage
            st.markdown("<h3 style='text-align: center; margin: 0;'>Cloud Coverage (%)</h3>", unsafe_allow_html=True)

            # Using columns for Cloudiness metrics
            col_sidebar_a, col_sidebar_b = st.columns(2)
            with col_sidebar_a:
                st.markdown(
                    f"<h4 style='text-align: center; margin: 0;'>Current<br><span style='font-size: 20px;'>{current_cloudiness:.1f} %</span></h4>",
                    unsafe_allow_html=True
                )
            with col_sidebar_b:
                st.markdown(
                    f"<h4 style='text-align: center; margin: 0;'>Next 3-Days<br><span style='font-size: 20px;'>{three_day_forecast_avg:.1f} %</span></h4>",
                    unsafe_allow_html=True
                )

            # Separator for Daylight Information
            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

            # Daylight Information
            st.markdown("<h3 style='text-align: center; margin: 0;'>Daylight Information</h3>", unsafe_allow_html=True)

            # Using columns for Sunrise and Sunset metrics
            col_sidebar_c, col_sidebar_d = st.columns(2)
            with col_sidebar_c:
                st.markdown(
                    f"<h4 style='text-align: center; margin: 0;'>Sunrise Time<br><span style='font-size: 20px;'>{current_sunrise.strftime('%H:%M')}</span></h4>",
                    unsafe_allow_html=True
                )
            with col_sidebar_d:
                st.markdown(
                    f"<h4 style='text-align: center; margin: 0;'>Sunset Time<br><span style='font-size: 20px;'>{current_sunset.strftime('%H:%M')}</span></h4>",
                    unsafe_allow_html=True
                )

            # Remaining Sunlight
            st.markdown(
                f"<h4 style='text-align: center; margin: 0;'>Remaining Sunlight<br><span style='font-size: 20px;'>{sunlight_remaining} %</span></h4>",
                unsafe_allow_html=True
            )

            # Weather Forecast Link
            st.markdown(
                "<h4 style='text-align: center;margin: 0;'><a href='https://openweathermap.org/city/263824' target='_blank' style='text-decoration: none;'>Weather Forecast Agios Nikolaos</a></h4>",
                unsafe_allow_html=True
            )

        # Check for temperature alarms
        alarms = check_temperature_alarms(df)
        if alarms:
            st.error("Alarms Detected:")
            for alarm in alarms:
                st.write(alarm)

        # plot historical temperature data
        time_range = st.selectbox("Select Time Range", ['Past Week', 'Past 3 Days', 'Past Day'])
        filtered_df = filter_data(df, time_range)
        plot_temperatures(filtered_df)

    else:
        st.error("No weather data available.")


if __name__ == "__main__":
    main()
