import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from geopy.distance import geodesic
from sklearn.linear_model import LinearRegression
import anomaly_detection

class EBikeAnalytics:
    def __init__(self):
        self.battery_capacity = 500  # Wh (typical Bosch PowerTube 500)
        self.data = None
    
    def calculate_range_estimate(self, terrain_type, assist_level, rider_weight):
        """Calculate estimated range based on various factors"""
        base_range = {
            'flat': 100,
            'hilly': 70,
            'mountainous': 50
        }
        
        assist_multiplier = {
            'eco': 1.2,
            'tour': 1.0,
            'sport': 0.8,
            'turbo': 0.6
        }
        
        # Weight factor (based on 75kg reference)
        weight_factor = 1 - (max(0, rider_weight - 75) * 0.002)
        
        estimated_range = (base_range[terrain_type] * 
                         assist_multiplier[assist_level] * 
                         weight_factor)
        
        return round(estimated_range, 1)
    
    def analyze_battery_health(self, cycles, max_capacity, current_capacity):
        """Analyze battery health and provide recommendations"""
        health_percentage = (current_capacity / max_capacity) * 100
        
        if cycles > 500:
            wear_level = "High"
        elif cycles > 200:
            wear_level = "Medium"
        else:
            wear_level = "Low"
            
        return {
            'health_percentage': round(health_percentage, 1),
            'wear_level': wear_level,
            'recommendation': self._get_battery_recommendation(health_percentage)
        }
    
    def _get_battery_recommendation(self, health_percentage):
        if health_percentage < 70:
            return "Consider battery replacement"
        elif health_percentage < 80:
            return "Monitor battery performance closely"
        return "Battery is in good condition"

def show_main_page():
    st.title("🚲 Bosch eBike Analytics System")
    analyzer = EBikeAnalytics()

    # Main content
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Range Estimation")
        
        # Input parameters
        terrain_type = st.selectbox(
            "Terrain Type",
            ['flat', 'hilly', 'mountainous'],
            help="Select the type of terrain you'll be riding on"
        )
        
        assist_level = st.selectbox(
            "Assist Level",
            ['eco', 'tour', 'sport', 'turbo'],
            help="Choose your preferred motor assistance level"
        )
        
        rider_weight = st.slider(
            "Rider Weight (kg)", 
            40, 120, 75,
            help="Enter the rider's weight for more accurate range estimation"
        )
        
        estimated_range = analyzer.calculate_range_estimate(
            terrain_type, assist_level, rider_weight
        )
        
        st.metric(
            "Estimated Range",
            f"{estimated_range} km",
            delta=None,
            help="Estimated range based on current settings"
        )

    with col2:
        st.subheader("Battery Analysis")
        cycles = st.number_input(
            "Battery Cycles", 
            min_value=0, 
            value=100,
            help="Number of complete charge cycles"
        )
        
        current_capacity = st.number_input(
            "Current Capacity (Wh)", 
            min_value=0.0, 
            max_value=500.0, 
            value=480.0,
            help="Current battery capacity in Watt-hours"
        )
        
        if st.button("Analyze Battery"):
            battery_analysis = analyzer.analyze_battery_health(
                cycles, 500, current_capacity
            )
            st.info(f"Battery Health: {battery_analysis['health_percentage']}%")
            st.write(f"Wear Level: {battery_analysis['wear_level']}")
            st.write(f"Recommendation: {battery_analysis['recommendation']}")

def main():
    st.set_page_config(
        page_title="Bosch eBike Analytics",
        page_icon="🚲",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add navigation
    pages = {
        "Dashboard": show_main_page,
        "Anomaly Detection": anomaly_detection.main
    }
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        selection = st.radio("Go to", list(pages.keys()))
        
        st.markdown("---")
        st.markdown("### Settings")
        if selection == "Dashboard":
            st.markdown("""
            Configure your eBike settings and analyze its performance.
            Use the controls below to estimate range and check battery health.
            """)
        else:
            st.markdown("""
            Monitor your eBike's sensor data and detect potential issues.
            Generate sample data or upload your own sensor readings.
            """)
    
    # Display selected page
    pages[selection]()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "### About Bosch eBike Analytics\n"
        "This analytics system helps Bosch eBike users monitor their bike's "
        "performance, estimate range, track battery health, and detect anomalies. "
        "It uses advanced algorithms to provide accurate predictions and recommendations."
    )

if __name__ == "__main__":
    main() 