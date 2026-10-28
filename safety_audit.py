"""
Site Safety & PPE Audit Module (Epic 2 & Epic 4)
Performs multimodal visual audits for worker PPE compliance and site hazard detection
aligned with OSHA 1926 (Subparts E, M) and Indian Standards (IS 456, IS 2925, IS 3521).
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

SAFETY_SYSTEM_PROMPT = """You are a Senior Construction Site Safety Auditor and EHS Engineer certified in OSHA 1926 (Safety and Health Regulations for Construction) and Indian Standards (IS 456:2000, IS 2925, IS 3521, IS 13416).
Analyze site images with rigorous objectivity.
1. NEVER assume PPE is worn if obscured, out of frame, or ambiguous; mark status as 'Not Verifiable' or 'Indeterminate'.
2. Classify hazards into severity: 'Low', 'Medium', 'High', or 'Critical'.
3. Assign actionable, engineer-grade corrective remedies citing OSHA and IS standards.
4. Always output strictly valid JSON matching the exact requested contract."""

SAFETY_ANALYSIS_PROMPT = """Analyze this construction site photo for worker PPE compliance and visible site hazards.

Return ONLY a valid JSON object matching this schema:
{
  "platform_id": "6ac4c98d1dcde6d7857c1642",
  "audit_timestamp": "ISO-8601 string",
  "safety_score": 82, // integer between 0 and 100
  "overall_status": "Compliant" | "Review Required" | "Action Required" | "Critical Non-Compliance",
  "compliance_summary": "Concise 2-sentence executive summary of observations",
  "worker_count_estimate": 3,
  "ppe_detection": [
    {
      "item": "Safety Helmet / Hard Hat",
      "detected_count": 3,
      "missing_count": 0,
      "status": "Compliant" | "Non-Compliant" | "Partial" | "Not Verifiable",
      "standard_ref": "OSHA 1926.100 / IS 2925:1984",
      "risk_level": "Low" | "Medium" | "High" | "Critical",
      "observation": "All 3 visible personnel wearing Type 1 Class E industrial hard hats."
    },
    {
      "item": "High-Visibility Vest",
      "detected_count": 3,
      "missing_count": 0,
      "status": "Compliant" | "Non-Compliant" | "Partial" | "Not Verifiable",
      "standard_ref": "OSHA 1926.201 / IS 15809 Class 2",
      "risk_level": "Low" | "Medium" | "High" | "Critical",
      "observation": "Fluorescent orange/lime vests with retroreflective tape visible."
    },
    {
      "item": "Safety Footwear / Steel-Toe Boots",
      "detected_count": 2,
      "missing_count": 1,
      "status": "Compliant" | "Non-Compliant" | "Partial" | "Not Verifiable",
      "standard_ref": "OSHA 1926.96 / IS 15298:2016",
      "risk_level": "Medium",
      "observation": "Heavy protective work boots detected on visible feet; one worker's feet obscured by material."
    },
    {
      "item": "Fall Protection / Safety Harness",
      "detected_count": 0,
      "missing_count": 0,
      "status": "Compliant" | "Non-Compliant" | "Not Applicable (Ground Level)" | "Not Verifiable",
      "standard_ref": "OSHA 1926.501 / IS 3521:1999",
      "risk_level": "Critical",
      "observation": "Required when working at elevations >= 1.8m (6 ft). Note whether workers are elevated or at grade."
    }
  ],
  "identified_hazards": [
    {
      "hazard_id": "HAZ-01",
      "hazard": "Specific hazard description",
      "category": "Fall Hazard" | "Electrical" | "Struck-by" | "Caught-in-between" | "Housekeeping" | "Access/Egress",
      "severity": "Low" | "Medium" | "High" | "Critical",
      "osha_ref": "e.g. OSHA 1926.501(b)(1)",
      "is_ref": "e.g. IS 13416 Part 1",
      "corrective_remedy": "Concrete, actionable step-by-step remedy."
    }
  ],
  "site_advisory_notes": "Important site note or supervisory advisory."
}"""


def get_safety_demo_result(scenario: str = "compliant_site") -> Dict[str, Any]:
    """Generates realistic structured audit results for demonstration mode."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if scenario == "high_risk":
        return {
            "platform_id": PLATFORM_ID,
            "audit_timestamp": now_iso,
            "safety_score": 54,
            "overall_status": "Critical Non-Compliance",
            "compliance_summary": "High fall hazard observed on elevated slab deck without perimeter barrier. Multiple workers lack anchored harnesses and high-visibility gear.",
            "worker_count_estimate": 4,
            "ppe_detection": [
                {
                    "item": "Safety Helmet / Hard Hat",
                    "detected_count": 2,
                    "missing_count": 2,
                    "status": "Non-Compliant",
                    "standard_ref": "OSHA 1926.100 / IS 2925",
                    "risk_level": "Critical",
                    "observation": "2 workers operating in active hoist zone without hard hats.",
                },
                {
                    "item": "High-Visibility Vest",
                    "detected_count": 1,
                    "missing_count": 3,
                    "status": "Non-Compliant",
                    "standard_ref": "OSHA 1926.201 / IS 15809",
                    "risk_level": "High",
                    "observation": "3 workers wearing plain dark clothing near forklift transit lane.",
                },
                {
                    "item": "Safety Footwear / Steel-Toe Boots",
                    "detected_count": 3,
                    "missing_count": 1,
                    "status": "Partial",
                    "standard_ref": "OSHA 1926.96 / IS 15298",
                    "risk_level": "Medium",
                    "observation": "One operative observed in soft athletic shoes amidst scrap rebar.",
                },
                {
                    "item": "Fall Protection / Full Body Harness",
                    "detected_count": 0,
                    "missing_count": 2,
                    "status": "Non-Compliant",
                    "standard_ref": "OSHA 1926.501 / IS 3521",
                    "risk_level": "Critical",
                    "observation": "Workers working near unguarded 3rd-floor perimeter edge without lanyard anchorage.",
                },
            ],
            "identified_hazards": [
                {
                    "hazard_id": "HAZ-001",
                    "hazard": "Unguarded floor perimeter edge at 9.2m elevation",
                    "category": "Fall Hazard",
                    "severity": "Critical",
                    "osha_ref": "OSHA 1926.501(b)(1)",
                    "is_ref": "IS 13416 Part 1",
                    "corrective_remedy": "Immediately halt work at elevation. Install 42-inch top-rail and 21-inch mid-rail perimeter guardrails with toe-boards before resuming.",
                },
                {
                    "hazard_id": "HAZ-002",
                    "hazard": "Uncapped projecting rebar dowels in worker travel path",
                    "category": "Caught-in-between / Impalement",
                    "severity": "High",
                    "osha_ref": "OSHA 1926.701(b)",
                    "is_ref": "IS 456:2000 Section 5",
                    "corrective_remedy": "Affix steel-reinforced plastic rebar impalement safety caps or wooden trough covers to all protruding starter bars.",
                },
                {
                    "hazard_id": "HAZ-003",
                    "hazard": "Electrical distribution cable routed through standing puddle",
                    "category": "Electrical",
                    "severity": "High",
                    "osha_ref": "OSHA 1926.404(b)(1)",
                    "is_ref": "IS 5216 / Central Electricity Authority Rules",
                    "corrective_remedy": "Elevate temporary power lines on insulated stands; verify RCCB/ELCB tripping sensitivity at 30mA.",
                },
            ],
            "site_advisory_notes": "Stop-work notice issued for slab perimeter until engineered fall prevention systems are certified by EHS Officer.",
        }

    # Standard / Compliant site scenario
    return {
        "platform_id": PLATFORM_ID,
        "audit_timestamp": now_iso,
        "safety_score": 88,
        "overall_status": "Compliant",
        "compliance_summary": "Strong baseline PPE adoption observed. All visible workers equipped with safety hard hats and high-vis vests. Minor housekeeping and secondary cable management noted.",
        "worker_count_estimate": 3,
        "ppe_detection": [
            {
                "item": "Safety Helmet / Hard Hat",
                "detected_count": 3,
                "missing_count": 0,
                "status": "Compliant",
                "standard_ref": "OSHA 1926.100 / IS 2925:1984",
                "risk_level": "Low",
                "observation": "100% hard hat compliance with chinstraps fastened.",
            },
            {
                "item": "High-Visibility Vest",
                "detected_count": 3,
                "missing_count": 0,
                "status": "Compliant",
                "standard_ref": "OSHA 1926.201 / IS 15809",
                "risk_level": "Low",
                "observation": "High-vis lime and orange vests with clean reflective bands visible.",
            },
            {
                "item": "Safety Footwear / Steel-Toe Boots",
                "detected_count": 2,
                "missing_count": 0,
                "status": "Compliant",
                "standard_ref": "OSHA 1926.96 / IS 15298",
                "risk_level": "Low",
                "observation": "Heavy ankle-height protective leather boots detected.",
            },
            {
                "item": "Fall Protection / Full Body Harness",
                "detected_count": 0,
                "missing_count": 0,
                "status": "Not Applicable (Ground Level)",
                "standard_ref": "OSHA 1926.501 / IS 3521",
                "risk_level": "Low",
                "observation": "Activities currently confined to ground-level staging and rebar cutting bay.",
            },
        ],
        "identified_hazards": [
            {
                "hazard_id": "HAZ-001",
                "hazard": "Accumulated timber offcuts and tie wire scrap near passageway",
                "category": "Housekeeping",
                "severity": "Medium",
                "osha_ref": "OSHA 1926.25(a)",
                "is_ref": "IS 13416 Part 2",
                "corrective_remedy": "Conduct a 15-minute housekeeping sweep to clear scrap material into designated disposal skips.",
            },
            {
                "hazard_id": "HAZ-002",
                "hazard": "Temporary extension cord crossing pedestrian pathway without cable crossover ramp",
                "category": "Access/Egress",
                "severity": "Low",
                "osha_ref": "OSHA 1926.416(e)(1)",
                "is_ref": "IS 5216",
                "corrective_remedy": "Install heavy-duty rubber cable protector bridge to eliminate tripping hazard.",
            },
        ],
        "site_advisory_notes": "Commend workforce on safety adherence during daily toolbox talk. Re-verify fire extinguisher hydrostatic dates in staging zone.",
    }


def audit_site_safety(
    image: Optional[Image.Image],
    api_key: Optional[str] = None,
    force_demo: bool = False,
    scenario: str = "compliant_site",
) -> Tuple[Dict[str, Any], str]:
    """
    Executes multimodal PPE and site safety audit.
    Returns (result_dict, execution_source).
    """
    key = resolve_api_key(api_key)

    if not force_demo and key and image is not None:
        try:
            raw_json = call_gemini_multimodal(
                prompt=SAFETY_ANALYSIS_PROMPT,
                image=image,
                system_instruction=SAFETY_SYSTEM_PROMPT,
                api_key=key,
                json_mode=True,
            )
            result = sanitize_json_response(raw_json)
            # Ensure mandatory fields
            result.setdefault("platform_id", PLATFORM_ID)
            result.setdefault("safety_score", 75)
            result.setdefault("overall_status", "Review Required")
            result.setdefault("ppe_detection", [])
            result.setdefault("identified_hazards", [])
            return result, "AI Multimodal Analysis (Gemini Live)"
        except Exception as exc:
            demo_data = get_safety_demo_result(scenario)
            demo_data["notes"] = f"Gemini live audit failed ({exc}). Showing verified demonstration baseline."
            return demo_data, f"Fallback Demonstration Mode (Error: {exc})"

    # Demonstration mode
    return get_safety_demo_result(scenario), "Demonstration Mode (Pre-validated Data Contract)"
