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

# Load temperature data from CSV for plotting
def load_data(time_range):
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, format='ISO8601')
        df['timestamp'] = df['timestamp'].dt.tz_convert(ATHENS_TZ)  # Convert UTC to Athens time

        # Filter the data based on the selected time range
        if time_range == 'Past Week':
            return df[df['timestamp'] >= (datetime.now(ATHENS_TZ) - timedelta(days=7))]
        elif time_range == 'Past 3 Days':
            return df[df['timestamp'] >= (datetime.now(ATHENS_TZ) - timedelta(days=3))]
        elif time_range == 'Past Day':
            return df[df['timestamp'] >= (datetime.now(ATHENS_TZ) - timedelta(days=1))]
        else:
            return df
    else:
        return pd.DataFrame(columns=['timestamp', 'temp_1', 'temp_2', 'temp_3', 'temp_4', 'temp_5', 'temp_6'])

# Plot temperature data with dynamic width
def plot_temperatures(df):
    if not df.empty:
        # Define layout properties with centering for titles
        common_layout = dict(
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
            font=dict(size=12),             # Responsive font size
            title_font=dict(size=16),       # Responsive title font size
            showlegend=False,               # Remove legends
            xaxis=dict(title_font=dict(size=14), automargin=True),  # X-axis title with auto margins
            yaxis=dict(title_font=dict(size=14), automargin=True),  # Y-axis title with auto margins
            margin=dict(l=20, r=20, t=40, b=40),  # Tighter margins
            hovermode=False                 # Disable hover tooltips
        )

        # Custom HTML with white underline and colored numbers
        underline_style = "text-decoration: underline; color: white;"  # White underline styling

        # First plot: Rooms 11-12 (Red) & 13-14 (Blue)
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_1'], mode='lines', name='Rooms 11-12', line=dict(color='red')))
        fig1.add_trace(
            go.Scatter(x=df['timestamp'], y=df['temp_2'], mode='lines', name='Rooms 13-14', line=dict(color='blue')))
        fig1.update_layout(
            title=dict(
                text=f"<span style='{underline_style}'>Rooms <span style='color:red;'>11-12</span> & <span style='color:blue;'>13-14</span></span>",
                x=0.5,  # Center the title
                xanchor='center',  # Ensure title is centered
                yanchor='top'
            ),
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
            title=dict(
                text=f"<span style='{underline_style}'>Rooms <span style='color:red;'>15-16</span> & <span style='color:blue;'>17-18</span></span>",
                x=0.5,
                xanchor='center',
                yanchor='top'
            ),
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
            title=dict(
                text=f"<span style='{underline_style}'>Rooms <span style='color:red;'>21-23</span> & <span style='color:blue;'>24-28</span></span>",
                x=0.5,
                xanchor='center',
                yanchor='top'
            ),
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            **common_layout
        )

        # Plotly chart configuration to hide toolbar
        config = {
            'displayModeBar': False  # Disable the toolbar
        }

        # Display the three plots without toolbars and hover tooltips
        st.plotly_chart(fig1, use_container_width=True, config=config)
        st.plotly_chart(fig2, use_container_width=True, config=config)
        st.plotly_chart(fig3, use_container_width=True, config=config)
    else:
        st.write("No data available.")





# Main function for the Streamlit app
def main():
    st.title("Boiler Temperature Monitoring")

    # Use a narrower column width to fit mobile screens better
    # with col:
    time_range = st.selectbox(
        "Select Time Range",
        ['Past Week',
         'Past 3 Days',
         'Past Day']
    )

    df = load_data(time_range)
    plot_temperatures(df)

if __name__ == "__main__":
    main()
