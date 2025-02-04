import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

class EBikeAnomalyDetector:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        
    def generate_sample_data(self, n_samples=1000):
        """Generate random eBike sensor data for demonstration"""
        # Generate timestamps with random start time in the last month
        start_date = datetime.now() - timedelta(days=random.randint(1, 30))
        timestamps = [start_date + timedelta(minutes=i*random.randint(5, 15)) for i in range(n_samples)]
        
        # Generate base patterns with daily cycles
        time_of_day = np.array([(t.hour + t.minute/60) for t in timestamps])
        daily_pattern = np.sin(2 * np.pi * time_of_day / 24)
        
        # Normal operating parameters with realistic variations
        motor_temp = []
        battery_voltage = []
        motor_rpm = []
        current_draw = []
        
        for i in range(n_samples):
            # Temperature varies with time of day and usage
            base_temp = 45 + 20 * daily_pattern[i]  # Base temperature varies between 25-65°C
            motor_temp.append(base_temp + random.gauss(0, 3))
            
            # Battery voltage decreases throughout the day
            base_voltage = 42 - (i/n_samples) * 4  # Voltage drops from 42V to 38V
            battery_voltage.append(base_voltage + random.gauss(0, 0.2))
            
            # RPM varies with terrain and rider input
            base_rpm = 200 + 100 * abs(daily_pattern[i])
            motor_rpm.append(base_rpm + random.gauss(0, 25))
            
            # Current draw correlates with RPM and temperature
            base_current = 8 + (motor_rpm[-1]/250) * 4
            current_draw.append(base_current + random.gauss(0, 1.5))
        
        # Convert to numpy arrays
        motor_temp = np.array(motor_temp)
        battery_voltage = np.array(battery_voltage)
        motor_rpm = np.array(motor_rpm)
        current_draw = np.array(current_draw)
        
        # Inject realistic anomalies
        n_anomalies = int(n_samples * random.uniform(0.03, 0.07))  # 3-7% anomalies
        anomaly_indices = random.sample(range(n_samples), n_anomalies)
        
        for idx in anomaly_indices:
            anomaly_type = random.choice(['temp', 'voltage', 'rpm', 'current', 'combined'])
            
            if anomaly_type == 'temp' or anomaly_type == 'combined':
                motor_temp[idx] += random.choice([-1, 1]) * random.uniform(15, 25)
            
            if anomaly_type == 'voltage' or anomaly_type == 'combined':
                battery_voltage[idx] += random.choice([-1, 1]) * random.uniform(3, 6)
            
            if anomaly_type == 'rpm' or anomaly_type == 'combined':
                motor_rpm[idx] *= random.uniform(0.3, 2.0)
            
            if anomaly_type == 'current' or anomaly_type == 'combined':
                current_draw[idx] *= random.uniform(1.5, 2.5)
        
        # Create DataFrame with the generated data
        df = pd.DataFrame({
            'timestamp': timestamps,
            'motor_temperature': motor_temp,
            'battery_voltage': battery_voltage,
            'motor_rpm': motor_rpm,
            'current_draw': current_draw
        })
        
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
    
    def detect_anomalies(self, data):
        """Detect anomalies in the sensor data"""
        # Prepare features for anomaly detection
        features = data[['motor_temperature', 'battery_voltage', 'motor_rpm', 'current_draw']]
        
        # Scale the features
        scaled_features = self.scaler.fit_transform(features)
        
        # Calculate dynamic contamination based on data variance
        feature_std = np.std(scaled_features, axis=0)
        base_contamination = 0.05  # 5% base rate
        variance_factor = np.mean(feature_std) / 2
        contamination = min(max(base_contamination + variance_factor, 0.01), 0.15)
        
        # Initialize model with dynamic contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=None,
            n_estimators=200,
            max_samples='auto'
        )
        
        # Fit the model and predict
        predictions = self.model.fit_predict(scaled_features)
        
        # Add predictions and anomaly scores to the dataframe
        data['anomaly'] = predictions
        data['anomaly_score'] = self.model.score_samples(scaled_features)
        
        return data
    
    def plot_anomalies(self, data, feature):
        """Create an interactive plot highlighting anomalies"""
        fig = go.Figure()
        
        # Plot normal points
        normal_data = data[data['anomaly'] == 1]
        fig.add_trace(go.Scatter(
            x=normal_data['timestamp'],
            y=normal_data[feature],
            mode='markers',
            name='Normal',
            marker=dict(
                color=normal_data['anomaly_score'],
                colorscale='Viridis',
                size=6,
                showscale=True,
                colorbar=dict(title='Anomaly Score')
            ),
            hovertemplate=(
                "<b>Time</b>: %{x}<br>" +
                "<b>Value</b>: %{y:.2f}<br>" +
                "<b>Score</b>: %{marker.color:.3f}<br>" +
                "<extra></extra>"
            )
        ))
        
        # Plot anomalies
        anomaly_data = data[data['anomaly'] == -1]
        fig.add_trace(go.Scatter(
            x=anomaly_data['timestamp'],
            y=anomaly_data[feature],
            mode='markers',
            name='Anomaly',
            marker=dict(
                color='red',
                size=10,
                symbol='x'
            ),
            hovertemplate=(
                "<b>Time</b>: %{x}<br>" +
                "<b>Value</b>: %{y:.2f}<br>" +
                "<extra></extra>"
            )
        ))
        
        fig.update_layout(
            title=f'{feature} Over Time',
            xaxis_title='Time',
            yaxis_title=feature,
            hovermode='closest',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig

def main():
    st.title("🔍 Bosch eBike Anomaly Detection")
    st.write("""
    This page analyzes sensor data from your eBike to detect potential anomalies 
    that might indicate maintenance needs or system issues.
    """)
    
    # Initialize the anomaly detector
    detector = EBikeAnomalyDetector()
    
    # Generate or load data
    st.subheader("Sensor Data Analysis")
    
    # Add controls for data generation
    col1, col2 = st.columns(2)
    with col1:
        n_samples = st.slider("Number of data points", 100, 2000, 1000, 100)
    
    if st.button("Generate Sample Data"):
        data = detector.generate_sample_data(n_samples=n_samples)
        st.session_state['sensor_data'] = data
        st.session_state['processed_data'] = detector.detect_anomalies(data.copy())
        
        # Calculate actual contamination
        anomaly_count = len(st.session_state['processed_data'][st.session_state['processed_data']['anomaly'] == -1])
        contamination = anomaly_count / len(data)
        st.success(f"Sample data generated and analyzed! Detected contamination rate: {contamination:.1%}")
    
    # If data exists in session state, show analysis
    if 'processed_data' in st.session_state:
        data = st.session_state['processed_data']
        
        # Summary statistics
        st.subheader("Anomaly Detection Summary")
        total_anomalies = len(data[data['anomaly'] == -1])
        total_records = len(data)
        anomaly_percentage = (total_anomalies / total_records) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Anomalies", total_anomalies)
        with col2:
            st.metric("Total Records", total_records)
        with col3:
            st.metric("Anomaly Percentage", f"{anomaly_percentage:.1f}%")
        
        # Feature selection for plotting
        feature = st.selectbox(
            "Select sensor data to visualize:",
            ['motor_temperature', 'battery_voltage', 'motor_rpm', 'current_draw']
        )
        
        # Plot the selected feature
        fig = detector.plot_anomalies(data, feature)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed anomaly analysis
        st.subheader("Detailed Anomaly Analysis")
        anomaly_data = data[data['anomaly'] == -1].copy()
        if not anomaly_data.empty:
            anomaly_data['timestamp'] = anomaly_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            st.write("Recent anomalies detected:")
            
            # Sort by anomaly score and show the most significant anomalies
            anomaly_data['anomaly_score'] = abs(anomaly_data['anomaly_score'])
            anomaly_data = anomaly_data.sort_values('anomaly_score', ascending=False)
            st.dataframe(
                anomaly_data[['timestamp', 'motor_temperature', 'battery_voltage', 
                             'motor_rpm', 'current_draw', 'anomaly_score']].head(10)
            )
            
            # Recommendations based on anomalies
            st.subheader("Recommendations")
            if len(anomaly_data[anomaly_data['motor_temperature'] > 70]) > 0:
                st.warning("⚠️ High motor temperature detected. Consider checking cooling system.")
            if len(anomaly_data[anomaly_data['battery_voltage'] < 32]) > 0:
                st.warning("⚠️ Low battery voltage detected. Battery might need inspection.")
            if len(anomaly_data[anomaly_data['current_draw'] > 15]) > 0:
                st.warning("⚠️ High current draw detected. Check for motor efficiency issues.")
        else:
            st.success("No anomalies detected in the current dataset!")

if __name__ == "__main__":
    main() 