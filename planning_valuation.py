"""
Project Planning & Real Estate Valuation Module (Epic 3 & Epic 4)
Calculates construction Capex, project budgets, Indian real estate market valuation in INR,
and structural material requirements (steel & cement) based on CPWD / IS standards.
Platform ID: 6ac4c98d1dcde6d7857c1642
"""

import datetime
from typing import Any, Dict, List, Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PLATFORM_ID = "6ac4c98d1dcde6d7857c1642"

# 2025-2026 Indian Market Base Construction Rates (₹ / sq ft of built-up area)
TIER_BASE_RATES = {
    "Tier 1 (Mumbai, Bengaluru, Delhi-NCR, Hyderabad, Chennai)": {
        "Economy": 2200,
        "Standard": 2900,
        "Premium": 3950,
        "Ultra-Luxury": 5400,
    },
    "Tier 2 (Pune, Ahmedabad, Kolkata, Kochi, Jaipur, Chandigarh)": {
        "Economy": 1850,
        "Standard": 2400,
        "Premium": 3300,
        "Ultra-Luxury": 4600,
    },
    "Tier 3 (Coimbatore, Indore, Nagpur, Lucknow, Bhubaneswar, Surat)": {
        "Economy": 1550,
        "Standard": 2000,
        "Premium": 2850,
        "Ultra-Luxury": 3900,
    },
}

# Structure type complexity multipliers & structural material coefficients
STRUCTURE_PROFILES = {
    "Residential High-Rise (RCC Shear Wall)": {
        "cost_multiplier": 1.05,
        "steel_kg_per_sqft": 4.2,  # Fe 500D TMT rebar
        "cement_bags_per_sqft": 0.42,  # 50-kg bags
        "market_rate_tier1": 11500,  # ₹ / sq ft saleable
        "market_rate_tier2": 6800,
        "market_rate_tier3": 4400,
    },
    "Luxury Villa / Gated Community": {
        "cost_multiplier": 1.15,
        "steel_kg_per_sqft": 4.5,
        "cement_bags_per_sqft": 0.44,
        "market_rate_tier1": 16000,
        "market_rate_tier2": 9500,
        "market_rate_tier3": 5800,
    },
    "Commercial Office Tower (Grade A)": {
        "cost_multiplier": 1.22,
        "steel_kg_per_sqft": 5.0,
        "cement_bags_per_sqft": 0.45,
        "market_rate_tier1": 14500,
        "market_rate_tier2": 8200,
        "market_rate_tier3": 5100,
    },
    "Industrial PEB Warehouse / Logistics Park": {
        "cost_multiplier": 0.82,
        "steel_kg_per_sqft": 3.2,
        "cement_bags_per_sqft": 0.30,
        "market_rate_tier1": 5500,
        "market_rate_tier2": 3800,
        "market_rate_tier3": 2600,
    },
    "Institutional / Healthcare Facility": {
        "cost_multiplier": 1.30,
        "steel_kg_per_sqft": 5.2,
        "cement_bags_per_sqft": 0.46,
        "market_rate_tier1": 13500,
        "market_rate_tier2": 7900,
        "market_rate_tier3": 4900,
    },
}


def format_inr(value: float) -> str:
    """
    Format monetary amounts into standard Indian currency denominations (Crores / Lakhs).
    Examples:
      15,000,000 -> ₹1.50 Cr
      450,000 -> ₹4.50 Lakhs
      75,000 -> ₹75,000
    """
    val = float(value)
    abs_val = abs(val)
    sign = "-" if val < 0 else ""

    if abs_val >= 10_000_000:  # 1 Crore = 10 Million
        return f"{sign}₹{abs_val / 10_000_000:.2f} Cr"
    elif abs_val >= 100_000:  # 1 Lakh = 100 Thousand
        return f"{sign}₹{abs_val / 100_000:.2f} Lakhs"
    else:
        return f"{sign}₹{abs_val:,.0f}"


def get_milestone_stage(completion_pct: float) -> Tuple[str, str]:
    """Map completion percentage to CPWD construction milestone stages."""
    if completion_pct <= 20:
        return (
            "Substructure & Foundation",
            "Site clearance, excavation, piling/raft foundation, and plinth beam casting.",
        )
    elif completion_pct <= 50:
        return (
            "Superstructure RCC Framework",
            "Columns, shear walls, beam-slab deck shuttering, reinforcement tying, and concrete pouring.",
        )
    elif completion_pct <= 75:
        return (
            "Masonry, MEP & Internal Services",
            "Autoclaved aerated concrete (AAC) blockwork, electrical conduit, plumbing risers, HVAC ducting, and internal plaster.",
        )
    elif completion_pct <= 95:
        return (
            "Façade, Architectural Finishes & Elevators",
            "Curtain wall glazing, vitrified tiling/flooring, external paint, elevator install, and sanitary ware.",
        )
    else:
        return (
            "Testing, Commissioning & Handover",
            "Fire NOC compliance, MEP balancing, occupancy certificate (OC) acquisition, and client snagging.",
        )


def calculate_project_plan(
    structure_type: str,
    built_up_sqft: float,
    location_tier: str,
    completion_percent: float,
    finish_level: str = "Standard",
    contingency_percent: float = 10.0,
) -> Dict[str, Any]:
    """
    Computes complete project financial planning, asset valuation,
    material requirements (steel & cement), and trade breakdown.
    """
    # Safe defaults
    tier_data = TIER_BASE_RATES.get(location_tier, list(TIER_BASE_RATES.values())[0])
    base_rate = tier_data.get(finish_level, 2900)

    profile = STRUCTURE_PROFILES.get(
        structure_type, list(STRUCTURE_PROFILES.values())[0]
    )
    cost_multiplier = profile["cost_multiplier"]

    # Budget calculations
    contingency_factor = 1.0 + (contingency_percent / 100.0)
    effective_rate_per_sqft = base_rate * cost_multiplier
    total_budget = built_up_sqft * effective_rate_per_sqft * contingency_factor
    capex_incurred = total_budget * (completion_percent / 100.0)

    # Material requirement calculations (CPWD / IS structural benchmarks)
    steel_kg = built_up_sqft * profile["steel_kg_per_sqft"]
    steel_mt = steel_kg / 1000.0
    steel_quintals = steel_kg / 100.0

    cement_bags = built_up_sqft * profile["cement_bags_per_sqft"]
    cement_mt = (cement_bags * 50.0) / 1000.0

    # Real Estate Market Valuation
    # Determined by market rate, location tier, built-up sqft, and construction stage progression
    if "Tier 1" in location_tier:
        market_rate_sqft = profile["market_rate_tier1"]
    elif "Tier 2" in location_tier:
        market_rate_sqft = profile["market_rate_tier2"]
    else:
        market_rate_sqft = profile["market_rate_tier3"]

    # Valuation models land equity baseline (60% to 70%) plus finished improvements (up to 100%)
    stage_valuation_factor = 0.65 + (completion_percent / 100.0) * 0.35
    total_market_valuation = built_up_sqft * market_rate_sqft * stage_valuation_factor

    milestone_title, milestone_desc = get_milestone_stage(completion_percent)

    # Trade budget breakdown for chart
    trade_breakdown = {
        "RCC Structural Works & Rebar": round(total_budget * 0.38),
        "Masonry & Plastering": round(total_budget * 0.14),
        "MEP (Electrical, Plumbing, HVAC)": round(total_budget * 0.18),
        "Finishes, Façade & Flooring": round(total_budget * 0.20),
        "Contingency & Statutory Permits": round(total_budget * (contingency_percent / 100.0)),
    }

    result = {
        "platform_id": PLATFORM_ID,
        "calculation_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "input_parameters": {
            "structure_type": structure_type,
            "built_up_sqft": built_up_sqft,
            "location_tier": location_tier,
            "finish_level": finish_level,
            "completion_percent": completion_percent,
            "contingency_percent": contingency_percent,
        },
        "financial_summary": {
            "total_estimated_budget_inr": round(total_budget),
            "capex_incurred_inr": round(capex_incurred),
            "current_asset_valuation_inr": round(total_market_valuation),
            "formatted_total_budget": format_inr(total_budget),
            "formatted_capex_incurred": format_inr(capex_incurred),
            "formatted_asset_valuation": format_inr(total_market_valuation),
            "effective_rate_per_sqft_inr": round(effective_rate_per_sqft),
            "market_rate_per_sqft_inr": market_rate_sqft,
        },
        "material_requirements": {
            "steel": {
                "metric_tonnes": round(steel_mt, 1),
                "quintals": round(steel_quintals, 1),
                "kilograms": round(steel_kg),
                "norm_reference": f"{profile['steel_kg_per_sqft']} kg/sqft (Fe 500D TMT)",
            },
            "cement": {
                "standard_bags_50kg": round(cement_bags),
                "metric_tonnes": round(cement_mt, 1),
                "norm_reference": f"{profile['cement_bags_per_sqft']} bags/sqft (OPC 53 / PPC)",
            },
        },
        "milestone_tracker": {
            "completion_percent": completion_percent,
            "current_stage": milestone_title,
            "stage_description": milestone_desc,
        },
        "trade_breakdown_inr": trade_breakdown,
    }

    return result


def create_financial_bar_chart(plan_data: Dict[str, Any]) -> go.Figure:
    """Generate high-contrast Plotly bar chart comparing Budget, Capex, and Valuation."""
    fin = plan_data["financial_summary"]
    categories = ["Total Budget", "CAPEX Incurred", "Current Valuation"]
    values = [
        fin["total_estimated_budget_inr"],
        fin["capex_incurred_inr"],
        fin["current_asset_valuation_inr"],
    ]
    formatted = [
        fin["formatted_total_budget"],
        fin["formatted_capex_incurred"],
        fin["formatted_asset_valuation"],
    ]
    colors = ["#3b82f6", "#f59e0b", "#10b981"]

    fig = go.Figure(
        data=[
            go.Bar(
                x=categories,
                y=values,
                text=formatted,
                textposition="auto",
                marker=dict(color=colors, line=dict(color="#1e293b", width=1.5)),
            )
        ]
    )

    fig.update_layout(
        title="<b>Project Financial Overview (INR)</b>",
        xaxis_title="Financial Metric",
        yaxis_title="Amount in INR (₹)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=13),
        margin=dict(l=40, r=40, t=50, b=40),
        height=380,
    )
    return fig


def create_trade_pie_chart(plan_data: Dict[str, Any]) -> go.Figure:
    """Generate Plotly donut chart showing trade cost allocation."""
    trades = plan_data["trade_breakdown_inr"]
    labels = list(trades.keys())
    values = list(trades.values())

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.45,
                textinfo="label+percent",
                marker=dict(colors=["#2563eb", "#0ea5e9", "#10b981", "#f59e0b", "#8b5cf6"]),
            )
        ]
    )

    fig.update_layout(
        title="<b>Trade Cost Allocation (CPWD Benchmark)</b>",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12),
        margin=dict(l=20, r=20, t=50, b=20),
        height=380,
        showlegend=False,
    )
    return fig
