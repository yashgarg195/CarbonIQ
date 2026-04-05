# Product Guidelines: CarbonIQ

## Design Principles
- **Clarity over Complexity:** Logistics data can be overwhelming; prioritize clean, high-contrast visualizations and simple KPI cards.
- **Actionable Insights:** Every chart or data point should lead to a potential action (e.g., "Optimize this lane" or "Switch to EV").
- **Trust & Transparency:** Always show the calculation methodology (e.g., the GLEC formula) to build trust in the carbon estimates.

## User Experience (UX)
- **Glassmorphic Theme:** Maintain the dark, enterprise-grade glassmorphic aesthetic for a modern, high-tech feel.
- **Contextual Assistance:** The AI Assistant should be easily accessible but not intrusive, providing context-aware help based on the current page.
- **Responsive Layout:** Ensure the dashboard adapts gracefully to different screen sizes, though primary use is desktop.

## Voice and Tone
- **Professional & Expert:** Use industry-standard terminology (GLEC, CO2e, tkm, Lane Intensity).
- **Encouraging & Sustainability-Focused:** Frame insights around progress and potential savings to motivate users.
- **Precise:** Avoid vague terms; use exact figures and units wherever possible.

## Technical Standards
- **Data Integrity:** Ensure emission factors are always sourced from reputable databases (like UK GHG 2025).
- **AI Ethics:** Clearly label AI-generated insights to distinguish them from direct calculations.
- **Performance:** Streamlit components should load quickly; optimize data caching for large datasets.
