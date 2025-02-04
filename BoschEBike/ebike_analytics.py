import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add the current directory to Python path for local imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

import anomaly_detection

# Constants for calculations
BATTERY_CAPACITY = 500  # Wh
ASSIST_LEVELS = {
    'ECO': 0.4,
    'TOUR': 0.7,
    'SPORT': 1.0,
    'TURBO': 1.3
}

def calculate_range(terrain_type, assist_level, rider_weight, battery_health):
    """Calculate estimated range based on various factors"""
    # Base range calculation
    base_range = BATTERY_CAPACITY / 15  # Assuming 15Wh/km base consumption
    
    # Apply terrain factor
    terrain_factors = {
        'Flat': 1.0,
        'Rolling Hills': 0.8,
        'Mountainous': 0.6
    }
    range_with_terrain = base_range * terrain_factors[terrain_type]
    
    # Apply assist level factor
    range_with_assist = range_with_terrain / ASSIST_LEVELS[assist_level.upper()]
    
    # Apply weight factor (assuming base calculation is for 75kg rider)
    weight_factor = 1 - ((rider_weight - 75) * 0.003)  # 0.3% reduction per kg above 75kg
    range_with_weight = range_with_assist * weight_factor
    
    # Apply battery health factor
    range_with_battery = range_with_weight * (battery_health / 100)
    
    return max(round(range_with_battery, 1), 0)

def predict_battery_lifespan(cycles, depth_of_discharge):
    """Predict remaining battery lifespan based on usage patterns"""
    max_cycles = 1000  # Maximum cycles under optimal conditions
    
    # Impact of depth of discharge on battery life
    dod_factor = 1 - (depth_of_discharge - 0.5) * 0.5
    
    remaining_cycles = max(0, (max_cycles * dod_factor) - cycles)
    remaining_percentage = (remaining_cycles / (max_cycles * dod_factor)) * 100
    
    return round(remaining_percentage, 1)

def generate_sample_data():
    """Generate sample ride data for visualization"""
    dates = pd.date_range(start='2024-01-01', end='2024-02-01', freq='D')
    data = {
        'Date': dates,
        'Distance': np.random.normal(25, 5, len(dates)),  # km
        'Battery_Used': np.random.uniform(40, 80, len(dates)),  # %
        'Assist_Level': np.random.choice(list(ASSIST_LEVELS.keys()), len(dates)),
        'Average_Speed': np.random.normal(20, 3, len(dates))  # km/h
    }
    return pd.DataFrame(data)

def validate_ride_data(df):
    """Validate uploaded ride data format"""
    required_columns = ['Date', 'Distance', 'Battery_Used', 'Assist_Level', 'Average_Speed']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Convert Date column to datetime if it's not already
    try:
        df['Date'] = pd.to_datetime(df['Date'])
    except Exception:
        return False, "Could not parse Date column. Please ensure it's in a valid date format."
    
    return True, ""

def show_ride_analytics(df):
    """Display ride analytics for the given dataframe"""
    # Ride statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Average Daily Distance",
            f"{df['Distance'].mean():.1f} km",
            f"{df['Distance'].mean() - df['Distance'].shift(1).mean():.1f} km"
        )
    
    with col2:
        st.metric(
            "Average Battery Usage",
            f"{df['Battery_Used'].mean():.1f}%",
            f"{df['Battery_Used'].mean() - df['Battery_Used'].shift(1).mean():.1f}%"
        )
    
    with col3:
        st.metric(
            "Average Speed",
            f"{df['Average_Speed'].mean():.1f} km/h",
            f"{df['Average_Speed'].mean() - df['Average_Speed'].shift(1).mean():.1f} km/h"
        )
    
    # Distance over time chart
    fig_distance = px.line(
        df,
        x='Date',
        y='Distance',
        title='Daily Riding Distance'
    )
    st.plotly_chart(fig_distance)
    
    # Assist level distribution
    fig_assist = px.pie(
        df,
        names='Assist_Level',
        title='Assist Level Distribution'
    )
    st.plotly_chart(fig_assist)
    
    # Battery usage patterns
    fig_battery = px.scatter(
        df,
        x='Distance',
        y='Battery_Used',
        color='Assist_Level',
        title='Battery Usage vs. Distance by Assist Level'
    )
    st.plotly_chart(fig_battery)
    
    # Additional statistics
    st.subheader("Detailed Statistics")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Distance Statistics")
        st.write(f"Total Distance: {df['Distance'].sum():.1f} km")
        st.write(f"Longest Ride: {df['Distance'].max():.1f} km")
        st.write(f"Shortest Ride: {df['Distance'].min():.1f} km")
    
    with col2:
        st.markdown("#### Battery Usage Statistics")
        st.write(f"Average Battery per km: {(df['Battery_Used'] / df['Distance']).mean():.1f}%/km")
        st.write(f"Most Efficient Ride: {(df['Battery_Used'] / df['Distance']).min():.1f}%/km")
        st.write(f"Least Efficient Ride: {(df['Battery_Used'] / df['Distance']).max():.1f}%/km")
    
    # Show raw data if requested
    if st.checkbox("Show Raw Data"):
        st.dataframe(df)
        
        # Download button for the data
        csv = df.to_csv(index=False)
        st.download_button(
            "Download Ride Data",
            csv,
            "ride_data.csv",
            "text/csv",
            key='download-csv'
        )

def main():
    st.title("Bosch eBike Analytics System")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Select Page",
        ["Range Estimation", "Battery Health", "Ride Analytics", "Anomaly Detection"]
    )
    
    if page == "Range Estimation":
        st.header("Range Estimation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            terrain = st.selectbox(
                "Terrain Type",
                ["Flat", "Rolling Hills", "Mountainous"]
            )
            
            assist = st.selectbox(
                "Assist Level",
                list(ASSIST_LEVELS.keys())
        )

    with col2:
            weight = st.number_input(
                "Rider Weight (kg)",
                min_value=40,
                max_value=150,
                value=75
            )
            
            battery_health = st.slider(
                "Battery Health (%)",
            min_value=0, 
                max_value=100,
                value=100
            )
        
        if st.button("Calculate Range"):
            range_estimate = calculate_range(terrain, assist, weight, battery_health)
            
            # Display result with gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=range_estimate,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Estimated Range (km)"},
                gauge={
                    'axis': {'range': [None, 120]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 40], 'color': "red"},
                        {'range': [40, 80], 'color': "yellow"},
                        {'range': [80, 120], 'color': "green"}
                    ]
                }
            ))
            
            st.plotly_chart(fig)
            
            # Additional range information
            st.info(f"""
            Based on your inputs:
            - Terrain impact: {terrain} terrain typically {'reduces' if terrain != 'Flat' else 'maintains'} range
            - Assist level {assist} uses {ASSIST_LEVELS[assist]}x base power
            - Weight factor is calculated relative to a 75kg reference
            - Current battery health: {battery_health}%
            """)
    
    elif page == "Battery Health":
        st.header("Battery Health Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cycles = st.number_input(
                "Charge Cycles",
                min_value=0,
                max_value=2000,
                value=100
            )
        
        with col2:
            avg_discharge = st.slider(
                "Average Depth of Discharge (%)",
                min_value=0,
                max_value=100,
                value=60
            ) / 100
        
        remaining_life = predict_battery_lifespan(cycles, avg_discharge)
        
        # Display battery health gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=remaining_life,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Battery Health"},
            delta={'reference': 100},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "red"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ]
            }
        ))
        
        st.plotly_chart(fig)
        
        # Battery health recommendations
        if remaining_life < 30:
            st.warning("Battery replacement recommended soon.")
        elif remaining_life < 70:
            st.info("Battery health is moderate. Consider optimizing charging habits.")
        else:
            st.success("Battery is in good health!")
        
            st.markdown("""
        ### Battery Care Tips:
        - Avoid complete discharges when possible
        - Store at 30-60% charge if not using for extended periods
        - Avoid extreme temperatures
        - Use official Bosch charger
        """)
    
    elif page == "Ride Analytics":
        st.header("Ride Analytics")
        
        # Data source selection
        data_source = st.radio(
            "Select Data Source",
            ["Use Sample Data", "Upload Ride Data"],
            help="Choose between sample data or upload your own ride data"
        )
        
        if data_source == "Upload Ride Data":
            st.info("""
            Upload a CSV file with the following columns:
            - Date: Date of the ride
            - Distance: Distance in kilometers
            - Battery_Used: Battery percentage used
            - Assist_Level: One of ECO, TOUR, SPORT, or TURBO
            - Average_Speed: Average speed in km/h
            """)
            
            uploaded_file = st.file_uploader(
                "Upload ride data (CSV)",
                type=['csv'],
                help="Upload your ride data in CSV format"
            )
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    valid, error_msg = validate_ride_data(df)
                    
                    if not valid:
                        st.error(f"Invalid data format: {error_msg}")
                        return
                        
                    show_ride_analytics(df)
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
            else:
                st.warning("Please upload a CSV file or switch to sample data")
                
                # Show sample CSV format
                st.markdown("#### Sample CSV Format:")
                sample_data = pd.DataFrame({
                    'Date': ['2024-01-01', '2024-01-02'],
                    'Distance': [25.5, 30.2],
                    'Battery_Used': [45, 55],
                    'Assist_Level': ['ECO', 'TOUR'],
                    'Average_Speed': [18.5, 20.1]
                })
                st.dataframe(sample_data)
                
                # Download sample template
                csv = sample_data.to_csv(index=False)
                st.download_button(
                    "Download Sample Template",
                    csv,
                    "ride_data_template.csv",
                    "text/csv",
                    key='download-template'
                )
        else:
            # Use sample data
            df = generate_sample_data()
            show_ride_analytics(df)
    
    else:  # Anomaly Detection page
        anomaly_detection.main()

if __name__ == "__main__":
    main() 