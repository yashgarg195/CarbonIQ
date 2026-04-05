"""AI-powered insights for CarbonIQ using Hugging Face Inference API."""

import os
import pandas as pd

# ── Load .env file ────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass  # python-dotenv not installed, fall back to env vars

# ── Hugging Face Setup ───────────────────────────────────────────────────────
_HF_TOKEN = os.environ.get("HF_API_TOKEN", "")
_HF_MODEL = os.environ.get("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
_client = None


def _get_client():
    """Lazy-load the Hugging Face InferenceClient."""
    global _client
    if _client is None and _HF_TOKEN:
        try:
            from huggingface_hub import InferenceClient
            _client = InferenceClient(token=_HF_TOKEN)
        except Exception as e:
            print(f"[Error] Hugging Face init failed: {e}")
            _client = None
    return _client


def _generate(system_msg: str, user_msg: str, max_tokens: int = 512) -> str:
    """Generate text using the Hugging Face Inference API (chat completion)."""
    client = _get_client()
    if client is None:
        return None

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]
    response = client.chat_completion(
        messages=messages,
        model=_HF_MODEL,
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def is_available() -> bool:
    """Check if the AI features are available."""
    return bool(_HF_TOKEN)


# ── Fleet Summary ─────────────────────────────────────────────────────────────

def generate_fleet_summary(kpis: dict, top_lanes: pd.DataFrame) -> str:
    """
    Generate a plain-English narrative summary of the fleet's emission status.

    Args:
        kpis: Dict from analytics.summary_kpis().
        top_lanes: DataFrame from analytics.top_emission_lanes().

    Returns:
        Human-readable sustainability summary string.
    """
    top_lanes_str = ""
    if len(top_lanes) > 0:
        top_3 = top_lanes.head(3)
        top_lanes_str = "\n".join(
            f"  - {r['lane']}: {r['co2e_kg']:.0f} kg CO₂e ({r['shipment_count']} shipments)"
            for _, r in top_3.iterrows()
        )

    system_msg = "You are a professional sustainability analyst specializing in logistics and the GLEC Framework."
    user_msg = f"""Write a concise 3-4 sentence executive summary of the fleet's carbon emission status.
Results are now powered by the 2025 UK GHG Government Factors and EPA SmartWay carrier benchmarks.
Be specific with numbers. Highlight that accuracy has been improved with these new datasets.

Data:
- Total fleet emissions: {kpis['total_co2e']:,.0f} kg CO₂e
- Total shipments: {kpis['shipment_count']}
- Average per shipment: {kpis['avg_per_shipment']:,.1f} kg CO₂e
- Diesel share: {kpis['diesel_share']}%
- Average fleet age: {kpis['avg_fleet_age']} years
- Top emission lanes:
{top_lanes_str}

Write the summary in a professional but accessible tone. Mention how fleet age affects overall efficiency. No bullet points, just flowing prose."""

    try:
        result = _generate(system_msg, user_msg)
        if result:
            return result
    except Exception as e:
        print(f"[Error] HF fleet summary failed: {e}")

    return _fallback_fleet_summary(kpis, top_lanes)


def _fallback_fleet_summary(kpis: dict, top_lanes: pd.DataFrame) -> str:
    """Fallback summary when AI is unavailable."""
    return (
        f"Your fleet generated **{kpis['total_co2e']:,.0f} kg CO₂e** across "
        f"**{kpis['shipment_count']}** shipments (avg "
        f"**{kpis['avg_per_shipment']:,.1f} kg** per shipment). "
        f"Diesel vehicles account for **{kpis['diesel_share']}%** of the fleet "
        f"with an average vehicle age of **{kpis.get('avg_fleet_age', 'N/A')} years**. "
        f"The highest-emission lane is **{kpis['worst_lane']}**. "
        f"Consider transitioning diesel vehicles to EV or CNG and replacing older vehicles to reduce emissions."
    )


# ── Scenario Narrative ────────────────────────────────────────────────────────

def generate_scenario_narrative(scenario: dict) -> str:
    """
    Generate a narrative for What-If Simulator results.

    Args:
        scenario: Dict from simulator.run_combined_scenario()['total'].

    Returns:
        Human-readable scenario analysis string.
    """
    levers_text = ""
    if "levers" in scenario:
        levers_text = "\n".join(
            f"  - {l['label']}: saves {l['savings_co2e']:,.0f} kg ({l['savings_pct']}%)"
            for l in scenario.get("levers", [])
        )

    total = scenario.get("total", scenario)

    system_msg = "You are a sustainability consultant analyzing a what-if scenario for a road freight fleet in India."
    user_msg = f"""Write a concise 2-3 sentence summary of the scenario results with an actionable recommendation.

Scenario Results:
- Baseline emissions: {total['before_co2e']:,.0f} kg CO₂e
- Projected emissions: {total['after_co2e']:,.0f} kg CO₂e
- Total savings: {total['savings_co2e']:,.0f} kg ({total['savings_pct']}% reduction)
Individual levers:
{levers_text}

Be specific, cite numbers, and include a prioritized recommendation."""

    try:
        result = _generate(system_msg, user_msg)
        if result:
            return result
    except Exception as e:
        print(f"[Error] HF scenario narrative failed: {e}")

    return _fallback_scenario_narrative(scenario)


def _fallback_scenario_narrative(scenario: dict) -> str:
    """Fallback narrative when AI is unavailable."""
    total = scenario.get("total", scenario)
    return (
        f"This scenario reduces fleet emissions from **{total['before_co2e']:,.0f} kg** "
        f"to **{total['after_co2e']:,.0f} kg CO₂e** — a **{total['savings_pct']}%** reduction "
        f"saving **{total['savings_co2e']:,.0f} kg CO₂e**."
    )


# ── Carbon Agent Chat ─────────────────────────────────────────────────────────

def ask_carbon_agent(question: str, df: pd.DataFrame) -> str:
    """
    Answer user questions about fleet emissions using Hugging Face with DataFrame context.

    Args:
        question: User's natural language question.
        df: Shipment DataFrame for context.

    Returns:
        AI-generated answer string.
    """
    if not is_available():
        return "[Notice] AI Agent is not available. Please set the `HF_API_TOKEN` environment variable to enable this feature."

    # Build compact data context
    total_co2e = df["co2e_kg"].sum()
    shipment_count = len(df)
    fuel_breakdown = df.groupby("fuel_type")["co2e_kg"].sum().to_dict()
    top_routes = (
        df.groupby(["origin", "destination"])["co2e_kg"]
        .sum()
        .nlargest(5)
        .reset_index()
    )
    routes_str = "\n".join(
        f"  - {r['origin']}→{r['destination']}: {r['co2e_kg']:.0f} kg"
        for _, r in top_routes.iterrows()
    )

    avg_load = df["load_factor"].mean()
    vehicle_breakdown = df.groupby("vehicle_type")["co2e_kg"].sum().to_dict()

    system_msg = """You are CarbonIQ, an AI assistant specializing in road freight carbon emissions for Indian logistics.
Answer the user's question using ONLY the data provided below. Be concise (2-4 sentences max).
If the data doesn't contain enough information, say so honestly."""
    user_msg = f"""Fleet Data Context:
- Total emissions: {total_co2e:,.0f} kg CO₂e across {shipment_count} shipments
- Fuel breakdown: {fuel_breakdown}
- Vehicle breakdown: {vehicle_breakdown}
- Average load factor: {avg_load:.2f}
- Average vehicle age: {df['vehicle_age'].mean():.1f} years
- Top 5 emission routes:
{routes_str}

User question: {question}"""

    try:
        result = _generate(system_msg, user_msg)
        if result:
            return result
        return "[Error] Could not generate a response. Please try again."
    except Exception as e:
        return f"[Error] Error generating response: {e}"


# ── Chart-Level AI Insights ──────────────────────────────────────────────────

def generate_chart_insight(chart_name: str, data_context: str) -> str:
    """
    Generate a short 1-2 sentence AI insight for an individual chart.

    Args:
        chart_name: Human-readable chart title.
        data_context: A short string summarizing the key data points.

    Returns:
        Brief AI-generated insight string.
    """
    system_msg = (
        "You are CarbonIQ, a sustainability analytics assistant. "
        "Write exactly 2 concise sentences interpreting the chart data. "
        "Be specific with numbers. No bullet points."
    )
    user_msg = f"Chart: {chart_name}\nData: {data_context}\n\nProvide a brief analytical insight."

    try:
        result = _generate(system_msg, user_msg, max_tokens=150)
        if result:
            return result
    except Exception as e:
        print(f"[Error] Chart insight generation failed: {e}")

    return f"This chart shows the distribution and trends for {chart_name.lower()}. Review the data points above for detailed analysis."