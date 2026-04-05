# 🌍 CarbonIQ — Carbon Intelligence for Road Freight
link: https://carbon-iq.streamlit.app

CarbonIQ is an enterprise-grade **Carbon Intelligence Dashboard** for road freight logistics. It provides real-time emissions monitoring, shipment-level estimation, lane analytics, and what-if scenario modeling — all powered by a persistent AI Assistant.

## Key Features

- **Fleet Overview**: Monitor CO₂e emissions and freight volume trends.
- **Shipment Estimator**: Calculate carbon footprint at the lane level.
- **Lane Analytics**: Identify high-emission routes and optimize efficiency.
- **What-If Simulator**: Model the impact of fleet electrification and route optimization.
- **AI Assistant**: Get context-aware sustainability insights powered by Hugging Face.

## Quick Start

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   Set your `HF_API_TOKEN` in a `.env` file.

3. **Launch dashboard**:

   ```bash
   streamlit run app/app.py
   ```