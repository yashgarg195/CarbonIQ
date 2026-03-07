"""GLEC Framework emission estimator for road freight."""

import os
import pandas as pd

# ── Load emission factors ──────────────────────────────────────────────────
_EF_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "emission_factors.csv")
_CARRIER_EF_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "carrier_performance.csv")

_ef_df = pd.read_csv(_EF_PATH)
_EF_LOOKUP = {
    (row.fuel_type, row.vehicle_type): row.ef_kg_co2e_per_tkm
    for _, row in _ef_df.iterrows()
}

# Try to load carrier performance data
try:
    _carrier_df = pd.read_csv(_CARRIER_EF_PATH)
    _CARRIER_LOOKUP = dict(zip(_carrier_df['carrier_name'], _carrier_df['ef_kg_co2e_per_tkm']))
except Exception:
    _CARRIER_LOOKUP = {}

# Default emission factor (UK Rigid 7.5-17t)
_DEFAULT_EF = 0.26427


def estimate_emissions(
    distance_km: float,
    weight_tonnes: float,
    fuel_type: str,
    vehicle_type: str,
    load_factor: float = 1.0,
    carrier_name: str = ""
) -> float:
    """
    Estimate CO₂e emissions using the GLEC Framework formula.
    Supports carrier-specific emission factors if carrier_name is provided.
    """
    # Priority: Carrier specific > Vehicle/Fuel specific > Default
    ef = _CARRIER_LOOKUP.get(carrier_name) if carrier_name else None
    if ef is None:
        ef = _EF_LOOKUP.get((fuel_type, vehicle_type), _DEFAULT_EF)
    
    # Ensure ef is a float
    ef_val: float = float(ef) if ef is not None else _DEFAULT_EF
    
    co2e = distance_km * weight_tonnes * ef_val * load_factor
    return round(float(co2e), 2)


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
            carrier_name=r.get("carrier_name")
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
