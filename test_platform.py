"""
Unit & Integration Test Suite - Multimodal Construction Intelligence Platform
Tests formulas, JSON contracts, INR formatting, weather advisories, and AI fallbacks.
Platform ID: 6ac4c98d1dcde6d7857c1642
"""

import pytest
from modules.planning_valuation import (
    format_inr,
    get_milestone_stage,
    calculate_project_plan,
)
from modules.safety_audit import (
    get_safety_demo_result,
    PLATFORM_ID,
)
from modules.crack_diagnostics import (
    get_crack_demo_result,
)
from modules.architectural_render import (
    build_architectural_prompt,
    generate_pollinations_url,
)
from modules.weather_assistant import (
    WEATHER_PROTOCOLS,
    query_engineering_assistant,
)
from modules.ai_engine import (
    sanitize_json_response,
)


def test_format_inr():
    assert format_inr(15000000) == "₹1.50 Cr"
    assert format_inr(100000000) == "₹10.00 Cr"
    assert format_inr(450000) == "₹4.50 Lakhs"
    assert format_inr(75000) == "₹75,000"
    assert format_inr(0) == "₹0"


def test_milestone_stages():
    stage10, _ = get_milestone_stage(10)
    assert "Substructure" in stage10

    stage35, _ = get_milestone_stage(35)
    assert "Superstructure" in stage35

    stage65, _ = get_milestone_stage(65)
    assert "MEP" in stage65

    stage85, _ = get_milestone_stage(85)
    assert "Façade" in stage85 or "Finishes" in stage85

    stage98, _ = get_milestone_stage(98)
    assert "Commissioning" in stage98 or "Handover" in stage98


def test_calculate_project_plan():
    plan = calculate_project_plan(
        structure_type="Residential High-Rise (RCC Shear Wall)",
        built_up_sqft=10000,
        location_tier="Tier 1 (Mumbai, Bengaluru, Delhi-NCR, Hyderabad, Chennai)",
        completion_percent=50,
        finish_level="Standard",
        contingency_percent=10.0,
    )
    assert plan["platform_id"] == PLATFORM_ID
    assert "financial_summary" in plan
    fin = plan["financial_summary"]
    assert fin["total_estimated_budget_inr"] > 0
    assert fin["capex_incurred_inr"] == round(fin["total_estimated_budget_inr"] * 0.5)
    assert fin["current_asset_valuation_inr"] > fin["capex_incurred_inr"]
    assert "Cr" in fin["formatted_total_budget"] or "Lakhs" in fin["formatted_total_budget"]

    # Material tests
    mat = plan["material_requirements"]
    assert mat["steel"]["kilograms"] == 42000  # 10000 * 4.2
    assert mat["steel"]["metric_tonnes"] == 42.0
    assert mat["cement"]["standard_bags_50kg"] == 4200  # 10000 * 0.42


def test_safety_audit_contract():
    result = get_safety_demo_result("compliant_site")
    assert result["platform_id"] == PLATFORM_ID
    assert 0 <= result["safety_score"] <= 100
    assert result["overall_status"] in ["Compliant", "Review Required", "Action Required", "Critical Non-Compliance"]
    assert len(result["ppe_detection"]) >= 4
    for item in result["ppe_detection"]:
        assert "item" in item
        assert "status" in item
        assert "standard_ref" in item
        assert "risk_level" in item

    assert len(result["identified_hazards"]) >= 1
    for h in result["identified_hazards"]:
        assert "hazard" in h
        assert "severity" in h
        assert "corrective_remedy" in h


def test_crack_diagnostics_contract():
    for defect in ["Structural Shear", "Spalling", "Hairline"]:
        diag = get_crack_demo_result(defect)
        assert diag["platform_id"] == PLATFORM_ID
        assert diag["defect_type"] == defect
        assert diag["estimated_crack_width_mm"] > 0
        assert diag["severity"] in ["Low", "Moderate", "High", "Critical"]
        assert len(diag["root_causes"]) >= 2
        assert len(diag["recommended_engineering_repairs"]) >= 2
        assert len(diag["non_destructive_testing_advised"]) >= 1


def test_architectural_render_prompt_and_url():
    prompt = build_architectural_prompt(
        structure_type="Commercial Office Tower (Grade A)",
        built_up_sqft=50000,
        location_tier="Tier 1 (Mumbai, Bengaluru, Delhi-NCR, Hyderabad, Chennai)",
    )
    assert "Commercial Office Tower" in prompt
    assert "50,000" in prompt
    url = generate_pollinations_url(prompt, seed=99)
    assert url.startswith("https://image.pollinations.ai/prompt/")
    assert "seed=99" in url
    assert "model=flux" in url


def test_weather_protocols():
    assert "Normal / Favorable (22°C - 30°C, Calm)" in WEATHER_PROTOCOLS
    assert "High Wind (> 38 km/h / 24 mph / Gale Alert)" in WEATHER_PROTOCOLS
    wind_proto = WEATHER_PROTOCOLS["High Wind (> 38 km/h / 24 mph / Gale Alert)"]
    assert "MANDATORY SUSPENSION" in wind_proto["crane_status"]


def test_offline_engineering_assistant():
    q_curing = "What is the minimum curing time for concrete under IS 456?"
    ans = query_engineering_assistant(q_curing, [])
    assert "7 days" in ans or "IS 456" in ans

    q_crane = "At what wind speed should tower crane operations stop?"
    ans_crane = query_engineering_assistant(q_crane, [])
    assert "38 km/h" in ans_crane or "wind" in ans_crane.lower()


def test_json_sanitizer():
    fenced_json = "```json\n{\"safety_score\": 90, \"overall_status\": \"Compliant\"}\n```"
    parsed = sanitize_json_response(fenced_json)
    assert parsed["safety_score"] == 90

    prefix_json = "Here is the result:\n{\"defect_type\": \"Hairline\"}\nHope this helps!"
    parsed_pref = sanitize_json_response(prefix_json)
    assert parsed_pref["defect_type"] == "Hairline"
