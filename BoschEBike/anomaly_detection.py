import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def generate_sample_sensor_data(n_samples=1000):
    """Generate sample sensor data for demonstration"""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=n_samples, freq='H')
    
    # Normal operating ranges
    temp_normal = np.random.normal(45, 5, n_samples)  # Battery temperature (°C)
    voltage_normal = np.random.normal(36, 2, n_samples)  # Battery voltage (V)
    current_normal = np.random.normal(10, 2, n_samples)  # Current draw (A)
    
    # Add some anomalies (5% of data)
    n_anomalies = n_samples // 20
    anomaly_idx = np.random.choice(n_samples, n_anomalies, replace=False)
    
    temp_normal[anomaly_idx] += np.random.normal(20, 5, n_anomalies)
    voltage_normal[anomaly_idx] += np.random.normal(-5, 2, n_anomalies)
    current_normal[anomaly_idx] += np.random.normal(15, 5, n_anomalies)
    
    data = pd.DataFrame({
        'timestamp': dates,
        'temperature': temp_normal,
        'voltage': voltage_normal,
        'current': current_normal
    })
    
    return data

def detect_anomalies(data, contamination=0.05):
    """Detect anomalies in sensor data using Isolation Forest"""
    # Prepare data for anomaly detection
    features = ['temperature', 'voltage', 'current']
    X = data[features]
        
        # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest
    iso_forest = IsolationForest(contamination=contamination, random_state=42)
    anomalies = iso_forest.fit_predict(X_scaled)
    
    # Add anomaly predictions to the dataframe
    data['is_anomaly'] = anomalies == -1
        
        return data
    
def plot_sensor_data(data, sensor_type):
    """Plot sensor data with anomalies highlighted"""
    fig = px.scatter(
        data,
        x='timestamp',
        y=sensor_type,
        color='is_anomaly',
        color_discrete_map={True: 'red', False: 'blue'},
        title=f'{sensor_type.title()} Over Time',
        labels={'is_anomaly': 'Is Anomaly'}
    )
        return fig

def main():
    st.title("eBike Anomaly Detection")
    st.write("""
    Monitor your eBike's sensor data and detect potential issues using machine learning.
    This system uses an Isolation Forest algorithm to identify anomalous behavior in:
    - Battery Temperature
    - Voltage Levels
    - Current Draw
    """)
    
    # Sidebar controls
    st.sidebar.header("Detection Settings")
    contamination = st.sidebar.slider(
        "Anomaly Threshold",
        min_value=0.01,
        max_value=0.20,
        value=0.05,
        help="Percentage of data points to be considered as anomalies"
    )
    
    # Generate or upload data
    data_source = st.radio(
        "Select Data Source",
        ["Generate Sample Data", "Upload Sensor Data"]
    )
    
    if data_source == "Generate Sample Data":
        n_samples = st.slider(
            "Number of Data Points",
            min_value=100,
            max_value=5000,
            value=1000
        )
        data = generate_sample_sensor_data(n_samples)
    else:
        uploaded_file = st.file_uploader(
            "Upload sensor data CSV",
            type=['csv'],
            help="CSV should contain columns: timestamp, temperature, voltage, current"
        )
        if uploaded_file is not None:
            try:
                data = pd.read_csv(uploaded_file)
                data['timestamp'] = pd.to_datetime(data['timestamp'])
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                return
        else:
            st.info("Please upload a CSV file or switch to sample data")
            return
    
    # Detect anomalies
    if st.button("Detect Anomalies"):
        with st.spinner("Analyzing sensor data..."):
            data_with_anomalies = detect_anomalies(data, contamination)
            
            # Display summary
            n_anomalies = data_with_anomalies['is_anomaly'].sum()
            st.metric(
                "Detected Anomalies",
                f"{n_anomalies} points",
                f"{(n_anomalies/len(data)*100):.1f}% of data"
            )
            
            # Plot each sensor's data
            st.subheader("Temperature Analysis")
            st.plotly_chart(plot_sensor_data(data_with_anomalies, 'temperature'))
            
            st.subheader("Voltage Analysis")
            st.plotly_chart(plot_sensor_data(data_with_anomalies, 'voltage'))
            
            st.subheader("Current Analysis")
            st.plotly_chart(plot_sensor_data(data_with_anomalies, 'current'))
            
            # Anomaly details
            if n_anomalies > 0:
                st.subheader("Anomaly Details")
                anomalies = data_with_anomalies[data_with_anomalies['is_anomaly']]
                st.dataframe(anomalies)
                
                # Download anomaly report
                csv = anomalies.to_csv(index=False)
                st.download_button(
                    "Download Anomaly Report",
                    csv,
                    "anomaly_report.csv",
                    "text/csv",
                    key='download-csv'
                )

if __name__ == "__main__":
    main() 