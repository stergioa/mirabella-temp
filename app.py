import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objs as go
import pytz
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import os
from plotly.subplots import make_subplots

CSV_FILE = 'temperature_data.csv'

# Athens timezone
ATHENS_TZ = pytz.timezone('Europe/Athens')

# detect if user is on a mobile device
def is_mobile():
    user_agent = st.query_params.get('user_agent', [''])[0]
    return 'Mobile' in user_agent or 'iPhone' in user_agent or 'Android' in user_agent


# adjust time shift based on the selected time range and device
def get_time_shift(time_range):
    if is_mobile():  # Reduce the shift on mobile
        if time_range == 'Past Week':
            return pd.Timedelta(minutes=800)
        elif time_range == 'Past 3 Days':
            return pd.Timedelta(minutes=500)
        elif time_range == 'Past Day':
            return pd.Timedelta(minutes=160)
    else:
        if time_range == 'Past Week':
            return pd.Timedelta(minutes=500)
        elif time_range == 'Past 3 Days':
            return pd.Timedelta(minutes=250)
        elif time_range == 'Past Day':
            return pd.Timedelta(minutes=80)
        return pd.Timedelta(minutes=0)

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

def add_sun_overlay(fig, df):
    # hardcoded sunrise and sunset times
    sunrise_time = "06:41"
    sunset_time = "17:19"

    # extract unique days from the timestamp column
    unique_days = df['timestamp'].dt.date.unique()

    # determine the minimum and maximum temperature values for the plot
    y_min = df[['temp_1', 'temp_2', 'temp_3', 'temp_4', 'temp_5', 'temp_6']].min().min()
    y_max = df[['temp_1', 'temp_2', 'temp_3', 'temp_4', 'temp_5', 'temp_6']].max().max()

    for day in unique_days:
        # create datetime objects for sunrise and sunset
        sunrise = pd.to_datetime(f"{day} {sunrise_time}")
        sunset = pd.to_datetime(f"{day} {sunset_time}")

        # add a yellow translucent rectangle for the sun overlay
        fig.add_shape(
            type="rect",
            x0=sunrise,
            y0=y_min,
            x1=sunset,
            y1=y_max,
            fillcolor="yellow",
            opacity=0.15,  # reduced opacity for a subtler effect
            line_width=0,
            layer='below'  # ensure the overlay is behind the temperature lines
        )

    # add a dummy trace for the legend
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color="yellow", opacity=0.15),
            name="Sunlight"
        )
    )

    # return the updated figure
    return fig



def plot_correlations(df):
    # Mapping temperature columns to room names
    room_pairs = [
        ('temp_1', 'Rooms 11-12'),
        ('temp_2', 'Rooms 13-14'),
        ('temp_3', 'Rooms 15-16'),
        ('temp_4', 'Rooms 17-18'),
        ('temp_5', 'Rooms 21-23'),
        ('temp_6', 'Rooms 24-28')
    ]

    # Create a dictionary to map temp columns to room names
    temp_to_room_map = {temp: room for temp, room in room_pairs}

    # Correlation matrix for all boiler temperatures
    corr_matrix = df[['temp_1', 'temp_2', 'temp_3', 'temp_4', 'temp_5', 'temp_6']].corr()

    # Rename the index and columns of the correlation matrix using the room names
    corr_matrix.rename(index=temp_to_room_map, columns=temp_to_room_map, inplace=True)

    # Create the heatmap
    fig_corr_matrix = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='Viridis'
    ))
    fig_corr_matrix.update_layout(title="Boiler Temperature Correlation Matrix")

    # Display the heatmap
    st.plotly_chart(fig_corr_matrix, use_container_width=True)

# def forecast_temperature_series_with_average_seasonality(series, periods=288):
#     # Calculate the number of data points per day (assuming 300-second intervals, there are 288 points in a day)
#     points_per_day = periods
#
#     # Check if there is enough data for 5 days
#     if len(series) < points_per_day * 5:
#         raise ValueError("Not enough data to calculate a 5-day average seasonality forecast.")
#
#     # Fill in any missing values using interpolation
#     series = series.interpolate(method='linear')
#
#     # Collect the last 5 days' data, ensuring each slice has the correct number of points
#     recent_5_days_data = []
#     for i in range(5):
#         start_idx = -(i + 1) * points_per_day
#         end_idx = -i * points_per_day if -i * points_per_day != 0 else None
#         slice_data = series.iloc[start_idx:end_idx].values
#
#         # Use interpolation to fill gaps in the slice
#         if len(slice_data) < points_per_day:
#             slice_data = np.interp(
#                 np.arange(points_per_day),  # Points where we need values
#                 np.arange(len(slice_data)),  # Existing points
#                 slice_data  # Existing values
#             )
#
#         recent_5_days_data.append(slice_data)
#
#     # Calculate the average for each time point across the 5 days
#     forecast = np.mean(recent_5_days_data, axis=0)
#
#     return forecast



def plot_temperatures(df, time_range, overkill_mode, unfiltered_df):
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

        # Forecast temperature for each room using ARIMA
        forecast_times = pd.date_range(
            start=df['timestamp'].iloc[-1] + pd.Timedelta(seconds=300),
            periods=288,
            freq='300S'
        )
        # # Forecast temperature for each room using the simplified linear approach
        # forecasted_temps = {
        #     'Rooms 11-12': forecast_temperature_series_with_average_seasonality(unfiltered_df['temp_1']),
        #     'Rooms 13-14': forecast_temperature_series_with_average_seasonality(unfiltered_df['temp_2']),
        #     'Rooms 15-16': forecast_temperature_series_with_average_seasonality(unfiltered_df['temp_3']),
        #     'Rooms 17-18': forecast_temperature_series_with_average_seasonality(unfiltered_df['temp_4']),
        #     'Rooms 21-23': forecast_temperature_series_with_average_seasonality(unfiltered_df['temp_5']),
        #     'Rooms 24-28': forecast_temperature_series_with_average_seasonality(unfiltered_df['temp_6'])
        # }

        # Create figures for each room pair
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_1'], mode='lines', name='Rooms 11-12', line=dict(color='red'))
        )
        fig1.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_2'], mode='lines', name='Rooms 13-14', line=dict(color='blue'))
        )
        fig1.update_layout(
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            **common_layout
        )

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_3'], mode='lines', name='Rooms 15-16', line=dict(color='red'))
        )
        fig2.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_4'], mode='lines', name='Rooms 17-18', line=dict(color='blue'))
        )
        fig2.update_layout(
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            **common_layout
        )

        fig3 = go.Figure()
        fig3.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_5'], mode='lines', name='Rooms 21-23', line=dict(color='red'))
        )
        fig3.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_6'], mode='lines', name='Rooms 24-28', line=dict(color='blue'))
        )
        fig3.update_layout(
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            **common_layout
        )

        # Get the time shift for the current time range
        time_shift = get_time_shift(time_range)

        # Add annotations with time shift only if overkill mode is not activated
        fig1.add_annotation(
            x=df['timestamp'].iloc[-1] + time_shift,
            y=df['temp_1'].iloc[-1],
            text=f"{df['temp_1'].iloc[-1]:.1f} °C", showarrow=False, font=dict(color='red')
        )
        fig1.add_annotation(
            x=df['timestamp'].iloc[-1] + time_shift,
            y=df['temp_2'].iloc[-1],
            text=f"{df['temp_2'].iloc[-1]:.1f} °C", showarrow=False, font=dict(color='blue')
        )
        fig2.add_annotation(
            x=df['timestamp'].iloc[-1] + time_shift,
            y=df['temp_3'].iloc[-1],
            text=f"{df['temp_3'].iloc[-1]:.1f} °C", showarrow=False, font=dict(color='red')
        )
        fig2.add_annotation(
            x=df['timestamp'].iloc[-1] + time_shift,
            y=df['temp_4'].iloc[-1],
            text=f"{df['temp_4'].iloc[-1]:.1f} °C", showarrow=False, font=dict(color='blue')
        )
        fig3.add_annotation(
            x=df['timestamp'].iloc[-1] + time_shift,
            y=df['temp_5'].iloc[-1],
            text=f"{df['temp_5'].iloc[-1]:.1f} °C", showarrow=False, font=dict(color='red')
        )
        fig3.add_annotation(
            x=df['timestamp'].iloc[-1] + time_shift,
            y=df['temp_6'].iloc[-1],
            text=f"{df['temp_6'].iloc[-1]:.1f} °C", showarrow=False, font=dict(color='blue')
        )

        # if overkill, add sun overlay and forecasted temperatures
        if overkill_mode:
            for fig in [fig1, fig2, fig3]:
                fig = add_sun_overlay(fig, df)
            # fig1.add_trace(
            #     go.Scatter(x=forecast_times, y=forecasted_temps['Rooms 11-12'],
            #                mode='lines', name='Forecast Rooms 11-12', line=dict(color='red', dash='dash'))
            # )
            # fig1.add_trace(
            #     go.Scatter(x=forecast_times, y=forecasted_temps['Rooms 13-14'],
            #                mode='lines', name='Forecast Rooms 13-14', line=dict(color='blue', dash='dash'))
            # )
            # fig2.add_trace(
            #     go.Scatter(x=forecast_times, y=forecasted_temps['Rooms 15-16'],
            #                mode='lines', name='Forecast Rooms 15-16', line=dict(color='red', dash='dash'))
            # )
            # fig2.add_trace(
            #     go.Scatter(x=forecast_times, y=forecasted_temps['Rooms 17-18'],
            #                mode='lines', name='Forecast Rooms 17-18', line=dict(color='blue', dash='dash'))
            # )
            # fig3.add_trace(
            #     go.Scatter(x=forecast_times, y=forecasted_temps['Rooms 21-23'],
            #                mode='lines', name='Forecast Rooms 21-23', line=dict(color='red', dash='dash'))
            # )
            # fig3.add_trace(
            #     go.Scatter(x=forecast_times, y=forecasted_temps['Rooms 24-28'],
            #                mode='lines', name='Forecast Rooms 24-28', line=dict(color='blue', dash='dash'))
            # )

        # Plotly chart configuration to hide toolbar and disable zoom on mobile
        config = {
            'displayModeBar': False,  # Disable the toolbar
            'scrollZoom': False,      # Disable zoom on scroll or pinch on mobile
            'staticPlot': False,      # Completely disable all interactions
            'responsive': True        # Make charts responsive to screen size
        }

        # create tabs to choose rooms
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


def plot_correlation_gauges(df):
    # Define room names and corresponding temperature columns in groups of two
    room_pairs = [
        [('temp_1', 'Rooms 11-12'), ('temp_2', 'Rooms 13-14')],
        [('temp_3', 'Rooms 15-16'), ('temp_4', 'Rooms 17-18')],
        [('temp_5', 'Rooms 21-23'), ('temp_6', 'Rooms 24-28')]
    ]

    st.subheader("Correlation Gauges")
    # Create a selectbox for choosing the correlation type
    correlation_type = st.selectbox(
        "label",
        ["Boiler Temp. vs Cloud Coverage", "Boiler Temp. vs Exterior Temperature"],
        label_visibility="collapsed"
    )

    # Determine the column to use based on the selection
    correlation_column = (
        'current_cloudiness' if correlation_type == "Boiler Temp. vs Cloud Coverage" else 'current_temp'
    )

    # Create tabs to choose room groups
    tabs = st.tabs(["Rooms 11-14", "Rooms 15-18", "Rooms 21-28"])

    for tab, pairs in zip(tabs, room_pairs):
        with tab:
            # Create a 1x2 layout for the gauges
            fig = make_subplots(
                rows=1, cols=2,
                specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
                horizontal_spacing=0.2
            )
            # Add gauges to the figure
            for idx, (temp_col, room_name) in enumerate(pairs):
                correlation = df[temp_col].corr(df[correlation_column])
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=correlation,
                        title={'text': room_name, 'font': {'size': 20}},
                        gauge={
                            'axis': {'range': [-1, 1], 'tickfont': {'size': 15}},
                            'bar': {'thickness': 0},
                            'threshold': {
                                'line': {'color': "green", 'width': 2},
                                'thickness': 0.9,
                                'value': correlation
                            },
                        },
                    ),
                    row=1, col=idx + 1
                )
            # Update layout and display the figure
            fig.update_layout(height=300, width=700, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)


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
        col1, col2 = st.columns([3, 1])
        with col1:
            time_range = st.selectbox("Select Time Range", ['Past Week', 'Past 3 Days', 'Past Day'])
        with col2:
            st.write("")  # adds a blank line
            st.write("")
            overkill_mode = st.checkbox("Advanced Mode", value=True)
        unfiltered_df = df.copy()
        filtered_df = filter_data(df, time_range)
        plot_temperatures(filtered_df, time_range, overkill_mode, unfiltered_df)
        if overkill_mode:
            st.subheader("More Info")
            plot_correlations(filtered_df)
            plot_correlation_gauges(df)

    else:
        st.error("No weather data available.")


if __name__ == "__main__":
    main()
