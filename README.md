# 🌍 CarbonIQ — Carbon Intelligence for Road Freight
link: https://carbon-iq.streamlit.app
CarbonIQ is an enterprise-grade **Carbon Intelligence Dashboard** for road freight logistics. It provides real-time emissions monitoring, shipment-level estimation, lane analytics, and what-if scenario modeling — all powered by a persistent AI Assistant.

Built with **Streamlit**, **Plotly**, **Pandas**, and the **Hugging Face Inference API**.

---

##  Key Features

###  Fleet Emissions Overview
- Real-time KPI cards: Total CO₂e, Shipments, Avg/Shipment, Diesel Share, **Avg Fleet Age**
- AI-Generated Sustainability Intelligence (powered by Qwen 72B)
- Monthly emission trend chart (by fuel type)
- EPA SmartWay carrier efficiency leaderboard

###  Shipment Estimator
- Estimate CO₂e for any single shipment using the **GLEC Framework**
- Inputs: Origin, Destination, Carrier, Distance, Weight, Fuel Type, Vehicle Type, Load Factor, **Vehicle Age**
- Formula breakdown showing all factors including the **Age Multiplier**
- Visual gauge comparing estimate vs. fleet average

###  Lane Analytics
- Automatic lane risk classification (High / Medium / Low)
- Emission intensity vs. volume scatter plot
- Risk distribution pie chart
- **Vehicle Age Distribution** histogram
- Detailed lane data table

###  What-If Simulator
- Model 4 emission reduction levers simultaneously:
  - Diesel → EV switch
  - Diesel → CNG switch
  - Load consolidation improvement
  - Route optimization (shorter distances)
- Waterfall chart showing savings per lever
- Before vs. After comparison chart
- AI-generated scenario narrative

###  CarbonIQ AI Assistant
- Persistent chat sidebar powered by Hugging Face
- Context-aware — knows your fleet's emissions, fuel mix, routes, and **vehicle age profile**
- Ask natural language questions like *"What is the average age of our fleet?"*

---

##  Vehicle Age Factor

CarbonIQ accounts for **vehicle age degradation** in emission calculations:

| Vehicle Age | Impact |
|-------------|--------|
| 0–5 years | No impact (1.0× multiplier) |
| 6+ years | +1.5% emissions per additional year |

**Example:** A 10-year-old truck emits ~7.5% more CO₂e than a brand-new one of the same model.

---

##  Project Structure

```
CarbonIQ/
├── app/
│   ├── app.py              # Main Streamlit dashboard
│   ├── predictor.py         # GLEC emission estimator + age factor
│   ├── analytics.py         # KPIs, trends, lane risk classification
│   ├── simulator.py         # What-If scenario engine
│   └── ai_insights.py       # Hugging Face AI integration
├── data/
│   ├── sample_shipments.csv     # 800 shipments with vehicle_age
│   ├── emission_factors.csv     # UK GHG 2025 emission factors
│   └── carrier_performance.csv  # EPA SmartWay carrier benchmarks
├── .env                     # HF_API_TOKEN (not committed)
├── .streamlit/config.toml   # Streamlit config (telemetry off)
└── requirements.txt
```

---

##  Getting Started

### Prerequisites
- Python 3.9+
- A Hugging Face API token (for AI features)

### Installation

```bash
git clone https://github.com/yashgarg195/CarbonIQ.git
cd CarbonIQ
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the project root:

```env
HF_API_TOKEN=your_huggingface_token_here
HF_MODEL=Qwen/Qwen2.5-72B-Instruct
```

### Run

```bash
streamlit run app/app.py
```

The app will open at `http://localhost:8501`.

---

##  Data Sources

| Dataset | Source | Purpose |
|---------|--------|---------|
| `emission_factors.csv` | UK GHG Conversion Factors 2025 | Fuel/vehicle-specific CO₂e emission factors |
| `carrier_performance.csv` | EPA SmartWay | Carrier-level emission benchmarks |
| `sample_shipments.csv` | Synthetic | 800 Indian logistics shipments with vehicle age data |

---

##  Tech Stack

- **Frontend:** Streamlit + Plotly (dark glassmorphic theme)
- **Data:** Pandas, NumPy
- **AI:** Hugging Face Inference API (Qwen 72B)
- **Emission Model:** GLEC Framework with vehicle age degradation

---

##  License

This project is for educational and research purposes.

---

*Built with ♻️ by the CarbonIQ team*
