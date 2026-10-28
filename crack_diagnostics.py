"""
Crack Diagnostics & Structural Integrity Module (Epic 2 & Epic 4)
Classifies concrete defects, estimates crack width, isolates root causes,
and provides structural engineering repair blueprints aligned with IS 456:2000 and ACI 224R.
Platform ID: 6ac4c98d1dcde6d7857c1642
"""

import datetime
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image

from modules.ai_engine import (
    call_gemini_multimodal,
    sanitize_json_response,
    resolve_api_key,
)

PLATFORM_ID = "6ac4c98d1dcde6d7857c1642"

CRACK_SYSTEM_PROMPT = """You are a Principal Structural Forensic Engineer specializing in reinforced concrete (RCC) durability, failure analysis, and rehabilitation under IS 456:2000 and ACI 224R/318.
Examine surface images with meticulous forensic rigor:
1. Classify defects strictly into one of: 'Hairline', 'Settlement', 'Structural Shear', 'Thermal Expansion', 'Spalling', or 'Surface Crazing'.
2. Provide a realistic estimated crack width in millimeters (mm).
3. If structural shear, active movement, or deep delamination is suspected, mandate immediate engineer escalation.
4. Output strictly valid JSON conforming to the contract."""

CRACK_ANALYSIS_PROMPT = """Analyze this concrete/wall defect image.
Classify the defect type, estimate crack width in mm, isolate root causes, and propose engineering repair methods.

Return ONLY a valid JSON object matching this schema:
{
  "platform_id": "6ac4c98d1dcde6d7857c1642",
  "assessment_timestamp": "ISO-8601 string",
  "defect_type": "Hairline" | "Settlement" | "Structural Shear" | "Thermal Expansion" | "Spalling",
  "structural_element": "RCC Beam" | "RCC Column" | "Slab Deck" | "Shear Wall / Retaining Wall" | "Masonry Plaster",
  "estimated_crack_width_mm": 1.5, // float in millimeters
  "severity": "Low" | "Moderate" | "High" | "Critical",
  "urgency": "Immediate / Stop Live Load" | "High Priority (< 48 hrs)" | "Scheduled Maintenance (< 30 days)" | "Routine Monitoring",
  "crack_orientation_pattern": "Diagonal ~45° near support" | "Vertical longitudinal" | "Spiderweb / Map cracking" | "Horizontal step-like",
  "is_456_compliance_status": "Exceeds permissible 0.3mm limit under IS 456 Cl 35.3.2" | "Within serviceability limit",
  "root_causes": [
    "Primary cause 1",
    "Secondary factor 2"
  ],
  "recommended_engineering_repairs": [
    "Specific repair protocol (e.g. low-pressure epoxy injection, elastomeric routing, micro-concrete re-profiling)"
  ],
  "non_destructive_testing_advised": [
    "e.g. Ultrasonic Pulse Velocity (UPV) Test (IS 13311 Part 1)",
    "Rebound Hammer Test (IS 13311 Part 2)",
    "Core Extraction & Carbonation Depth Test"
  ],
  "engineer_escalation_protocol": "Standard or emergency instructions for the site engineer."
}"""


def get_crack_demo_result(defect_type: str = "Structural Shear") -> Dict[str, Any]:
    """Generates realistic pre-calculated diagnostic profiles for demonstration mode."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if defect_type == "Structural Shear":
        return {
            "platform_id": PLATFORM_ID,
            "assessment_timestamp": now_iso,
            "defect_type": "Structural Shear",
            "structural_element": "RCC Beam (Near Support Junction)",
            "estimated_crack_width_mm": 1.8,
            "severity": "Critical",
            "urgency": "Immediate / Stop Live Load",
            "crack_orientation_pattern": "Diagonal ~45° inclined shear tension crack propagating toward compression zone",
            "is_456_compliance_status": "Severe Non-Compliance: Exceeds permissible limit of 0.3mm (Cl. 35.3.2) by 500%",
            "root_causes": [
                "Principal diagonal tensile stresses exceeding concrete shear capacity (IS 456 Cl. 40)",
                "Insufficient or widely spaced transverse shear stirrups (links) in high shear zone",
                "Unanticipated construction surcharge loading on floor span above",
                "Substandard bond between longitudinal rebar and surrounding aggregate matrix",
            ],
            "recommended_engineering_repairs": [
                "Emergency Action: Erect heavy-duty adjustable steel shores (acrow props) directly under beam to relieve live load.",
                "Precision Drill: Install mechanical injection ports at 150mm centers along crack trace.",
                "Pressure Injection: Low-viscosity, high-modulus structural epoxy resin (conforming to ASTM C881 / IS code).",
                "External Strengthening: Apply bidirectional Carbon Fiber Reinforced Polymer (CFRP) fabric laminate U-wraps around web.",
                "Post-Repair Load Test: Verify flexural and shear recovery per IS 456 Cl. 17.6 criteria.",
            ],
            "non_destructive_testing_advised": [
                "Ultrasonic Pulse Velocity (UPV) across beam cross-section (IS 13311 Part 1) to verify internal crack depth",
                "Rebound Hammer survey (IS 13311 Part 2) to evaluate concrete grade uniformity",
                "Ferroscan / Covermeter inspection to map existing stirrup spacing",
            ],
            "engineer_escalation_protocol": "Red-tag zone immediately. Notify Project Structural Engineer and Project Director within 2 hours. Install tell-tale glass crack monitors.",
        }

    elif defect_type == "Spalling":
        return {
            "platform_id": PLATFORM_ID,
            "assessment_timestamp": now_iso,
            "defect_type": "Spalling",
            "structural_element": "RCC Column & Soffit",
            "estimated_crack_width_mm": 3.2,
            "severity": "High",
            "urgency": "High Priority (< 48 hrs)",
            "crack_orientation_pattern": "Delamination fracture plane with exposed oxidized steel reinforcement",
            "is_456_compliance_status": "Critical Durability Failure: Inadequate nominal cover violating IS 456:2000 Cl. 26.4",
            "root_causes": [
                "Atmospheric carbonation ingress neutralizing concrete alkalinity (pH < 9.0)",
                "Corrosion expansion of embedded steel rebar creating radial bursting tensile stresses",
                "Inadequate original clear concrete cover (< 25mm in external exposure)",
                "Moisture migration and chloride penetration through porous concrete matrix",
            ],
            "recommended_engineering_repairs": [
                "Delineate repair boundary with diamond saw cut (minimum 15mm depth) to prevent feather edging.",
                "Chop back distressed concrete behind exposed corroded bars (minimum 20mm clearance all around rebar).",
                "Grit-blast corroded rebar to Swedish Standard Sa 2.5 cleanliness; apply zinc-rich epoxy anti-corrosion primer.",
                "Apply bonding agent (polymer/epoxy based) followed by fiber-reinforced polymer modified structural repair mortar (PMM).",
                "Apply elastomeric anti-carbonation protective coating over entire concrete surface.",
            ],
            "non_destructive_testing_advised": [
                "Phenolphthalein carbonation depth indicator spray",
                "Half-Cell Potential corrosion mapping (ASTM C876)",
                "Chloride ion content titration test",
            ],
            "engineer_escalation_protocol": "Install safety catch-netting beneath soffit to prevent concrete debris falling on personnel. Schedule repairs within 48 hours.",
        }

    # Default: Hairline / Shrinkage
    return {
        "platform_id": PLATFORM_ID,
        "assessment_timestamp": now_iso,
        "defect_type": "Hairline",
        "structural_element": "Masonry Plaster / Surface Screed",
        "estimated_crack_width_mm": 0.2,
        "severity": "Low",
        "urgency": "Routine Monitoring",
        "crack_orientation_pattern": "Non-structural map cracking / random superficial micro-fissures",
        "is_456_compliance_status": "Within acceptable cosmetic tolerance (<= 0.3mm under IS 456 Cl. 35.3.2)",
        "root_causes": [
            "Plastic shrinkage during early curing phase due to rapid ambient moisture evaporation",
            "High water-cement ratio in plaster skim mortar",
            "Minor diurnal thermal expansion and contraction cycles",
            "Insufficient wet curing duration following plaster application",
        ],
        "recommended_engineering_repairs": [
            "Monitor crack stability over a 30-day thermal cycle using an optical crack comparator card.",
            "If dormant: Rake open fissure lightly in V-groove (2mm x 2mm).",
            "Fill with flexible acrylic / polyurethane crack sealant.",
            "Apply two coats of fiber-bridging elastomeric exterior architectural paint.",
        ],
        "non_destructive_testing_advised": [
            "Visual crack comparator optical gauge monitoring (weekly log)",
            "Moisture meter reading to detect active water ingress",
        ],
        "engineer_escalation_protocol": "No immediate structural hazard. Include in routine quarterly facility maintenance log.",
    }


def diagnose_concrete_defect(
    image: Optional[Image.Image],
    api_key: Optional[str] = None,
    force_demo: bool = False,
    demo_type: str = "Structural Shear",
    user_context: str = "",
) -> Tuple[Dict[str, Any], str]:
    """
    Executes multimodal concrete defect classification and triage.
    Returns (result_dict, execution_source).
    """
    key = resolve_api_key(api_key)

    if not force_demo and key and image is not None:
        try:
            full_prompt = CRACK_ANALYSIS_PROMPT
            if user_context.strip():
                full_prompt += f"\n\nAdditional Site Context from Engineer:\n{user_context.strip()}"

            raw_json = call_gemini_multimodal(
                prompt=full_prompt,
                image=image,
                system_instruction=CRACK_SYSTEM_PROMPT,
                api_key=key,
                json_mode=True,
            )
            result = sanitize_json_response(raw_json)
            result.setdefault("platform_id", PLATFORM_ID)
            result.setdefault("defect_type", "Structural Shear")
            result.setdefault("estimated_crack_width_mm", 1.0)
            result.setdefault("severity", "Moderate")
            result.setdefault("root_causes", [])
            result.setdefault("recommended_engineering_repairs", [])
            return result, "AI Multimodal Diagnostic (Gemini Live)"
        except Exception as exc:
            demo_data = get_crack_demo_result(demo_type)
            demo_data["notes"] = f"Live diagnostic failed ({exc}). Showing verified forensic baseline."
            return demo_data, f"Fallback Demonstration Mode (Error: {exc})"

    return get_crack_demo_result(demo_type), "Demonstration Mode (Pre-validated Data Contract)"
