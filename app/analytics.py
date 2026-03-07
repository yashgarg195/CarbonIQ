"""Analytics functions for CarbonIQ — KPIs, lane analysis, and trends."""

import pandas as pd
import streamlit as st


@st.cache_data
def summary_kpis(df: pd.DataFrame) -> dict:
    """
    Compute fleet-wide KPI summary.

    Returns dict with: total_co2e, shipment_count, avg_per_shipment,
    worst_lane, best_lane, diesel_share.
    """
    total_co2e = round(df["co2e_kg"].sum(), 2)
    shipment_count = len(df)
    avg_per_shipment = round(total_co2e / shipment_count, 2) if shipment_count else 0

    # Lane analysis
    lanes = (
        df.groupby(["origin", "destination"])["co2e_kg"]
        .sum()
        .reset_index()
        .sort_values("co2e_kg", ascending=False)
    )
    worst_lane = (
        f"{lanes.iloc[0]['origin']} → {lanes.iloc[0]['destination']}"
        if len(lanes) > 0 else "N/A"
    )
    best_lane = (
        f"{lanes.iloc[-1]['origin']} → {lanes.iloc[-1]['destination']}"
        if len(lanes) > 0 else "N/A"
    )

    diesel_count = len(df[df["fuel_type"] == "Diesel"])
    diesel_share = round(diesel_count / shipment_count * 100, 1) if shipment_count else 0

    return {
        "total_co2e": total_co2e,
        "shipment_count": shipment_count,
        "avg_per_shipment": avg_per_shipment,
        "worst_lane": worst_lane,
        "best_lane": best_lane,
        "diesel_share": diesel_share,
    }


@st.cache_data
def top_emission_lanes(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Return top-N origin→destination pairs by total CO₂e.

    Returns DataFrame with columns: origin, destination, co2e_kg,
    shipment_count, avg_distance_km, avg_weight_tonnes.
    """
    lanes = (
        df.groupby(["origin", "destination"])
        .agg(
            co2e_kg=("co2e_kg", "sum"),
            shipment_count=("shipment_id", "count"),
            avg_distance_km=("distance_km", "mean"),
            avg_weight_tonnes=("weight_tonnes", "mean"),
        )
        .reset_index()
        .sort_values("co2e_kg", ascending=False)
        .head(n)
    )
    lanes["co2e_kg"] = lanes["co2e_kg"].round(2)
    lanes["avg_distance_km"] = lanes["avg_distance_km"].round(1)
    lanes["avg_weight_tonnes"] = lanes["avg_weight_tonnes"].round(1)
    lanes["lane"] = lanes["origin"] + " → " + lanes["destination"]
    return lanes


@st.cache_data
def emission_trend(df: pd.DataFrame, freq: str = "ME") -> pd.DataFrame:
    """
    Compute emission totals over time, grouped by fuel type.

    Args:
        df: Shipment DataFrame with 'date', 'co2e_kg', and 'fuel_type' columns.
        freq: Pandas frequency alias ('W' for weekly, 'ME' for month-end).

    Returns:
        DataFrame with columns: date, fuel_type, co2e_kg.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    trend = (
        df.groupby([pd.Grouper(key="date", freq=freq), "fuel_type"])["co2e_kg"]
        .sum()
        .reset_index()
    )
    trend["co2e_kg"] = trend["co2e_kg"].round(2)
    return trend


@st.cache_data
def lane_risk_classification(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify lanes as High / Medium / Low emission intensity.

    Intensity = total CO₂e / total distance across all shipments on that lane.
    """
    lanes = (
        df.groupby(["origin", "destination"])
        .agg(
            total_co2e=("co2e_kg", "sum"),
            total_distance=("distance_km", "sum"),
            shipment_count=("shipment_id", "count"),
            avg_load_factor=("load_factor", "mean"),
        )
        .reset_index()
    )
    lanes["intensity"] = (lanes["total_co2e"] / lanes["total_distance"]).round(4)
    lanes["lane"] = lanes["origin"] + " → " + lanes["destination"]

    # Classify based on intensity percentiles
    q33 = lanes["intensity"].quantile(0.33)
    q66 = lanes["intensity"].quantile(0.66)
    lanes["risk"] = lanes["intensity"].apply(
        lambda x: "High" if x >= q66 else ("Medium" if x >= q33 else "Low")
    )
    return lanes.sort_values("intensity", ascending=False)



@st.cache_data
def carrier_efficiency_leaderboard(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Return top-N carriers by emission efficiency.
    Efficiency = sum(co2e_kg) / sum(weight * distance)
    """
    if 'carrier_name' not in df.columns:
        return pd.DataFrame()

    df_c = df.copy()
    df_c["_tkm"] = df_c["distance_km"] * df_c["weight_tonnes"]

    carriers = (
        df_c.groupby("carrier_name")
        .agg(
            total_co2e=("co2e_kg", "sum"),
            total_tkm=("_tkm", "sum"),
            shipment_count=("shipment_id", "count")
        )
        .reset_index()
    )
    # Filter tiny carriers to avoid outliers
    carriers = carriers[carriers['shipment_count'] > 0]
    carriers["ef_kg_per_tkm"] = (carriers["total_co2e"] / carriers["total_tkm"]).round(4)
    return carriers.sort_values("ef_kg_per_tkm").head(n)

