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
)
from app.simulator import run_combined_scenario
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    /* Global Typography */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #0f111a;
    }

    /* Professional Sidebar Ribbon */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
        padding-top: 1rem;
    }
    
    /* Layout structural spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 100% !important;
    }

    /* Fixed Right AI Console Pane */
    /* Updated selector: Use nth-child(2) to target the second column in the horizontal alignment block */
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
        position: fixed !important;
        right: 0 !important;
        top: 0 !important;
        width: 350px !important;
        height: 100vh !important;
        background-color: #161b22 !important;
        border-left: 1px solid #30363d !important;
        padding: 60px 24px 80px 24px !important;
        z-index: 100 !important;
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
        z-index: 101 !important;
        left: auto !important;
    }

    /* AI Header styling to prevent vertical text */
    .ai-console-header h3 {
        white-space: nowrap !important;
    }

    /* Adjust main content container */
    .block-container {
        max-width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }
    
    /* Sidebar Navigation Buttons */
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
        border: none;
    }
    section[data-testid="stSidebar"] .stButton > button:active,
    section[data-testid="stSidebar"] .stButton > button:focus {
        background-color: #1f6feb;
        color: #ffffff;
    }

    /* KPI Cards - Enterprise Style */
    .kpi-container {
        display: flex;
        gap: 24px;
        margin-bottom: 24px;
        flex-wrap: wrap;
    }
    .kpi-card {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        text-align: left;
        min-width: 150px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 600;
        color: #ffffff;
        margin: 4px 0 2px 0;
    }
    .kpi-label {
        font-size: 12px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    .kpi-sublabel {
        font-size: 11px;
        color: #8b949e;
    }

    /* AI Insight Card - Professional Status Box */
    .ai-card {
        background-color: #161b22;
        border: 1px solid #238636;
        border-left: 4px solid #238636;
        border-radius: 6px;
        padding: 16px 20px;
        margin: 24px 0;
    }
    .ai-card h4 {
        color: #ffffff;
        margin: 0 0 8px 0;
        font-size: 14px;
        font-weight: 600;
    }
    .ai-card p {
        color: #c9d1d9;
        font-size: 14px;
        line-height: 1.5;
        margin: 0;
    }

    /* Savings card */
    .savings-card {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        text-align: left;
        min-width: 150px;
    }
    .savings-value {
        font-size: 28px;
        font-weight: 600;
        color: #3fb950;
        margin: 4px 0 2px 0;
    }

    /* Page headers */
    .page-header {
        font-size: 20px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .page-subtitle {
        font-size: 13px;
        color: #8b949e;
        margin-bottom: 24px;
    }
    
    /* Standard headers inside columns */
    h4 {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        margin-bottom: 12px !important;
        margin-top: 16px !important;
    }

    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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
            fig_trend.update_yaxes(showgrid=True, gridcolor="#30363d")
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_right:
            st.markdown("#### Top 10 High-Emission Lanes")
            fig_lanes = px.bar(
                top_lanes,
                x="lane",
                y="co2e_kg",
                color="co2e_kg",
                color_continuous_scale=["#34e89e", "#ffd93d", "#ff6b6b"],
                labels={"co2e_kg": "CO₂e (kg)", "lane": "Lane"},
                text="co2e_kg",
            )
            fig_lanes.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=40),
                showlegend=False,
                height=260,
                xaxis_tickangle=-35,
                coloraxis_showscale=False,
            )
            fig_lanes.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_lanes, use_container_width=True)


    # ══════════════════════════════════════════════════════════════════════════════
    # PAGE 2: Shipment Estimator
    # ══════════════════════════════════════════════════════════════════════════════
    elif page == "Estimator":
        st.markdown('<div class="page-header">Shipment Emission Estimator</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subtitle">Estimate CO₂e for a single shipment using the GLEC Framework formula</div>', unsafe_allow_html=True)

        col_form, col_result = st.columns([1, 1])

        with col_form:
            st.markdown("#### Enter Shipment Details")

            origins = sorted(df["origin"].unique().tolist())
            destinations = sorted(df["destination"].unique().tolist())

            origin = st.selectbox("Origin City", origins, index=0, key="est_origin")
            destination = st.selectbox("Destination City", destinations, index=1, key="est_dest")
            distance_km = st.number_input("Distance (km)", min_value=10.0, max_value=5000.0, value=500.0, step=50.0)
            weight_tonnes = st.number_input("Cargo Weight (tonnes)", min_value=0.5, max_value=50.0, value=10.0, step=0.5)
            fuel_type = st.selectbox("Fuel Type", get_all_fuel_types(), key="est_fuel")
            vehicle_type = st.selectbox("Vehicle Type", get_all_vehicle_types(), key="est_vehicle")
            load_factor = st.slider("Load Factor", min_value=0.1, max_value=1.0, value=0.8, step=0.05)

            estimate_btn = st.button("Estimate Emissions", use_container_width=True, type="primary")

        with col_result:
            st.markdown("#### Estimation Result")
            if estimate_btn:
                co2e = estimate_emissions(distance_km, weight_tonnes, fuel_type, vehicle_type, load_factor)
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
            if run_btn or any([ev_pct, cng_pct, load_imp, reroute_pct]):
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
            else:
                st.info("Adjust the scenario levers and click Run Scenario to see projected emission reductions.")

# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# AI ASSISTANT PANEL (RIGHT COLUMN)
# ══════════════════════════════════════════════════════════════════════════════
with ai_col:
    st.markdown("""
    <div class="ai-console-header" style="padding-bottom: 10px; border-bottom: 1px solid #30363d; margin-bottom: 16px;">
        <h3 style="margin:0; font-size:16px; font-weight:600; color:#58a6ff;">🤖 CarbonIQ Assistant</h3>
        <p style="margin:0; font-size:12px; color:#8b949e;">Powered by HuggingFace Qwen</p>
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
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = ask_carbon_agent(f"{prompt}", df)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
