"""Generate ~800 synthetic shipment records using GLEC emission factors."""

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ── Configuration ─────────────────────────────────────────────────────────────
NUM_RECORDS = 800
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "sample_shipments.csv")
EF_PATH = os.path.join(os.path.dirname(__file__), "emission_factors.csv")

# Realistic Indian city pairs with approximate road distances (km)
ROUTES = [
    ("Mumbai", "Delhi", 1400),
    ("Delhi", "Kolkata", 1500),
    ("Kolkata", "Chennai", 1660),
    ("Chennai", "Mumbai", 1330),
    ("Bangalore", "Hyderabad", 570),
    ("Hyderabad", "Mumbai", 710),
    ("Delhi", "Jaipur", 280),
    ("Jaipur", "Ahmedabad", 670),
    ("Ahmedabad", "Mumbai", 530),
    ("Pune", "Bangalore", 840),
    ("Lucknow", "Delhi", 550),
    ("Chennai", "Bangalore", 350),
    ("Kolkata", "Guwahati", 1000),
    ("Mumbai", "Nagpur", 820),
    ("Delhi", "Chandigarh", 250),
    ("Hyderabad", "Visakhapatnam", 620),
    ("Bangalore", "Kochi", 560),
    ("Pune", "Hyderabad", 560),
    ("Jaipur", "Delhi", 280),
    ("Nagpur", "Kolkata", 1060),
]

CARGO_TYPES = [
    "FMCG", "Pharmaceuticals", "Electronics", "Textiles",
    "Auto Parts", "Chemicals", "Agriculture", "E-commerce",
    "Building Materials", "Food & Beverages",
]

# ── Generator ─────────────────────────────────────────────────────────────────

def generate():
    ef_df = pd.read_csv(EF_PATH)
    ef_lookup = {
        (row.fuel_type, row.vehicle_type): row.ef_kg_co2e_per_tkm
        for _, row in ef_df.iterrows()
    }

    fuel_types = ef_df["fuel_type"].unique().tolist()
    vehicle_types = ef_df["vehicle_type"].unique().tolist()

    # Weighted fuel distribution: ~70% Diesel, ~20% CNG, ~10% EV
    fuel_weights = {"Diesel": 0.70, "CNG": 0.20, "EV": 0.10}

    records = []
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range_days = (end_date - start_date).days

    for i in range(1, NUM_RECORDS + 1):
        origin, destination, base_dist = random.choice(ROUTES)
        # Add ±15% distance variation for realism
        distance_km = round(base_dist * random.uniform(0.85, 1.15), 1)
        weight_tonnes = round(random.uniform(2, 25), 1)
        fuel_type = random.choices(fuel_types, weights=[fuel_weights.get(f, 0.1) for f in fuel_types])[0]
        vehicle_type = random.choice(vehicle_types)
        load_factor = round(random.uniform(0.4, 1.0), 2)
        cargo_type = random.choice(CARGO_TYPES)
        date = start_date + timedelta(days=random.randint(0, date_range_days))

        ef = ef_lookup.get((fuel_type, vehicle_type), 0.089)
        co2e_kg = round(distance_km * weight_tonnes * ef * load_factor, 2)

        records.append({
            "shipment_id": f"SHP-{i:04d}",
            "date": date.strftime("%Y-%m-%d"),
            "origin": origin,
            "destination": destination,
            "distance_km": distance_km,
            "weight_tonnes": weight_tonnes,
            "vehicle_type": vehicle_type,
            "fuel_type": fuel_type,
            "load_factor": load_factor,
            "cargo_type": cargo_type,
            "co2e_kg": co2e_kg,
        })

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Generated {len(df)} shipment records → {OUTPUT_PATH}")
    return df


if __name__ == "__main__":
    generate()
