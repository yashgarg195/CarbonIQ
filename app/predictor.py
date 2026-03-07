"""GLEC Framework emission estimator for road freight."""

import os
import pandas as pd

# ── Load emission factors once ────────────────────────────────────────────────
_EF_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "emission_factors.csv")
_ef_df = pd.read_csv(_EF_PATH)
_EF_LOOKUP = {
    (row.fuel_type, row.vehicle_type): row.ef_kg_co2e_per_tkm
    for _, row in _ef_df.iterrows()
}

# Default emission factor (Diesel 20FT) as fallback
_DEFAULT_EF = 0.089


def estimate_emissions(
    distance_km: float,
    weight_tonnes: float,
    fuel_type: str,
    vehicle_type: str,
    load_factor: float = 1.0,
) -> float:
    """
    Estimate CO₂e emissions using the GLEC Framework formula.

    CO₂e (kg) = distance_km × weight_tonnes × emission_factor × load_factor

    Returns:
        CO₂e in kg (rounded to 2 decimal places).
    """
    ef = _EF_LOOKUP.get((fuel_type, vehicle_type), _DEFAULT_EF)
    co2e = distance_km * weight_tonnes * ef * load_factor
    return round(co2e, 2)


def predict_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a `co2e_kg` column to the DataFrame using the GLEC formula.

    Expects columns: distance_km, weight_tonnes, fuel_type, vehicle_type, load_factor.
    """
    df = df.copy()
    df["co2e_kg"] = df.apply(
        lambda r: estimate_emissions(
            r["distance_km"], r["weight_tonnes"],
            r["fuel_type"], r["vehicle_type"],
            r.get("load_factor", 1.0),
        ),
        axis=1,
    )
    return df


def get_emission_factor(fuel_type: str, vehicle_type: str) -> float:
    """Return the emission factor for a given fuel/vehicle combination."""
    return _EF_LOOKUP.get((fuel_type, vehicle_type), _DEFAULT_EF)


def get_all_fuel_types() -> list:
    """Return all available fuel types."""
    return sorted(_ef_df["fuel_type"].unique().tolist())


def get_all_vehicle_types() -> list:
    """Return all available vehicle types."""
    return sorted(_ef_df["vehicle_type"].unique().tolist())
