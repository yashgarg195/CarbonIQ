"""What-If scenario simulator for CarbonIQ."""

import pandas as pd
from app.predictor import get_emission_factor


def simulate_ev_switch(df: pd.DataFrame, pct_switch: float) -> dict:
    """
    Simulate switching a percentage of Diesel fleet to EV.

    Args:
        df: Shipment DataFrame.
        pct_switch: Percentage of Diesel shipments to switch (0-100).

    Returns:
        Dict with before_co2e, after_co2e, savings_co2e, savings_pct, label.
    """
    df_sim = df.copy()
    diesel_mask = df_sim["fuel_type"] == "Diesel"
    n_switch = int(diesel_mask.sum() * pct_switch / 100)

    if n_switch > 0:
        switch_idx = df_sim[diesel_mask].sample(n=n_switch, random_state=42).index
        for idx in switch_idx:
            vtype = df_sim.loc[idx, "vehicle_type"]
            ef_ev = get_emission_factor("EV", vtype)
            df_sim.loc[idx, "fuel_type"] = "EV"
            df_sim.loc[idx, "co2e_kg"] = round(
                df_sim.loc[idx, "distance_km"]
                * df_sim.loc[idx, "weight_tonnes"]
                * ef_ev
                * df_sim.loc[idx, "load_factor"],
                2,
            )

    before = round(df["co2e_kg"].sum(), 2)
    after = round(df_sim["co2e_kg"].sum(), 2)
    savings = round(before - after, 2)
    pct = round(savings / before * 100, 1) if before > 0 else 0

    return {
        "label": f"EV Switch ({pct_switch}%)",
        "before_co2e": before,
        "after_co2e": after,
        "savings_co2e": savings,
        "savings_pct": pct,
    }


def simulate_cng_switch(df: pd.DataFrame, pct_switch: float) -> dict:
    """
    Simulate switching a percentage of Diesel fleet to CNG.
    """
    df_sim = df.copy()
    diesel_mask = df_sim["fuel_type"] == "Diesel"
    n_switch = int(diesel_mask.sum() * pct_switch / 100)

    if n_switch > 0:
        switch_idx = df_sim[diesel_mask].sample(n=n_switch, random_state=42).index
        for idx in switch_idx:
            vtype = df_sim.loc[idx, "vehicle_type"]
            ef_cng = get_emission_factor("CNG", vtype)
            df_sim.loc[idx, "fuel_type"] = "CNG"
            df_sim.loc[idx, "co2e_kg"] = round(
                df_sim.loc[idx, "distance_km"]
                * df_sim.loc[idx, "weight_tonnes"]
                * ef_cng
                * df_sim.loc[idx, "load_factor"],
                2,
            )

    before = round(df["co2e_kg"].sum(), 2)
    after = round(df_sim["co2e_kg"].sum(), 2)
    savings = round(before - after, 2)
    pct = round(savings / before * 100, 1) if before > 0 else 0

    return {
        "label": f"CNG Switch ({pct_switch}%)",
        "before_co2e": before,
        "after_co2e": after,
        "savings_co2e": savings,
        "savings_pct": pct,
    }


def simulate_load_improvement(df: pd.DataFrame, pct_improvement: float) -> dict:
    """
    Simulate improving load factor across the fleet.

    Args:
        pct_improvement: Percentage points to add to load factor (0-30).
    """
    df_sim = df.copy()
    improvement = pct_improvement / 100
    df_sim["load_factor"] = (df_sim["load_factor"] + improvement).clip(upper=1.0)

    # Recalculate CO₂e
    df_sim["co2e_kg"] = df_sim.apply(
        lambda r: round(
            r["distance_km"] * r["weight_tonnes"]
            * get_emission_factor(r["fuel_type"], r["vehicle_type"])
            * r["load_factor"], 2
        ),
        axis=1,
    )

    before = round(df["co2e_kg"].sum(), 2)
    after = round(df_sim["co2e_kg"].sum(), 2)
    savings = round(before - after, 2)
    pct = round(savings / before * 100, 1) if before > 0 else 0

    return {
        "label": f"Load Consolidation (+{pct_improvement}pp)",
        "before_co2e": before,
        "after_co2e": after,
        "savings_co2e": savings,
        "savings_pct": pct,
    }


def simulate_rerouting(df: pd.DataFrame, pct_reduction: float) -> dict:
    """
    Simulate rerouting to shorter distances.

    Args:
        pct_reduction: Percentage reduction in distance (0-30).
    """
    df_sim = df.copy()
    factor = 1 - pct_reduction / 100
    df_sim["distance_km"] = (df_sim["distance_km"] * factor).round(1)

    # Recalculate CO₂e
    df_sim["co2e_kg"] = df_sim.apply(
        lambda r: round(
            r["distance_km"] * r["weight_tonnes"]
            * get_emission_factor(r["fuel_type"], r["vehicle_type"])
            * r["load_factor"], 2
        ),
        axis=1,
    )

    before = round(df["co2e_kg"].sum(), 2)
    after = round(df_sim["co2e_kg"].sum(), 2)
    savings = round(before - after, 2)
    pct = round(savings / before * 100, 1) if before > 0 else 0

    return {
        "label": f"Rerouting (-{pct_reduction}% dist)",
        "before_co2e": before,
        "after_co2e": after,
        "savings_co2e": savings,
        "savings_pct": pct,
    }


def run_combined_scenario(
    df: pd.DataFrame,
    ev_pct: float = 0,
    cng_pct: float = 0,
    load_improvement: float = 0,
    rerouting_pct: float = 0,
) -> dict:
    """
    Run all levers combined and return individual + total savings.

    Returns dict with 'levers' (list of individual results) and 'total'.
    """
    levers = []
    before = round(df["co2e_kg"].sum(), 2)

    if ev_pct > 0:
        levers.append(simulate_ev_switch(df, ev_pct))
    if cng_pct > 0:
        levers.append(simulate_cng_switch(df, cng_pct))
    if load_improvement > 0:
        levers.append(simulate_load_improvement(df, load_improvement))
    if rerouting_pct > 0:
        levers.append(simulate_rerouting(df, rerouting_pct))

    # Combined effect (apply all levers sequentially)
    df_combined = df.copy()

    # EV switch
    if ev_pct > 0:
        diesel_mask = df_combined["fuel_type"] == "Diesel"
        n_switch = int(diesel_mask.sum() * ev_pct / 100)
        if n_switch > 0:
            switch_idx = df_combined[diesel_mask].sample(n=n_switch, random_state=42).index
            df_combined.loc[switch_idx, "fuel_type"] = "EV"

    # CNG switch (from remaining Diesel)
    if cng_pct > 0:
        diesel_mask = df_combined["fuel_type"] == "Diesel"
        n_switch = int(diesel_mask.sum() * cng_pct / 100)
        if n_switch > 0:
            switch_idx = df_combined[diesel_mask].sample(n=n_switch, random_state=42).index
            df_combined.loc[switch_idx, "fuel_type"] = "CNG"

    # Load improvement
    if load_improvement > 0:
        df_combined["load_factor"] = (
            df_combined["load_factor"] + load_improvement / 100
        ).clip(upper=1.0)

    # Rerouting
    if rerouting_pct > 0:
        df_combined["distance_km"] = (
            df_combined["distance_km"] * (1 - rerouting_pct / 100)
        ).round(1)

    # Recalculate all CO₂e
    df_combined["co2e_kg"] = df_combined.apply(
        lambda r: round(
            r["distance_km"] * r["weight_tonnes"]
            * get_emission_factor(r["fuel_type"], r["vehicle_type"])
            * r["load_factor"], 2
        ),
        axis=1,
    )

    after = round(df_combined["co2e_kg"].sum(), 2)
    total_savings = round(before - after, 2)
    total_pct = round(total_savings / before * 100, 1) if before > 0 else 0

    return {
        "levers": levers,
        "total": {
            "label": "Combined Scenario",
            "before_co2e": before,
            "after_co2e": after,
            "savings_co2e": total_savings,
            "savings_pct": total_pct,
        },
    }
