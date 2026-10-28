"""
Daily Site Assistant & Weather-Aware Advisory Module (Epic 5)
Provides dynamic weather-triggered site protocols and an interactive multi-turn
construction engineering chatbot powered by Gemini with a domain-specific offline expert engine.
Platform ID: 6ac4c98d1dcde6d7857c1642
"""

import datetime
from typing import Any, Dict, List, Optional, Tuple

from modules.ai_engine import (
    call_gemini_chat,
    resolve_api_key,
)

PLATFORM_ID = "6ac4c98d1dcde6d7857c1642"

WEATHER_PROTOCOLS = {
    "Normal / Favorable (22°C - 30°C, Calm)": {
        "badge_color": "#10b981",
        "severity": "Standard Operations",
        "crane_status": "[NORMAL] Fully Operational (Inspect anemometer and limit switches during morning pre-start)",
        "electrical_status": "[NORMAL] Routine Inspections (Check earth pit resistance <= 5 ohms and test ELCB trips)",
        "concrete_protocol": "[NORMAL] Standard Curing Protocol (Maintain continuous ponding/wet hessian curing for 7 days minimum under IS 456 Cl. 13.5)",
        "workforce_guidelines": "[NORMAL] Standard 8-hour shift with mandatory PPE compliance and 15-minute morning toolbox talk",
        "special_instructions": "Optimal conditions for concreting, structural steel erection, and external façade glazing.",
    },
    "High Wind (> 38 km/h / 24 mph / Gale Alert)": {
        "badge_color": "#ef4444",
        "severity": "High Hazard - Lifting Halted",
        "crane_status": "[SUSPENDED] MANDATORY SUSPENSION: Cease all tower crane, mobile crane, and hoist operations. Place boom in neutral freewheeling/weathervaning mode per OSHA 1926.1431 and IS 4573.",
        "electrical_status": "[CAUTION] Inspect overhead temporary catenary wires for swaying or contact with scaffolding tubes.",
        "concrete_protocol": "[CAUTION] Accelerated Surface Evaporation Risk: Use aliphatic alcohol evaporation retardants or wet burlap immediately after screeding to prevent plastic shrinkage cracking.",
        "workforce_guidelines": "[HALT] Halt all work on suspended cradles (gondolas), external scaffolding, and roofing sheets. Clear loose formwork ply and tie-down rebar bundles.",
        "special_instructions": "Secure all perimeter edge debris, zinc sheets, and signboards. Check guy-wire tension on all temporary bracing towers.",
    },
    "Heavy Rain & Monsoon Waterlogging": {
        "badge_color": "#3b82f6",
        "severity": "High Hazard - Electrical & Trenching Alert",
        "crane_status": "[CAUTION] Crane operations permitted only if ground bearing capacity under outriggers is verified. Monitor soil saturation.",
        "electrical_status": "[CRITICAL] ELECTRICAL LOCKOUT: De-energize all surface distribution boards exposed to water. Isolate 415V batching plant lines. Mandate 30mA residual current circuit breakers (RCCBs).",
        "concrete_protocol": "[BAN] Rain Concreting Ban: DO NOT pour unshielded concrete during downpour (IS 456 Cl. 13.3). If pour was underway, cover fresh slab with 250-micron polyethylene sheeting to prevent cement paste washout.",
        "workforce_guidelines": "[CAUTION] Slip and fall mitigation: Prohibit ladder work. Issue anti-slip gumboots. Establish designated dry walking planks across muddy corridors.",
        "special_instructions": "Deploy submersible dewatering pumps in deep basement pits and elevator sumps. Inspect open trenches for slope collapse/undermining per OSHA 1926 Subpart P.",
    },
    "Extreme Heat (> 40°C / Heatwave Alert)": {
        "badge_color": "#f97316",
        "severity": "High Hazard - Thermal & Curing Stress",
        "crane_status": "[CAUTION] Monitor hydraulic fluid temperatures on mobile cranes and telehandlers; ensure oil coolers operate effectively.",
        "electrical_status": "[CAUTION] Avoid cable overloading; thermal derating applies to heavily loaded underground and surface feeder cables.",
        "concrete_protocol": "[CRITICAL] HOT WEATHER CONCRETING PROTOCOL (IS 456 / ACI 305R): Fresh concrete delivery temperature must NOT exceed 32°C. Use chilled water, flake ice batching, or retarder admixtures. Shift major slab pours to night hours (7:00 PM - 5:00 AM). Initiate wet curing immediately upon final set.",
        "workforce_guidelines": "[CRITICAL] Heat Stress Prevention (OSHA National Emphasis Program): Mandate 15-minute rest breaks every hour in shaded cooling sheds. Provide ORS electrolytes and chilled drinking water. Reschedule heavy manual labor to early morning (5:30 AM - 11:00 AM).",
        "special_instructions": "Monitor workers for symptoms of heat exhaustion (dizziness, pale skin, nausea) and heat stroke (confusion, cessation of sweating - immediate 108/medical emergency).",
    },
    "Poor Air Quality & Dust Storm (AQI > 300)": {
        "badge_color": "#a855f7",
        "severity": "Moderate to High Environmental Alert",
        "crane_status": "[CAUTION] Reduced visibility: Use certified signal banksman with two-way radios for all crane slewing maneuvers.",
        "electrical_status": "[NORMAL] Standard precautions; blow clean air intake filters on site diesel generators.",
        "concrete_protocol": "[CAUTION] Keep aggregate stockpiles covered with tarpaulins to prevent fine silt and dust contamination affecting mix water demand.",
        "workforce_guidelines": "[CAUTION] Issue mandatory N95 / FFP2 particulate respirators to all operatives. Rotate workers performing grit-blasting or demolition.",
        "special_instructions": "Activate water mist cannons and perimeter fogger nozzles along site boundaries to suppress fugitive PM10 / PM2.5 dust per Central Pollution Control Board (CPCB) norms.",
    },
}

# Domain Expert Offline Knowledge Base for construction Q&A
ENGINEERING_KNOWLEDGE_BASE = [
    {
        "keywords": ["curing", "cure", "is 456", "duration", "water curing"],
        "answer": """**Concrete Curing Guidelines per IS 456:2000 (Clause 13.5):**
1. **Minimum Duration:**
   - For Ordinary Portland Cement (OPC): Minimum **7 days** of continuous moist curing.
   - For concrete with mineral admixtures (Fly Ash, GGBS, Pozzolana - PPC): Minimum **10 days** due to slower pozzolanic hydration.
   - In dry, hot, or arid climatic conditions: Minimum **14 days** is strongly recommended.
2. **Acceptable Curing Methods:**
   - **Horizontal Slabs:** Ponding with water using 50mm mortar bunds (most effective).
   - **Vertical Elements (Columns, Walls):** Wet hessian (burlap) cloth wrapping kept continuously saturated, or certified membrane-forming curing compounds conforming to ASTM C309.
3. **Engineering Impact:** Neglecting early curing reduces 28-day compressive strength by up to 30% and induces severe plastic shrinkage micro-cracking.""",
    },
    {
        "keywords": ["stripping", "formwork", "shuttering", "deshuttering", "removal"],
        "answer": """**Minimum Stripping Time for Formwork per IS 456:2000 (Clause 11.3):**
Under normal temperature conditions (using OPC cement):
1. **Vertical formwork to columns, walls, beams:** **16 to 24 hours**
2. **Soffit formwork to slabs (props left under):** **3 days**
3. **Soffit formwork to beams (props left under):** **7 days**
4. **Props under slabs:**
   - Spanning up to 4.5m: **7 days**
   - Spanning over 4.5m: **14 days**
5. **Props under beams and arches:**
   - Spanning up to 6.0m: **14 days**
   - Spanning over 6.0m: **21 days**
*Note: For PPC / Fly Ash concrete, increase durations by 25-30% or verify via on-site cube testing achieving 70% characteristic strength.*""",
    },
    {
        "keywords": ["crane", "wind", "speed", "shutdown", "tower crane", "limit"],
        "answer": """**Tower Crane Wind Speed Safety Thresholds (OSHA 1926.1431 & IS 4573 / ISO 4302):**
1. **Standard Operation Limit:** Normal crane lifts proceed up to **32 km/h (20 mph / 9 m/s)**.
2. **Cautionary Lifting of Large Surface Panels:** Reduce operations when wind gusts reach **25 km/h (15 mph)** due to sail area effect.
3. **Mandatory Shutdown Threshold:** **38 km/h (24 mph / ~10.5 m/s)** or manufacturer's stated limit. All lifting must immediately cease.
4. **Storm Weather Protocol:**
   - Hoist hook block to highest limit.
   - Trolley brought to jib root (near mast).
   - **CRITICAL:** Disengage slew brake to place jib in free-wheeling / weathervaning mode so it rotates naturally with the wind without structural twisting.""",
    },
    {
        "keywords": ["rebar", "fe 500", "fe 500d", "grade", "steel", "seismic"],
        "answer": """**Rebar Grades & Selection per IS 1786:2008 & IS 13920 (Ductile Detailing):**
1. **Fe 500 vs Fe 500D:**
   - The 'D' designates **High Ductility**.
   - Fe 500 has minimum elongation of 12%.
   - **Fe 500D** requires minimum elongation of **14.5%** and a higher tensile-to-yield ratio (UTS/YS >= 1.10).
2. **Seismic Mandate:** IS 13920 mandates Fe 500D (or Fe 415D) for all RCC structural elements (columns, beams, shear walls) in **Seismic Zones III, IV, and V** to ensure energy dissipation during earthquakes without brittle fracture.
3. **Corrosion Resistance:** In coastal/marine environments, use CRS (Corrosion Resistant Steel) or epoxy-coated / zinc-galvanized TMT bars.""",
    },
    {
        "keywords": ["excavation", "shoring", "trench", "osha", "trenching"],
        "answer": """**Excavation & Trenching Safety Standards (OSHA 1926 Subpart P & IS 3764):**
1. **Protective Systems Threshold:** Any excavation reaching **1.5 meters (5 feet)** or deeper must have an engineered protective system:
   - **Sloping / Benching:** Angle of repose based on soil type (Type A 3/4:1, Type B 1:1, Type C 1.5:1).
   - **Shoring:** Hydraulic aluminum or timber shoring preventing soil movement.
   - **Shielding:** Trench boxes designed to protect personnel inside.
2. **Access & Egress:** Ladders, stairways, or ramps must be provided within **7.5 meters (25 feet)** of lateral travel for workers in trenches 1.2m (4ft) or deeper.
3. **Spoil Heap Clearance:** Excavated soil heaps must be set back at least **0.6 meters (2 feet)** from the edge of the excavation.
4. **Competent Person:** Daily inspections required before work starts and after any rain event.""",
    },
    {
        "keywords": ["slump", "workability", "test", "concrete mix", "m25", "m30"],
        "answer": """**Concrete Slump Test Values per IS 456:2000 (Clause 7.1):**
1. **Low Workability (25 - 75 mm):** Mass concrete, shallow foundations with light reinforcement, pavement slabs.
2. **Medium Workability (75 - 100 mm):** Heavily reinforced sections in slabs, beams, columns, and retaining walls.
3. **High Workability (100 - 150 mm):** Pumped concrete, congested rebar cages, and slipform construction.
4. **Very High Workability (150 - 200 mm):** Tremie pipe concreting under water or bored cast-in-situ piling.
*Tip: Always measure slump within 15 minutes of discharge at point of placement.*""",
    },
]


def query_engineering_assistant(
    question: str,
    chat_history: List[Dict[str, str]],
    api_key: Optional[str] = None,
) -> str:
    """
    Answers construction engineering questions.
    Uses Gemini live chat when key is available, or intelligently searches
    the offline engineering knowledge graph.
    """
    key = resolve_api_key(api_key)

    if key:
        try:
            answer = call_gemini_chat(
                chat_history=chat_history,
                system_instruction=(
                    "You are a Senior Construction Project Director and Chartered Structural Engineer. "
                    "Provide practical, precise, and code-compliant answers citing IS 456:2000, IS 13920, "
                    "OSHA 1926, and CPWD specifications where applicable. Never replace a site engineer's formal sign-off."
                ),
                api_key=key,
            )
            if answer and answer.strip():
                return answer
        except Exception:
            pass

    # Intelligent offline fallback engine
    q_lower = question.lower()
    for entry in ENGINEERING_KNOWLEDGE_BASE:
        if any(kw in q_lower for kw in entry["keywords"]):
            return entry["answer"]

    # General fallback response
    return (
        f"**Construction Advisory for: '{question}'**\n\n"
        "As an on-site engineering assistant, here is standard site protocol:\n"
        "1. **Code Validation:** Cross-reference the relevant section of IS 456:2000 (Plain & Reinforced Concrete) or OSHA 1926.\n"
        "2. **Approved Method Statement:** Verify that the task aligns with the project's approved Job Safety Analysis (JSA) and Method Statement.\n"
        "3. **Physical Verification:** Check site batching calibration, cube test reports (7-day and 28-day), and rebar mill test certificates (MTC).\n"
        "4. **Competent Person Sign-off:** For structural or safety-critical modifications, obtain written approval from the Lead Structural Engineer or EHS Officer.\n\n"
        "*Tip: Enter your Google Gemini API key in the sidebar for real-time generative responses to custom project scenarios.*"
    )
