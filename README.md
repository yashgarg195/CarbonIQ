# CarbonIQ

CarbonIQ is a complete Carbon Intelligence System designed for road freight operations. It provides an enterprise-grade dashboard to monitor, analyze, and optimize fleet emissions, featuring real-time insights powered by a modern, fully-integrated AI Assistant.

## Features

- **Fleet Emissions Overview:** Track total fleet CO₂e, shipment counts, and view monthly emission trends.
- **Shipment Estimator:** Instantly calculate estimated CO₂e for individual shipments based on distance, weight, and fuel type.
- **Lane Analytics:** Identify high-emission routes, analyze risk distributions, and optimize route efficiency.
- **What-If Simulator:** Interactive scenario modeling to test the impact of electrifying the fleet, transitioning to CNG, consolidating loads, or optimizing routes.
- **AI Assistant Integration:** A persistent, context-aware AI chat built directly into the dashboard (powered by Hugging Face Inference API) that provides sustainability insights and answers queries.

## Technology Stack

- **Frontend / UI:** Streamlit (Custom 3:1 layout with AWS-style professional styling)
- **Data Visualization:** Plotly
- **Data Processing:** Pandas
- **AI Integration:** Hugging Face Inference API (`Qwen/Qwen2.5-72B-Instruct`)

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yashgarg195/CarbonIQ.git
   cd CarbonIQ
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Environment Variables:
   Create a `.env` file in the root directory and add your Hugging Face API token:
   ```env
   HF_API_TOKEN=your_huggingface_token_here
   ```

4. Run the application:
   ```bash
   streamlit run app/app.py
   ```