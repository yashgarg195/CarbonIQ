"""What-If scenario simulator for CarbonIQ."""

import pandas as pd
from app.predictor import estimate_emissions


# ── Helpers ───────────────────────────────────────────────────────────────────

def _recalc_emissions(df: pd.DataFrame) -> pd.DataFrame:
    """Recalculate co2e_kg for every row after mutations."""
    df["co2e_kg"] = df.apply(
        lambda r: estimate_emissions(
            r["distance_km"], r["weight_tonnes"],
            r["fuel_type"], r["vehicle_type"],
            r["load_factor"],
            carrier_name=r.get("carrier_name", "")
        ),
        axis=1,
    )
    return df


def _savings(label: str, df_orig: pd.DataFrame, df_new: pd.DataFrame) -> dict:
    """Compute before / after / savings dict."""
    before = round(df_orig["co2e_kg"].sum(), 2)
    after = round(df_new["co2e_kg"].sum(), 2)
    saved = round(before - after, 2)
    pct = round(saved / before * 100, 1) if before > 0 else 0
    return {
        "label": label,
        "before_co2e": before,
        "after_co2e": after,
        "savings_co2e": saved,
        "savings_pct": pct,
    }


# ── Individual Scenario Levers ────────────────────────────────────────────────

def _simulate_fuel_switch(df: pd.DataFrame, pct_switch: float, target_fuel: str) -> dict:
    """Switch a % of Diesel fleet to *target_fuel* (EV or CNG)."""
    df_sim = df.copy()
    diesel_mask = df_sim["fuel_type"] == "Diesel"
    n_switch = int(diesel_mask.sum() * pct_switch / 100)

    if n_switch > 0:
        switch_idx = df_sim[diesel_mask].sample(n=n_switch, random_state=42).index
        df_sim.loc[switch_idx, "fuel_type"] = target_fuel
        df_sim = _recalc_emissions(df_sim)

    return _savings(f"{target_fuel} Switch ({pct_switch}%)", df, df_sim)


def simulate_ev_switch(df: pd.DataFrame, pct_switch: float) -> dict:
    """Simulate switching a percentage of Diesel fleet to EV."""
    return _simulate_fuel_switch(df, pct_switch, "EV")


def simulate_cng_switch(df: pd.DataFrame, pct_switch: float) -> dict:
    """Simulate switching a percentage of Diesel fleet to CNG."""
    return _simulate_fuel_switch(df, pct_switch, "CNG")


def simulate_load_improvement(df: pd.DataFrame, pct_improvement: float) -> dict:
    """Simulate improving load factor across the fleet."""
    df_sim = df.copy()
    df_sim["load_factor"] = (df_sim["load_factor"] + pct_improvement / 100).clip(upper=1.0)
    df_sim = _recalc_emissions(df_sim)
    return _savings(f"Load Consolidation (+{pct_improvement}pp)", df, df_sim)


def simulate_rerouting(df: pd.DataFrame, pct_reduction: float) -> dict:
    """Simulate rerouting to shorter distances."""
    df_sim = df.copy()
    df_sim["distance_km"] = (df_sim["distance_km"] * (1 - pct_reduction / 100)).round(1)
    df_sim = _recalc_emissions(df_sim)
    return _savings(f"Rerouting (-{pct_reduction}% dist)", df, df_sim)


# ── Combined Scenario ─────────────────────────────────────────────────────────

def run_combined_scenario(
    df: pd.DataFrame,
    ev_pct: float = 0,
    cng_pct: float = 0,
    load_improvement: float = 0,
    rerouting_pct: float = 0,
) -> dict:
    """Run all levers combined and return individual + total savings."""
    # Individual lever results
    levers = []
    if ev_pct > 0:
        levers.append(simulate_ev_switch(df, ev_pct))
    if cng_pct > 0:
        levers.append(simulate_cng_switch(df, cng_pct))
    if load_improvement > 0:
        levers.append(simulate_load_improvement(df, load_improvement))
    if rerouting_pct > 0:
        levers.append(simulate_rerouting(df, rerouting_pct))

    # Combined simulation
    df_combined = df.copy()

    if ev_pct > 0:
        diesel = df_combined["fuel_type"] == "Diesel"
        n = int(diesel.sum() * ev_pct / 100)
        if n > 0:
            df_combined.loc[df_combined[diesel].sample(n=n, random_state=42).index, "fuel_type"] = "EV"

    if cng_pct > 0:
        diesel = df_combined["fuel_type"] == "Diesel"
        n = int(diesel.sum() * cng_pct / 100)
        if n > 0:
            df_combined.loc[df_combined[diesel].sample(n=n, random_state=42).index, "fuel_type"] = "CNG"

    if load_improvement > 0:
        df_combined["load_factor"] = (df_combined["load_factor"] + load_improvement / 100).clip(upper=1.0)

    if rerouting_pct > 0:
        df_combined["distance_km"] = (df_combined["distance_km"] * (1 - rerouting_pct / 100)).round(1)

    df_combined = _recalc_emissions(df_combined)

    total = _savings("Combined Scenario", df, df_combined)
    return {"levers": levers, "total": total}
