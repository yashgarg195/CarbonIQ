"""CarbonIQ — Carbon Intelligence Dashboard for Road Freight."""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.predictor import estimate_emissions, get_all_fuel_types, get_all_vehicle_types
from app.analytics import (
    summary_kpis,
    top_emission_lanes,
    emission_trend,
    lane_risk_classification,
    fuel_mix,
    carrier_efficiency_leaderboard,
)
from app.simulator import run_combined_scenario, simulate_ev_switch, simulate_load_improvement
from app.ai_insights import (
    generate_fleet_summary,
    generate_scenario_narrative,
    ask_carbon_agent,
    is_available as ai_is_available,
)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CarbonIQ | Carbon Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    /* Global Typography & Background */
    .stApp {
        font-family: 'Outfit', sans-serif;
        background: radial-gradient(circle at top right, #1a1c2c, #0f111a);
        color: #e6e6e6;
    }

    /* Professional Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(22, 27, 34, 0.95);
        border-right: 1px solid rgba(48, 54, 61, 0.5);
        backdrop-filter: blur(10px);
    }
    
    /* Layout structural spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 100% !important;
    }

    /* Fixed Right AI Console Pane - TARGET ONLY THE TOP-LEVEL LAYOUT */
    div[data-testid="stMainBlockContainer"] > div > div > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
        position: fixed !important;
        right: 0 !important;
        top: 0 !important;
        width: 350px !important;
        height: 100vh !important;
        background-color: #161b22 !important;
        border-left: 1px solid #30363d !important;
        padding: 60px 24px 80px 24px !important;
        z-index: 1000 !important;
        overflow-y: auto !important;
        display: block !important;
    }

    /* Push main content to the left to make room for fixed AI panel */
    section[data-testid="stMain"] {
        margin-right: 350px !important;
        width: calc(100% - 350px) !important;
    }

    /* Fixed Chat Input aligned with fixed AI panel */
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 0 !important;
        right: 0 !important;
        width: 350px !important;
        background-color: #161b22 !important;
        border-top: 1px solid #30363d !important;
        padding: 10px 20px 20px 20px !important;
        z-index: 1001 !important;
        left: auto !important;
    }

    /* AI Header styling (Pinned to top of pane) */
    .ai-console-header {
        position: sticky !important;
        top: 0 !important;
        background-color: #161b22 !important;
        z-index: 1002 !important;
        padding-bottom: 10px !important;
        border-bottom: 1px solid #30363d !important;
        margin-bottom: 16px !important;
        margin-top: -20px !important; /* Counteract pane padding */
    }
    
    .ai-console-header h3 {
        white-space: nowrap !important;
        margin: 0 !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #58a6ff !important;
    }
    .ai-console-header p {
        margin: 0 !important;
        font-size: 12px !important;
        color: #8b949e !important;
    }

    /* Sidebar Navigation Browsing */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background-color: transparent;
        color: #c9d1d9;
        border: none;
        border-radius: 4px;
        padding: 12px 16px;
        text-align: left;
        font-weight: 500;
        font-size: 14px;
        justify-content: flex-start;
        transition: background-color 0.1s ease;
        margin-bottom: 4px;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #21262d;
        color: #ffffff;
    }

    /* KPI Cards - Glassmorphism */
    .kpi-container {
        display: flex;
        gap: 24px;
        margin-bottom: 24px;
        flex-wrap: wrap;
    }
    .kpi-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(5px);
        transition: transform 0.3s ease, border 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(58, 123, 213, 0.5);
        background: rgba(255, 255, 255, 0.05);
    }
    .kpi-value {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #fff 0%, #aaa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0;
    }
    .kpi-label {
        font-size: 11px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }

    /* AI Card - Neon Accent */
    .ai-card {
        background: linear-gradient(135deg, rgba(35, 134, 54, 0.1) 0%, rgba(16, 21, 26, 0.5) 100%);
        border: 1px solid rgba(35, 134, 54, 0.3);
        border-left: 5px solid #238636;
        border-radius: 12px;
        padding: 24px;
        margin: 24px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Leaderboard Styles */
    .leaderboard-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    .leaderboard-row {
        border-bottom: 1px solid rgba(48, 54, 61, 0.5);
    }
    .leaderboard-rank {
        color: #58a6ff;
        font-weight: 700;
        padding: 12px;
    }
    .leaderboard-name {
        padding: 12px;
        font-weight: 500;
    }
    .leaderboard-value {
        text-align: right;
        padding: 12px;
        color: #3fb950;
        font-weight: 600;
    }

    /* Page headers */
    .page-header {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(90deg, #fff, #8b949e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    
    /* Fixed Chat Pane logic remains... */
</style>
""", unsafe_allow_html=True)


# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_shipments.csv")
    return pd.read_csv(data_path)


df = load_data()

# ── Application State ─────────────────────────────────────────────────────────
if "current_page" not in st.session_state:
    st.session_state.current_page = "Overview"
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Left Ribbon Navigation ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h3 style='color: #ffffff; padding: 0 16px; margin-bottom: 0;'>CarbonIQ</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8b949e; font-size: 12px; padding: 0 16px; margin-bottom: 24px;'>Carbon Intelligence</p>", unsafe_allow_html=True)

    st.markdown("<p style='color: #8b949e; font-size: 11px; text-transform: uppercase; font-weight: 600; padding: 0 16px; margin: 16px 0 8px 0;'>Dashboards</p>", unsafe_allow_html=True)
    if st.button("Overview", key="nav_overview"):
        st.session_state.current_page = "Overview"
    
    st.markdown("<p style='color: #8b949e; font-size: 11px; text-transform: uppercase; font-weight: 600; padding: 0 16px; margin: 16px 0 8px 0;'>Tools</p>", unsafe_allow_html=True)
    if st.button("Shipment Estimator", key="nav_estimator"):
        st.session_state.current_page = "Estimator"
    if st.button("Lane Analytics", key="nav_analytics"):
        st.session_state.current_page = "Analytics"
    if st.button("What-If Simulator", key="nav_simulator"):
        st.session_state.current_page = "Simulator"

    st.markdown("---")

page = st.session_state.current_page

# ── Main 3:1 Layout Grid ──────────────────────────────────────────────────────
main_col, ai_col = st.columns([7, 3], gap="small")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: Overview Dashboard
# ══════════════════════════════════════════════════════════════════════════════
with main_col:
    if page == "Overview":
        st.markdown('<div class="page-header">Fleet Emissions Overview</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subtitle">Real-time carbon intelligence for your road freight operations</div>', unsafe_allow_html=True)

        kpis = summary_kpis(df)
        top_lanes = top_emission_lanes(df, n=10)

        # KPI Cards
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-label">Total CO₂e</div>
                <div class="kpi-value">{kpis['total_co2e']:,.0f} kg</div>
                <div class="kpi-sublabel" style="color: #3fb950;">{kpis['total_co2e']/1000:,.1f} tonnes</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Shipments</div>
                <div class="kpi-value">{kpis['shipment_count']}</div>
                <div class="kpi-sublabel">Tracked this period</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Avg / Shipment</div>
                <div class="kpi-value">{kpis['avg_per_shipment']:,.1f} kg</div>
                <div class="kpi-sublabel">CO₂e per shipment</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Diesel Share</div>
                <div class="kpi-value">{kpis['diesel_share']}%</div>
                <div class="kpi-sublabel">of total fleet</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # AI Summary
        if ai_is_available():
            with st.spinner("Generating AI summary..."):
                ai_summary = generate_fleet_summary(kpis, top_lanes)
            st.markdown(f"""
            <div class="ai-card">
                <h4>AI-Generated Sustainability Intelligence</h4>
                <p>{ai_summary}</p>
            </div>
            """, unsafe_allow_html=True)

        # Charts Row
        col_left, col_right = st.columns([1, 1], gap="large")

        with col_left:
            st.markdown("#### Monthly Emission Trend (kg CO₂e)")
            trend_df = emission_trend(df, freq="M")
            fig_trend = px.area(
                trend_df,
                x="date",
                y="co2e_kg",
                color="fuel_type",
                color_discrete_map={"Diesel": "#ff6b6b", "CNG": "#ffd93d", "EV": "#34e89e"},
                labels={"co2e_kg": "", "date": "", "fuel_type": "Fuel"},
            )
            fig_trend.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
                height=260,
            )
            fig_trend.update_xaxes(showgrid=False)
            fig_trend.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_right:
            st.markdown("#### Carrier Efficiency Leaderboard (EPA Dataset)")
            # Get leaderboard
            leaderboard = carrier_efficiency_leaderboard(df, n=5)
            if not leaderboard.empty:
                for _, row in leaderboard.iterrows():
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.02); border-radius: 8px; padding: 10px; margin-bottom: 8px; border-left: 3px solid #3fb950; display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 13px; font-weight: 500;">{row['carrier_name']}</span>
                        <span style="font-size: 12px; color: #3fb950; font-weight: 600;">{row['ef_kg_per_tkm']:.4f} kg/tkm</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Generating carrier performance benchmarks...")


    # ══════════════════════════════════════════════════════════════════════════════
    # PAGE 2: Shipment Estimator
    # ══════════════════════════════════════════════════════════════════════════════
    elif page == "Estimator":
        st.markdown('<div class="page-header">Shipment Emission Estimator</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subtitle">Estimate CO₂e for a single shipment using the GLEC Framework formula</div>', unsafe_allow_html=True)

        col_form, col_result = st.columns([1, 1])

        with col_form:
            origins = sorted(df["origin"].unique().tolist())
            destinations = sorted(df["destination"].unique().tolist())

            # Load unique carriers for selection
            carrier_performance_path = os.path.join(os.path.dirname(__file__), "..", "data", "carrier_performance.csv")
            try:
                carriers_df = pd.read_csv(carrier_performance_path)
                carrier_list = ["(General / Unknown)"] + sorted(carriers_df["carrier_name"].unique().tolist())
            except:
                carrier_list = ["(General / Unknown)"]

            origin = st.selectbox("Origin City", origins, index=0, key="est_origin")
            destination = st.selectbox("Destination City", destinations, index=1, key="est_dest")
            
            # Carrier selection
            carrier_name = st.selectbox("Carrier (Optional)", carrier_list, key="est_carrier")
            actual_carrier = carrier_name if carrier_name != "(General / Unknown)" else ""

            distance_km = st.number_input("Distance (km)", min_value=10.0, max_value=5000.0, value=500.0, step=50.0)
            weight_tonnes = st.number_input("Cargo Weight (tonnes)", min_value=0.5, max_value=50.0, value=10.0, step=0.5)
            fuel_type = st.selectbox("Fuel Type", get_all_fuel_types(), key="est_fuel")
            vehicle_type = st.selectbox("Vehicle Type", get_all_vehicle_types(), key="est_vehicle")
            load_factor = st.slider("Load Factor", min_value=0.1, max_value=1.0, value=0.8, step=0.05)

            estimate_btn = st.button("Estimate Emissions", use_container_width=True, type="primary")

        with col_result:
            st.markdown("#### Estimation Result")
            if estimate_btn:
                co2e = estimate_emissions(distance_km, weight_tonnes, fuel_type, vehicle_type, load_factor, carrier_name=actual_carrier)
                fleet_avg = df["co2e_kg"].mean()

                # Result card
                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom: 16px;">
                    <div class="kpi-label">Estimated CO₂e</div>
                    <div class="kpi-value">{co2e:,.2f} kg</div>
                    <div class="kpi-sublabel">{co2e/1000:,.3f} tonnes</div>
                </div>
                """, unsafe_allow_html=True)

                # Formula breakdown
                from app.predictor import get_emission_factor
                ef = get_emission_factor(fuel_type, vehicle_type)
                st.markdown("##### Formula Breakdown")
                st.code(
                    f"CO₂e = {distance_km} km × {weight_tonnes} t × {ef} (EF) × {load_factor} (LF)\n"
                    f"CO₂e = {co2e:,.2f} kg",
                    language="text",
                )

                # Gauge chart vs fleet average
                st.markdown("##### vs Fleet Average")
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=co2e,
                    delta={"reference": fleet_avg, "relative": True, "valueformat": ".1%"},
                    gauge={
                        "axis": {"range": [0, max(co2e * 2, fleet_avg * 2)]},
                        "bar": {"color": "#3a7bd5"},
                        "steps": [
                            {"range": [0, fleet_avg * 0.7], "color": "rgba(52, 232, 158, 0.2)"},
                            {"range": [fleet_avg * 0.7, fleet_avg * 1.3], "color": "rgba(255, 217, 61, 0.2)"},
                            {"range": [fleet_avg * 1.3, max(co2e * 2, fleet_avg * 2)], "color": "rgba(255, 107, 107, 0.2)"},
                        ],
                        "threshold": {
                            "line": {"color": "white", "width": 2},
                            "thickness": 0.75,
                            "value": fleet_avg,
                        },
                    },
                    number={"suffix": " kg", "font": {"size": 28}},
                    title={"text": f"Fleet Avg: {fleet_avg:,.1f} kg", "font": {"size": 14}},
                ))
                fig_gauge.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=260,
                    margin=dict(l=20, r=20, t=40, b=20),
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
            else:
                st.info("Fill in the shipment details and click Estimate Emissions to see the result.")


    # ══════════════════════════════════════════════════════════════════════════════
    # PAGE 3: Lane Analytics
    # ══════════════════════════════════════════════════════════════════════════════
    elif page == "Analytics":
        st.markdown('<div class="page-header">Lane Analytics</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subtitle">Identify high-emission lanes and optimize route efficiency</div>', unsafe_allow_html=True)

        lane_df = lane_risk_classification(df)

        # Risk summary
        c1, c2, c3 = st.columns(3)
        high_count = len(lane_df[lane_df["risk"] == "High"])
        med_count = len(lane_df[lane_df["risk"] == "Medium"])
        low_count = len(lane_df[lane_df["risk"] == "Low"])

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-label">High Risk Lanes</div>
                <div class="kpi-value" style="background: linear-gradient(90deg, #ff6b6b, #ee5a24); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{high_count}</div>
                <div class="kpi-sublabel">Immediate attention needed</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Medium Risk Lanes</div>
                <div class="kpi-value" style="background: linear-gradient(90deg, #ffd93d, #f0932b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{med_count}</div>
                <div class="kpi-sublabel">Monitor & optimize</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Low Risk Lanes</div>
                <div class="kpi-value" style="background: linear-gradient(90deg, #34e89e, #0f9b0f); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{low_count}</div>
                <div class="kpi-sublabel">Performing well</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([6, 4], gap="large")

        with col_left:
            st.markdown("#### Lane Emission Intensity vs Volume")
            fig_scatter = px.scatter(
                lane_df,
                x="shipment_count",
                y="intensity",
                size="total_co2e",
                color="risk",
                color_discrete_map={"High": "#ff6b6b", "Medium": "#ffd93d", "Low": "#34e89e"},
                hover_data=["lane", "total_co2e", "avg_load_factor"],
                labels={
                    "shipment_count": "Shipment Volume",
                    "intensity": "Emission Intensity (kg CO₂e / km)",
                    "total_co2e": "Total CO₂e (kg)",
                    "risk": "Risk Level",
                },
            )
            fig_scatter.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col_right:
            st.markdown("#### Risk Distribution")
            risk_counts = lane_df["risk"].value_counts().reset_index()
            risk_counts.columns = ["risk", "count"]
            fig_risk = px.pie(
                risk_counts,
                values="count",
                names="risk",
                color="risk",
                color_discrete_map={"High": "#ff6b6b", "Medium": "#ffd93d", "Low": "#34e89e"},
                hole=0.5,
            )
            fig_risk.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                height=300,
                margin=dict(l=0, r=0, t=10, b=10),
            )
            fig_risk.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_risk, use_container_width=True)

        # Lane table
        st.markdown("#### Detailed Lane Data")

        display_df = lane_df[["lane", "risk", "total_co2e", "total_distance", "shipment_count", "avg_load_factor", "intensity"]].copy()
        display_df.columns = ["Lane", "Risk", "Total CO₂e (kg)", "Total Distance (km)", "Shipments", "Avg Load Factor", "Intensity"]
        display_df["Total CO₂e (kg)"] = display_df["Total CO₂e (kg)"].round(1)
        display_df["Total Distance (km)"] = display_df["Total Distance (km)"].round(1)
        display_df["Avg Load Factor"] = display_df["Avg Load Factor"].round(2)
        display_df["Intensity"] = display_df["Intensity"].round(4)

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Risk": st.column_config.TextColumn("Risk", help="Emission intensity risk level"),
                "Total CO₂e (kg)": st.column_config.NumberColumn(format="%.1f"),
                "Intensity": st.column_config.NumberColumn(format="%.4f"),
            },
        )


    # ══════════════════════════════════════════════════════════════════════════════
    # PAGE 4: What-If Simulator
    # ══════════════════════════════════════════════════════════════════════════════
    elif page == "Simulator":
        st.markdown('<div class="page-header">What-If Scenario Simulator</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subtitle">Explore emission reduction strategies for your fleet</div>', unsafe_allow_html=True)

        col_sliders, col_results = st.columns([1, 2])

        with col_sliders:
            st.markdown("#### Scenario Levers")

            ev_pct = st.slider("Diesel to EV Switch (%)", 0, 100, 30, 5, key="sim_ev")
            cng_pct = st.slider("Diesel to CNG Switch (%)", 0, 100, 15, 5, key="sim_cng")
            load_imp = st.slider("Load Consolidation (pp)", 0, 30, 10, 1, key="sim_load")
            reroute_pct = st.slider("Route Optimization (%)", 0, 30, 10, 1, key="sim_reroute")

            st.markdown("---")
            run_btn = st.button("Run Scenario", use_container_width=True, type="primary")

        with col_results:
            if run_btn:
                scenario = run_combined_scenario(
                    df,
                    ev_pct=ev_pct,
                    cng_pct=cng_pct,
                    load_improvement=load_imp,
                    rerouting_pct=reroute_pct,
                )
                total = scenario["total"]

                # Summary cards
                st.markdown(f"""
                <div class="kpi-container">
                    <div class="kpi-card">
                        <div class="kpi-label">Baseline Emissions</div>
                        <div class="kpi-value">{total['before_co2e']:,.0f} kg</div>
                        <div class="kpi-sublabel">Current fleet total</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Projected Emissions</div>
                        <div class="kpi-value" style="background: linear-gradient(90deg, #34e89e, #0f9b0f); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{total['after_co2e']:,.0f} kg</div>
                        <div class="kpi-sublabel">After scenario changes</div>
                    </div>
                    <div class="savings-card">
                        <div class="kpi-label" style="color: #34e89e;">Total Reduction</div>
                        <div class="savings-value">-{total['savings_pct']}%</div>
                        <div class="kpi-sublabel" style="color: #8892b0;">{total['savings_co2e']:,.0f} kg CO₂e saved</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Waterfall chart
                if scenario["levers"]:
                    st.markdown("#### Savings Breakdown by Lever")

                    labels = [l["label"] for l in scenario["levers"]]
                    values = [l["savings_co2e"] for l in scenario["levers"]]
                    pcts = [l["savings_pct"] for l in scenario["levers"]]

                    fig_waterfall = go.Figure()

                    # Individual lever bars
                    colors = ["#3a7bd5", "#34e89e", "#ffd93d", "#ff6b6b"]
                    for i, (label, val, pct) in enumerate(zip(labels, values, pcts)):
                        fig_waterfall.add_trace(go.Bar(
                            x=[label],
                            y=[val],
                            name=label,
                            marker_color=colors[i % len(colors)],
                            text=f"{val:,.0f} kg<br>({pct}%)",
                            textposition="outside",
                        ))

                    # Total bar
                    fig_waterfall.add_trace(go.Bar(
                        x=["Combined Total"],
                        y=[total["savings_co2e"]],
                        name="Combined",
                        marker_color="#00d2ff",
                        text=f"{total['savings_co2e']:,.0f} kg<br>({total['savings_pct']}%)",
                        textposition="outside",
                    ))

                fig_waterfall.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    height=400,
                    margin=dict(l=20, r=20, t=30, b=20),
                    yaxis_title="CO₂e Saved (kg)",
                )
                st.plotly_chart(fig_waterfall, use_container_width=True)

                # Before vs After comparison
                st.markdown("#### Before vs After")
                fig_compare = go.Figure()
                fig_compare.add_trace(go.Bar(
                    x=["Before", "After"],
                    y=[total["before_co2e"], total["after_co2e"]],
                    marker_color=["#ff6b6b", "#34e89e"],
                    text=[f"{total['before_co2e']:,.0f} kg", f"{total['after_co2e']:,.0f} kg"],
                    textposition="outside",
                    width=0.5,
                ))
                fig_compare.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    height=350,
                    margin=dict(l=20, r=20, t=20, b=20),
                    yaxis_title="Total CO₂e (kg)",
                )
                st.plotly_chart(fig_compare, use_container_width=True)

                # AI Narrative
                if ai_is_available():
                    with st.spinner("Generating scenario analysis..."):
                        narrative = generate_scenario_narrative(scenario)
                    st.markdown(f"""
                    <div class="ai-card">
                        <h4>AI Scenario Analysis</h4>
                        <p>{narrative}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # --- NEW SECTION: Strategic Recommendations ---
                st.markdown("---")
                st.markdown("#### 🎯 Smart Optimization Engine")
                st.markdown("<p style='font-size: 13px; color: #8b949e;'>Based on your fleet profile, we predicted additional high-impact actions:</p>", unsafe_allow_html=True)
                
                # Compute some "Next Best Steps"
                # 1. full EV switch (100% of remaining diesel)
                full_ev = simulate_ev_switch(df, 100)
                full_cons = simulate_load_improvement(df, 30) # Max 100% load
                
                rec_col1, rec_col2 = st.columns(2)
                with rec_col1:
                    st.markdown(f"""
                    <div style="background: rgba(88, 166, 255, 0.05); border: 1px dashed rgba(88, 166, 255, 0.3); border-radius: 10px; padding: 16px;">
                        <div style="font-size: 11px; color: #58a6ff; font-weight: 700; text-transform: uppercase;">Next-Best Technology</div>
                        <div style="font-size: 16px; font-weight: 600; margin: 8px 0;">100% EV Transition</div>
                        <div style="font-size: 12px; color: #c9d1d9;">Predicted impact: <span style="color: #3fb950; font-weight: 700;">-{full_ev['savings_pct']}% CO₂e</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with rec_col2:
                    st.markdown(f"""
                    <div style="background: rgba(63, 185, 80, 0.05); border: 1px dashed rgba(63, 185, 80, 0.3); border-radius: 10px; padding: 16px;">
                        <div style="font-size: 11px; color: #3fb950; font-weight: 700; text-transform: uppercase;">Next-Best Efficiency</div>
                        <div style="font-size: 16px; font-weight: 600; margin: 8px 0;">Max Load Consolidation</div>
                        <div style="font-size: 12px; color: #c9d1d9;">Predicted impact: <span style="color: #3fb950; font-weight: 700;">-{full_cons['savings_pct']}% CO₂e</span></div>
                    </div>
                    """, unsafe_allow_html=True)

            else:
                st.info("Adjust the scenario levers and click 'Run Scenario' to see projected emission reductions and strategic recommendations.")

# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# AI ASSISTANT PANEL (RIGHT COLUMN)
# ══════════════════════════════════════════════════════════════════════════════
with ai_col:
    st.markdown("""
    <div class="ai-console-header">
        <h3>CarbonIQ Assistant</h3>
        <p>Powered by HuggingFace Qwen</p>
    </div>
    """, unsafe_allow_html=True)
    
    # History container - we use st.container with height to allow internal scrolling 
    # while the column itself stays sticky to the viewport.
    chat_container = st.container(height=600, border=False)

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Fixed Chat input handled by CSS (pinned to bottom-right)
    if not ai_is_available():
        st.warning("[Notice] AI Assistant disabled.")
    else:
        if prompt := st.chat_input("Ask CarbonIQ..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Immediately display user message
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Show Thinking state
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = ask_carbon_agent(f"{prompt}", df)
                        st.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
