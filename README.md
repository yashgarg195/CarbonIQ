# CarbonIQ — Build Phase Context
## Carbon Tracker Agent for Road Freight
**Team:** Load a Code  
**Hackathon:** LogisticsNow LoRRI's AI Hackathon  
**Phase:** Prototype Development  
**IDE:** Google Antigravity

---

## 🎯 What We're Building
A lightweight, fully demonstrable Carbon Intelligence System for road freight that:
- Estimates CO₂e emissions per shipment
- Identifies high-emission lanes
- Provides an interactive analytics dashboard
- Includes a what-if scenario simulator (EV switch, load consolidation, rerouting)

**Constraint:** No paid APIs. Everything must be free or open-source.

---

## 🤖 AI & Model Options (All Free)

### Option A — Formula-Based (Recommended for demo)
No model needed. Use the GLEC Framework standard formula:
```
CO₂e (kg) = distance_km × weight_tonnes × emission_factor
```
- Emission factors sourced from public GLEC CSV (no API)
- Fully explainable to judges
- Zero latency, zero cost
- Use this as the core engine; layer ML on top if time allows

### Option B — Lightweight ML (Free)
Train locally, no API needed:
- **scikit-learn** Random Forest or XGBoost — train in minutes on mock data, save as `.pkl`
- **ONNX Runtime** — export model for fast inference, works anywhere
- Input features: distance, weight, vehicle type, fuel type, load factor
- Target: co2e_kg

### Option C — Free LLM APIs for Natural Language Insights
Use a free LLM to auto-generate sustainability summaries and recommendations:

| Provider | Free Tier | Best For |
|---|---|---|
| **Google Gemini API** | 15 req/min, 1M tokens/day (Gemini 1.5 Flash) | NL insight generation |
| **Groq API** | Free tier, extremely fast inference | Real-time chat assistant |
| **Hugging Face Inference API** | Free for public models | Summarization, classification |
| **Ollama** (local) | Completely free, runs offline | Llama 3, Mistral locally |
| **OpenRouter** | Free credits on signup, many models | Fallback/routing |

**Recommendation:** Use **Gemini 1.5 Flash** (Google AI Studio — free, no card needed) for the "Sustainability Insights" narrative feature. One API call per dashboard load to generate a plain-English summary of the fleet's emission status.

---

## 🛠️ Tech Stack (All Free)

| Layer | Tool | Cost |
|---|---|---|
| IDE | Google Antigravity | Free |
| Dashboard | Streamlit | Free (local + Streamlit Cloud) |
| Data processing | Pandas, NumPy | Free |
| Visualization | Plotly | Free |
| ML model | scikit-learn / XGBoost | Free |
| LLM insights | Gemini 1.5 Flash API (Google AI Studio) | Free |
| Geocoding / distance | OpenStreetMap Nominatim + OSRM | Free, no key needed |
| Database | SQLite (file-based) | Free |
| Hosting | Streamlit Community Cloud | Free |

---

## 📊 Data Plan

### Emission Factors
Store as a local CSV — no API call needed. Source: GLEC Framework (public).
- Diesel truck: ~0.089 kg CO₂e per tonne-km
- CNG truck: ~0.065 kg CO₂e per tonne-km
- EV truck: ~0.025 kg CO₂e per tonne-km

### Mock Shipment Dataset
Generate ~500-1000 records in Python using the GLEC formula as ground truth.
Fields: shipment_id, date, origin, destination, distance_km, weight_tonnes, vehicle_type, fuel_type, load_factor, cargo_type, co2e_kg

---

## 📱 Dashboard Pages

### Page 1 — Overview Dashboard
- KPI cards: total CO₂e, shipment count, avg per shipment, fleet diesel share
- Monthly emission trend chart (by fuel type)
- Top high-emission lanes bar chart
- AI-generated narrative summary (Gemini Flash, optional)

### Page 2 — Shipment Estimator
- Input: origin, destination, weight, vehicle type, fuel type, load factor
- Output: CO₂e estimate with formula breakdown
- Gauge chart vs fleet average

### Page 3 — Lane Analytics
- Lane risk classification (High / Medium / Low emission intensity)
- Sortable lane table with CO₂e, distance, load factor, shipment count
- Scatter: volume vs emission intensity

### Page 4 — What-If Simulator
- Sliders: % fleet to EV, % to CNG, load consolidation %, rerouting %
- Waterfall chart showing savings by lever
- Before vs after comparison
- Auto-generated scenario narrative (Gemini Flash, optional)

---

## 🚀 Development Phases

### Phase 1 — Data & Model
- [ ] Create emission_factors.csv
- [ ] Write data generator script (mock shipments)
- [ ] Implement GLEC formula estimator
- [ ] (Optional) Train scikit-learn model on mock data

### Phase 2 — Dashboard
- [ ] Scaffold Streamlit app (4 pages)
- [ ] Build Overview page
- [ ] Build Estimator page
- [ ] Build Lane Analytics page
- [ ] Build What-If Simulator page

### Phase 3 — AI Layer (Optional, high impact for judges)
- [ ] Integrate Gemini Flash API for narrative summaries
- [ ] Add "Ask the Carbon Agent" chat input (Groq or Gemini)

### Phase 4 — Polish & Demo Prep
- [ ] Pre-load demo data (no file upload needed on demo day)
- [ ] Deploy on Streamlit Community Cloud
- [ ] Prepare 2-minute demo script

---

## 💡 Demo Strategy
1. Pre-load data — dashboard opens with results instantly, no setup on stage
2. Run locally as primary, Streamlit Cloud as backup shareable link
3. Hardcode 2-3 dramatic what-if scenarios (e.g. 40% EV conversion = 32% CO₂e drop)
4. Keep a screenshot deck as last resort fallback

---

## 🔗 Free API Sign-Up Links
- Gemini API (Google AI Studio): https://aistudio.google.com
- Groq: https://console.groq.com
- Hugging Face: https://huggingface.co/settings/tokens
- OpenRouter: https://openrouter.ai
- OSRM (road distances, no key): http://router.project-osrm.org