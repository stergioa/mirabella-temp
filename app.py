import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objs as go
import pytz
import os

# Path to the CSV file
CSV_FILE = 'temperature_data.csv'

# Athens timezone
ATHENS_TZ = pytz.timezone('Europe/Athens')


def load_data():
    # Always load the full dataset
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

        # with st.expander("Rooms 11-12 & 13-14"):
        #     st.plotly_chart(fig1, use_container_width=True, config=config)
        # with st.expander("Rooms 15-16 & 17-18"):
        #     st.plotly_chart(fig2, use_container_width=True, config=config)
        # with st.expander("Rooms 21-23 & 24-28"):
        #     st.plotly_chart(fig3, use_container_width=True, config=config)

        tab1, tab2, tab3 = st.tabs(["Rooms 11-14", "15-18", "21-28"])
        with tab1:
            st.plotly_chart(fig1, use_container_width=True, config=config)
        with tab2:
            st.plotly_chart(fig2, use_container_width=True, config=config)
        with tab3:
            st.plotly_chart(fig3, use_container_width=True, config=config)

    else:
        st.write("No data available.")


def calculate_sunlight_remaining(sunrise, sunset):
    now = datetime.now(ATHENS_TZ)
    if now < sunrise:
        return 100  # Full sunlight remaining
    elif now > sunset:
        return 0  # No sunlight remaining
    else:
        total_duration = (sunset - sunrise).total_seconds()
        elapsed_duration = (now - sunrise).total_seconds()
        return max(0, min(100, 100 * (total_duration - elapsed_duration) / total_duration))


def main():
    st.set_page_config(page_title="Boiler Temp")
    st.title("Boiler Temperature Monitoring")

    # Load data
    df = load_data()

    # Display weather data if available
    if not df.empty:
        latest_data = df.iloc[-1]
        current_temp = latest_data['current_temp']
        current_humidity = latest_data['current_humidity']
        current_cloudiness = latest_data['current_cloudiness']
        current_sunrise = pd.to_datetime(latest_data['current_sunrise'])
        current_sunset = pd.to_datetime(latest_data['current_sunset'])
        three_day_forecast_avg = latest_data.get('three_day_forecast_avg', 'N/A')
        sunlight_remaining = calculate_sunlight_remaining(current_sunrise, current_sunset)

        # col1, col2, col3 = st.columns([0.5, 1, 1])

        # with col1:
        #     st.metric("Current Exterior Temp", f"{current_temp:.1f} °C")
        #
        # with col2:
        #     col2a, col2b = st.columns([1, 1])
        #     with col2a:
        #         st.metric("Current Cloudiness", f"{current_cloudiness:.1f} %")
        #     with col2b:
        #         st.metric("Next 3-Day Cloudiness", f"{three_day_forecast_avg:.1f} %")
        # with col3:
        #     col3a, col3b = st.columns([1, 1])
        #     with col3a:
        #         st.metric("Sunrise Time", f"{current_sunrise.strftime('%H:%M')}")
        #     with col3b:
        #         st.metric("Sunset Time", f"{current_sunset.strftime('%H:%M')}")
        # Move metrics to the sidebar
        with st.sidebar:
            st.markdown("<h3 style='text-align: center;'>Weather Conditions</h3>", unsafe_allow_html=True)

            # Current Exterior Temperature
            st.markdown(f"<h3 style='text-align: center;'>Current Exterior Temperature:</h3>", unsafe_allow_html=True)
            st.markdown(
                f"<h3 style='text-align: center;'><span style='font-size: 24px;'>{current_temp:.1f} °C</span></h3>",
                unsafe_allow_html=True)

            # Separator for Cloudiness metrics
            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)  # Reduced margin

            # Center Cloudiness metrics
            st.markdown("<h3 style='text-align: center;'>Cloud Coverage (%)</h3>", unsafe_allow_html=True)

            # Using columns for Cloudiness metrics
            col_sidebar_a, col_sidebar_b = st.columns(2)
            with col_sidebar_a:
                st.markdown(
                    f"<h4 style='text-align: center;'>Current:<br><span style='font-size: 18px;'>{current_cloudiness:.1f} %</span></h4>",
                    unsafe_allow_html=True)
            with col_sidebar_b:
                st.markdown(
                    f"<h4 style='text-align: center;'>Next 3-Days:<br><span style='font-size: 18px;'>{three_day_forecast_avg:.1f} %</span></h4>",
                    unsafe_allow_html=True)

            # Separator for Daylight Information
            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)  # Reduced margin

            # Center Daylight Information
            st.markdown("<h3 style='text-align: center;'>Daylight Information</h3>", unsafe_allow_html=True)

            # Using columns for Sunrise and Sunset metrics
            col_sidebar_c, col_sidebar_d = st.columns(2)
            with col_sidebar_c:
                st.markdown(
                    f"<h4 style='text-align: center;'>Sunrise Time:<br><span style='font-size: 18px;'>{current_sunrise.strftime('%H:%M')}</span></h4>",
                    unsafe_allow_html=True)
            with col_sidebar_d:
                st.markdown(
                    f"<h4 style='text-align: center;'>Sunset Time:<br><span style='font-size: 18px;'>{current_sunset.strftime('%H:%M')}</span></h4>",
                    unsafe_allow_html=True)
            st.markdown(
                "<h4 style='text-align: center;'><a href='https://openweathermap.org/city/263824' target='_blank' style='text-decoration: none;'>Weather Forecast Agios Nikolaos</a></h4>",
                unsafe_allow_html=True)

        # plot historical temperature data
        time_range = st.selectbox("Select Time Range", ['Past Week', 'Past 3 Days', 'Past Day'])
        filtered_df = filter_data(df, time_range)
        plot_temperatures(filtered_df)

    else:
        st.error("No weather data available.")

if __name__ == "__main__":
    main()
