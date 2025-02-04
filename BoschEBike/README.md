# Bosch eBike Analytics System

A sophisticated analytics platform designed for Bosch eBike systems that helps users monitor, analyze, and optimize their eBike performance.

## Features

- **Range Estimation**: Calculate expected range based on:
  - Terrain type (flat, hilly, mountainous)
  - Assist level (eco, tour, sport, turbo)
  - Rider weight
  - Battery capacity

- **Battery Health Analysis**:
  - Monitor battery health percentage
  - Track charge cycles
  - Get maintenance recommendations
  - Predict battery lifespan

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/bosch-ebike-analytics.git
cd bosch-ebike-analytics
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit application:
```bash
streamlit run ebike_analytics.py
```

The application will open in your default web browser, providing an interactive interface for:
- Calculating range estimates
- Analyzing battery health
- Viewing performance metrics
- Getting maintenance recommendations

## Technical Details

- Built with Python 3.8+
- Uses Streamlit for the web interface
- Implements advanced algorithms for range estimation
- Utilizes machine learning for battery health prediction

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by Bosch eBike Systems
- Based on real-world eBike performance data
- Developed with best practices for eBike battery management 