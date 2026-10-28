"""
Multimodal Construction Intelligence Platform
Turnkey Master Application (Skill Wallet Capstone Project 1)
Platform ID: 6ac4c98d1dcde6d7857c1642
Category: Generative AI | Real Estate Decision Support

Epics Covered:
- Pre-requisites & Epic 1: Requirements, Environment & Configuration
- Epic 2: PPE Safety Vision Audit & Structural Crack Diagnostics
- Epic 3: Project Planning, INR Real Estate Valuation & 3D Architectural Renderings
- Epic 4: Multimodal AI & Strict JSON Data Contracts
- Epic 5: Weather-Aware Advisory Protocols & Interactive Multi-turn Site Assistant
- Epic 6: Modern UI/UX, Automated Pytest Verification & Cloud Deployment Readiness
"""

import json
import os
from typing import Any, Dict, Optional
import pandas as pd
from PIL import Image
import streamlit as st

# Import Core Domain Modules
from modules.ai_engine import (
    DEMO_MODE,
    GEMINI_MODE,
    SUPPORTED_MODELS,
    resolve_api_key,
)
from modules.safety_audit import (
    PLATFORM_ID,
    audit_site_safety,
    get_safety_demo_result,
)
from modules.crack_diagnostics import (
    diagnose_concrete_defect,
    get_crack_demo_result,
)
from modules.planning_valuation import (
    STRUCTURE_PROFILES,
    TIER_BASE_RATES,
    calculate_project_plan,
    create_financial_bar_chart,
    create_trade_pie_chart,
    format_inr,
)
from modules.architectural_render import (
    LIGHTING_PRESETS,
    STYLE_PRESETS,
    build_architectural_prompt,
    fetch_rendered_image,
    generate_pollinations_url,
)
from modules.weather_assistant import (
    WEATHER_PROTOCOLS,
    query_engineering_assistant,
)

# Page Configuration (Emoji-free)
st.set_page_config(
    page_title="Multimodal Construction Intelligence Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Modern Custom CSS Styling
st.markdown(
    """
    <style>
    /* Global Typography & Spacing */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .block-container {
        max-width: 1440px;
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
    }
    
    /* Hero Header */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f766e 100%);
        border: 1px solid #334155;
        border-radius: 18px;
        padding: 1.8rem 2.2rem;
        color: #ffffff;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .hero-subtitle {
        font-size: 0.98rem;
        color: #94a3b8;
        margin-top: 0.4rem;
        margin-bottom: 0.8rem;
    }
    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 0.6rem;
    }
    .hero-pill {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #cbd5e1;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 14px 18px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }

    /* Badges & Pills */
    .badge-pass {
        background-color: #064e3b;
        color: #6ee7b7;
        border: 1px solid #059669;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-warn {
        background-color: #78350f;
        color: #fde68a;
        border: 1px solid #d97706;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-fail {
        background-color: #7f1d1d;
        color: #fca5a5;
        border: 1px solid #dc2626;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-neutral {
        background-color: #1e293b;
        color: #94a3b8;
        border: 1px solid #475569;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }

    /* Card Panels */
    .audit-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .audit-card h4 {
        margin-top: 0;
        margin-bottom: 0.6rem;
        color: #f8fafc;
        font-weight: 600;
    }

    /* Status Pill Containers */
    .pill-container {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        margin-top: 0.4rem;
        margin-bottom: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_image_safely(file_or_path) -> Optional[Image.Image]:
    """Safely open, format, and convert an uploaded file or path to PIL RGB."""
    if not file_or_path:
        return None
    try:
        img = Image.open(file_or_path).convert("RGB")
        return img
    except Exception as exc:
        st.error(f"Error loading image: {exc}")
        return None


def export_json_button(data: Dict[str, Any], filename: str, label: str = "Download JSON Report"):
    """Render a clean Streamlit JSON download button."""
    json_bytes = json.dumps(data, indent=2, ensure_ascii=False)
    st.download_button(
        label=label,
        data=json_bytes,
        file_name=filename,
        mime="application/json",
        use_container_width=True,
    )


# -------------------------------------------------------------
# SIDEBAR: Configuration, Security, Platform Metadata & Epics
# -------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; padding-bottom: 0.8rem;">
            <h2 style="margin: 0.2rem 0; font-size: 1.25rem; font-weight: 800;">Construction Intelligence</h2>
            <span style="font-size: 0.78rem; color: #94a3b8; font-family: monospace;">ID: 6ac4c98d1dcde6d7857c1642</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### AI Engine Settings")
    provider_choice = st.selectbox(
        "Execution Engine",
        [DEMO_MODE, GEMINI_MODE],
        index=0,
        help="Demonstration mode runs pre-validated structural contracts without an external key. Choose Google Gemini for live multimodal inspection.",
    )

    api_key_input = ""
    selected_model = "gemini-2.5-flash"

    if provider_choice == GEMINI_MODE:
        env_key = os.getenv("GEMINI_API_KEY", "")
        api_key_input = st.text_input(
            "Gemini API Key",
            value=env_key,
            type="password",
            placeholder="AIzaSy...",
            help="Your API key is kept in temporary memory and never persisted to disk or repository.",
        )
        selected_model = st.selectbox("Vision & Chat Model", SUPPORTED_MODELS, index=0)
        if not api_key_input:
            st.warning("No key supplied. Falling back gracefully to demonstration mode.")
    else:
        st.info("Demo Mode Active: Testing with pre-validated engineering contracts and local knowledge graph.")

    st.session_state["api_key"] = api_key_input
    st.session_state["provider"] = provider_choice
    st.session_state["selected_model"] = selected_model

    st.markdown("---")
    st.markdown("### Platform Epics Coverage")
    with st.expander("Kanban Epics (1 to 6)", expanded=False):
        st.markdown(
            """
            - **Epic 1:** Requirements & Environment (`Python 3.9+`, Pytest)
            - **Epic 2:** PPE Safety Vision & Crack Diagnostics (OSHA/IS 456)
            - **Epic 3:** Project Planning & INR Valuation (CPWD Steel/Cement)
            - **Epic 4:** Multimodal AI & Strict JSON Contracts
            - **Epic 5:** Site Chatbot & Weather Safety Advisory
            - **Epic 6:** Responsive Interface & Streamlit Cloud 1-Click Deploy
            """
        )

    st.markdown("### Standards Compliance")
    with st.expander("Governing Codes", expanded=False):
        st.markdown(
            """
            - **IS 456:2000:** Plain and Reinforced Concrete
            - **OSHA 1926:** Safety Regulations for Construction
            - **IS 2925 / IS 3521:** Industrial Helmets & Fall Harnesses
            - **CPWD Plinth Area Rates:** Structural Estimations
            """
        )

    st.markdown("---")
    st.caption("Capstone Project 1 · Skill Wallet · Dec 2026")


# -------------------------------------------------------------
# MAIN HEADER BANNER
# -------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-title">
            Multimodal Construction Intelligence Platform
        </div>
        <div class="hero-subtitle">
            Autonomous site safety auditing, concrete crack forensic triage, CPWD material planning, INR real estate valuation, and dynamic weather advisory.
        </div>
        <div class="hero-pills">
            <span class="hero-pill">Platform ID: {PLATFORM_ID}</span>
            <span class="hero-pill">Generative AI | Real Estate Support</span>
            <span class="hero-pill">Engine: {provider_choice.split()[0]}</span>
            <span class="hero-pill">Currency: INR (Lakhs & Crores)</span>
            <span class="hero-pill">Codes: OSHA 1926 & IS 456:2000</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# CORE APPLICATION TABS (Emoji-free)
# -------------------------------------------------------------
tab_safety, tab_cracks, tab_planning, tab_weather, tab_architecture = st.tabs(
    [
        "Tab 1: Site Safety & PPE Audit",
        "Tab 2: Crack Diagnostics",
        "Tab 3: Planning & Valuation",
        "Tab 4: Daily Site Assistant & Weather Advisory",
        "Tab 5: Architecture & Data Contracts",
    ]
)


# =============================================================
# TAB 1: SITE SAFETY & PPE AUDIT (EPIC 2 & EPIC 4)
# =============================================================
with tab_safety:
    st.subheader("Site Safety & Worker PPE Compliance Audit (OSHA 1926 & IS 456)")
    st.markdown(
        "Upload site surveillance photos to evaluate hard hats, high-visibility apparel, steel-toe footwear, "
        "and fall arrest harnesses against **OSHA 1926 (Subparts E, M)** and **IS 2925 / IS 3521** specifications."
    )

    col_up, col_action = st.columns([3, 2])
    with col_up:
        uploaded_safety_img = st.file_uploader(
            "Upload Construction Site Photo (JPG, PNG, WebP)",
            type=["jpg", "jpeg", "png", "webp"],
            key="safety_uploader",
        )
    with col_action:
        st.markdown("**Quick Demo Presets:**")
        preset_choice = st.radio(
            "Demonstration Scenario:",
            ["Compliant Structural Site", "High-Risk Perimeter Workzone"],
            index=0,
            horizontal=True,
        )
        use_sample = st.button("Load Sample Site Photo", use_container_width=True)

    # Resolve active image
    active_safety_img = None
    if use_sample:
        sample_path = "sample_data/sample_ppe_site.jpg"
        if os.path.exists(sample_path):
            active_safety_img = Image.open(sample_path)
            st.session_state["current_safety_image"] = active_safety_img
    elif uploaded_safety_img:
        active_safety_img = load_image_safely(uploaded_safety_img)
        st.session_state["current_safety_image"] = active_safety_img
    elif "current_safety_image" in st.session_state:
        active_safety_img = st.session_state["current_safety_image"]

    if active_safety_img is not None:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.image(active_safety_img, caption="Analyzed Workzone Scene", use_container_width=True)
        with c2:
            st.markdown("#### Inspection Trigger")
            st.write("Execute multimodal visual parsing for personal protective equipment and active site hazards.")
            run_audit = st.button("Execute Safety & PPE Audit", type="primary", use_container_width=True)

            if run_audit or "safety_audit_result" not in st.session_state:
                with st.spinner("Analyzing site imagery against OSHA & IS standards..."):
                    force_demo = (provider_choice == DEMO_MODE) or (not api_key_input)
                    demo_scenario = "high_risk" if "High-Risk" in preset_choice else "compliant_site"
                    result, source = audit_site_safety(
                        image=active_safety_img,
                        api_key=api_key_input,
                        force_demo=force_demo,
                        scenario=demo_scenario,
                    )
                    st.session_state["safety_audit_result"] = result
                    st.session_state["safety_audit_source"] = source

            if "safety_audit_result" in st.session_state:
                res = st.session_state["safety_audit_result"]
                src = st.session_state.get("safety_audit_source", "Audit")

                st.caption(f"**Execution Source:** {src}")
                score = int(res.get("safety_score", 0))

                # Status pill indicator
                status_str = res.get("overall_status", "Review Required")
                if "Compliant" in status_str and "Critical" not in status_str and "Non" not in status_str:
                    badge_html = f"<span class='badge-pass'>[PASS] {status_str}</span>"
                elif "Non-Compliance" in status_str or "Critical" in status_str:
                    badge_html = f"<span class='badge-fail'>[CRITICAL] {status_str}</span>"
                else:
                    badge_html = f"<span class='badge-warn'>[REVIEW] {status_str}</span>"

                st.markdown(f"**Overall Compliance:** {badge_html}", unsafe_allow_html=True)
                st.progress(score / 100.0, text=f"Safety Index Score: {score}/100")

    # Render Audit Findings
    if "safety_audit_result" in st.session_state:
        res = st.session_state["safety_audit_result"]

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Safety Score", f"{res.get('safety_score', 0)}/100")
        m2.metric("Overall Status", res.get("overall_status", "N/A"))
        m3.metric("Workers Identified", res.get("worker_count_estimate", "1+"))
        m4.metric("Hazards Flagged", len(res.get("identified_hazards", [])))

        st.info(f"**Executive Summary:** {res.get('compliance_summary', 'Audit executed.')}")

        st.markdown("### Personal Protective Equipment (PPE) Checklist")
        ppe_list = res.get("ppe_detection", [])
        if ppe_list:
            df_ppe = pd.DataFrame(ppe_list)
            # Reorder columns for optimal presentation
            cols_order = [c for c in ["item", "status", "standard_ref", "risk_level", "observation"] if c in df_ppe.columns]
            st.dataframe(df_ppe[cols_order], use_container_width=True, hide_index=True)

        st.markdown("### Identified Site Hazards & Corrective Engineering Remedies")
        hazards = res.get("identified_hazards", [])
        if hazards:
            for idx, h in enumerate(hazards):
                severity = h.get("severity", "Medium")
                cat = h.get("category", "General")
                desc = h.get("hazard", "Site condition requires attention.")
                remedy = h.get("corrective_remedy", "Consult competent safety person.")
                osha_ref = h.get("osha_ref", "OSHA 1926")
                is_ref = h.get("is_ref", "IS 13416")

                border_color = "#ef4444" if severity in ["High", "Critical"] else "#f59e0b" if severity == "Medium" else "#3b82f6"
                badge_class = "badge-fail" if severity in ["High", "Critical"] else "badge-warn" if severity == "Medium" else "badge-neutral"

                st.markdown(
                    f"""
                    <div style="background: #1e293b; border-left: 5px solid {border_color}; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; border: 1px solid #334155; border-left: 5px solid {border_color};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <strong style="color: #f8fafc; font-size: 1.05rem;">{idx+1}. {cat}: {desc}</strong>
                            <span class="{badge_class}">[{severity.upper()}]</span>
                        </div>
                        <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;">
                            <span><b>Standard Citations:</b> {osha_ref} | {is_ref}</span>
                        </div>
                        <div style="background: rgba(15, 23, 42, 0.6); padding: 8px 12px; border-radius: 6px; color: #e2e8f0; font-size: 0.9rem;">
                            <b>Actionable Remedy:</b> {remedy}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if res.get("site_advisory_notes"):
            st.warning(f"**Safety Officer Note:** {res['site_advisory_notes']}")

        col_dl, col_raw = st.columns([1, 1])
        with col_dl:
            export_json_button(res, f"safety_audit_report_{PLATFORM_ID}.json")
        with col_raw:
            with st.expander("View Raw JSON Contract (Epic 4)", expanded=False):
                st.json(res)


# =============================================================
# TAB 2: CRACK DIAGNOSTICS & STRUCTURAL INTEGRITY (EPIC 2 & 4)
# =============================================================
with tab_cracks:
    st.subheader("Concrete Crack Diagnostics & Structural Integrity (IS 456 / ACI 224R)")
    st.markdown(
        "Upload high-resolution concrete or masonry surface photos to classify defect typology "
        "(Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling), estimate width (mm), "
        "and generate structural rehabilitation blueprints."
    )

    c_c1, c_c2 = st.columns([3, 2])
    with c_c1:
        uploaded_crack_img = st.file_uploader(
            "Upload Concrete Surface Photo (JPG, PNG, WebP)",
            type=["jpg", "jpeg", "png", "webp"],
            key="crack_uploader",
        )
        crack_context = st.text_input(
            "Engineering Context (Optional):",
            placeholder="e.g. RCC transfer girder at Basement 1, age 4 years, observed after formwork de-shuttering",
        )
    with c_c2:
        st.markdown("**Sample Crack Defects:**")
        sample_defect_preset = st.radio(
            "Defect Archetype:",
            ["Structural Shear Crack (Beam)", "Concrete Spalling & Corroded Rebar", "Hairline Plaster Curing Crack"],
            index=0,
        )
        load_crack_sample = st.button("Load Sample Crack Photo", use_container_width=True)

    active_crack_img = None
    if load_crack_sample:
        if "Shear" in sample_defect_preset:
            p = "sample_data/sample_crack_shear.jpg"
        elif "Spalling" in sample_defect_preset:
            p = "sample_data/sample_crack_shear.jpg"
        else:
            p = "sample_data/sample_crack_hairline.jpg"

        if os.path.exists(p):
            active_crack_img = Image.open(p)
            st.session_state["current_crack_image"] = active_crack_img
    elif uploaded_crack_img:
        active_crack_img = load_image_safely(uploaded_crack_img)
        st.session_state["current_crack_image"] = active_crack_img
    elif "current_crack_image" in st.session_state:
        active_crack_img = st.session_state["current_crack_image"]

    if active_crack_img is not None:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.image(active_crack_img, caption="Evaluated Concrete Element", use_container_width=True)
        with c2:
            st.markdown("#### Diagnostic Execution")
            st.write("Run forensic evaluation for crack width, root cause isolation, and repair protocols.")
            run_crack = st.button("Perform Crack & Structural Diagnostic", type="primary", use_container_width=True)

            if run_crack or "crack_diagnostic_result" not in st.session_state:
                with st.spinner("Classifying structural failure modes & crack propagation..."):
                    force_demo = (provider_choice == DEMO_MODE) or (not api_key_input)
                    if "Spalling" in sample_defect_preset:
                        demo_type = "Spalling"
                    elif "Hairline" in sample_defect_preset:
                        demo_type = "Hairline"
                    else:
                        demo_type = "Structural Shear"

                    c_result, c_source = diagnose_concrete_defect(
                        image=active_crack_img,
                        api_key=api_key_input,
                        force_demo=force_demo,
                        demo_type=demo_type,
                        user_context=crack_context,
                    )
                    st.session_state["crack_diagnostic_result"] = c_result
                    st.session_state["crack_diagnostic_source"] = c_source

            if "crack_diagnostic_result" in st.session_state:
                c_res = st.session_state["crack_diagnostic_result"]
                c_src = st.session_state.get("crack_diagnostic_source", "Diagnostic")
                st.caption(f"**Execution Source:** {c_src}")

                defect_name = c_res.get("defect_type", "Structural Shear")
                sev = c_res.get("severity", "Moderate")
                badge_c = "badge-fail" if sev in ["High", "Critical"] else "badge-warn" if sev == "Moderate" else "badge-neutral"
                st.markdown(f"**Classification:** <span class='{badge_c}'>{defect_name.upper()} ({sev.upper()})</span>", unsafe_allow_html=True)

    # Render Crack Diagnostic Report
    if "crack_diagnostic_result" in st.session_state:
        c_res = st.session_state["crack_diagnostic_result"]

        st.markdown("---")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Defect Classification", c_res.get("defect_type", "Uncertain"))
        k2.metric("Estimated Crack Width", f"{c_res.get('estimated_crack_width_mm', 0.5):.1f} mm")
        k3.metric("Structural Element", c_res.get("structural_element", "RCC Component"))
        k4.metric("Action Urgency", c_res.get("urgency", "Engineering Review"))

        # IS 456:2000 Compliance Banner
        is_stat = c_res.get("is_456_compliance_status", "Review required")
        if "Non-Compliance" in is_stat or "Exceeds" in is_stat:
            st.error(f"IS 456:2000 Durability Compliance (Cl. 35.3.2): {is_stat}")
        else:
            st.success(f"IS 456:2000 Durability Compliance (Cl. 35.3.2): {is_stat}")

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("#### Root Cause Analysis")
            for rc in c_res.get("root_causes", []):
                st.markdown(f"- **Cause:** {rc}")

            st.markdown("#### Crack Pattern & Morphology")
            st.info(f"**Visual Pattern:** {c_res.get('crack_orientation_pattern', 'Not specified')}")

        with col_right:
            st.markdown("#### Recommended Engineering Repairs")
            for idx, rep in enumerate(c_res.get("recommended_engineering_repairs", [])):
                st.markdown(f"**Step {idx+1}:** {rep}")

            st.markdown("#### Non-Destructive Testing (NDT) Advised")
            for ndt in c_res.get("non_destructive_testing_advised", []):
                st.markdown(f"- {ndt}")

        if c_res.get("engineer_escalation_protocol"):
            st.warning(f"**Escalation Protocol:** {c_res['engineer_escalation_protocol']}")

        col_dl, col_raw = st.columns([1, 1])
        with col_dl:
            export_json_button(c_res, f"crack_diagnostic_report_{PLATFORM_ID}.json")
        with col_raw:
            with st.expander("View Raw JSON Contract (Epic 4)", expanded=False):
                st.json(c_res)


# =============================================================
# TAB 3: PLANNING, INR VALUATION & 3D RENDERING (EPIC 3 & 4)
# =============================================================
with tab_planning:
    st.subheader("Project Planning, Material Estimation & Real Estate Valuation (INR)")
    st.markdown(
        "Interactive cost engineering, capital expenditure tracking, asset market valuation, "
        "and material consumption benchmarks (TMT Steel & Cement) calibrated to Indian CPWD standards."
    )

    with st.form("planning_calculator_form"):
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            structure_choice = st.selectbox(
                "Structure Type",
                list(STRUCTURE_PROFILES.keys()),
                index=0,
            )
            built_up_area = st.number_input(
                "Built-Up Area (sq. ft.)",
                min_value=500,
                max_value=2_000_000,
                value=25_000,
                step=1_000,
            )
        with p_col2:
            location_tier = st.selectbox(
                "Indian Location Tier",
                list(TIER_BASE_RATES.keys()),
                index=0,
            )
            completion_slider = st.slider(
                "Construction Completion (%)",
                min_value=0,
                max_value=100,
                value=45,
                step=5,
            )
        with p_col3:
            finish_choice = st.selectbox(
                "Finish Specification Level",
                ["Economy", "Standard", "Premium", "Ultra-Luxury"],
                index=1,
            )
            contingency_slider = st.slider(
                "Contingency Allowance (%)",
                min_value=0,
                max_value=25,
                value=10,
                step=1,
            )

        submit_plan = st.form_submit_button("Compute Project Plan & Asset Valuation", type="primary", use_container_width=True)

    if submit_plan or "planning_result" not in st.session_state:
        plan_result = calculate_project_plan(
            structure_type=structure_choice,
            built_up_sqft=built_up_area,
            location_tier=location_tier,
            completion_percent=completion_slider,
            finish_level=finish_choice,
            contingency_percent=contingency_slider,
        )
        st.session_state["planning_result"] = plan_result

    plan = st.session_state["planning_result"]
    fin = plan["financial_summary"]
    mat = plan["material_requirements"]
    milestone = plan["milestone_tracker"]

    st.markdown("---")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Total Project Budget", fin["formatted_total_budget"], f"₹{fin['effective_rate_per_sqft_inr']}/sqft")
    f2.metric("CAPEX Incurred to Date", fin["formatted_capex_incurred"], f"{milestone['completion_percent']}% Complete")
    f3.metric("Current Asset Valuation", fin["formatted_asset_valuation"], f"₹{fin['market_rate_per_sqft_inr']}/sqft mkt")
    f4.metric("Steel Required (Fe 500D)", f"{mat['steel']['metric_tonnes']} MT", f"{mat['steel']['quintals']} Quintals")

    # Milestone Progress Bar
    st.markdown(f"#### Construction Milestone: **{milestone['current_stage']}**")
    st.progress(milestone["completion_percent"] / 100.0, text=f"{milestone['completion_percent']}% Physical Completion")
    st.caption(f"**Stage Focus:** {milestone['stage_description']}")

    # Charts: Financial Overview & Trade Breakdown
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(create_financial_bar_chart(plan), use_container_width=True)
    with chart_col2:
        st.plotly_chart(create_trade_pie_chart(plan), use_container_width=True)

    # Detailed Material Metrics
    st.markdown("### Structural Material Consumption (CPWD / IS Benchmarks)")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown(
            f"""
            <div class="audit-card">
                <h4>TMT Steel Rebar (Fe 500D)</h4>
                <p><b>Total Weight:</b> {mat['steel']['kilograms']:,} kg (<b>{mat['steel']['metric_tonnes']} Metric Tonnes</b> / {mat['steel']['quintals']} Quintals)</p>
                <p><b>Structural Consumption Norm:</b> {mat['steel']['norm_reference']}</p>
                <p style="font-size: 0.85rem; color: #94a3b8;">Compliant with IS 1786 and IS 13920 ductile seismic detailing requirements.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m_col2:
        st.markdown(
            f"""
            <div class="audit-card">
                <h4>Cement Requirements (OPC 53 / PPC)</h4>
                <p><b>Total Bags:</b> {mat['cement']['standard_bags_50kg']:,} standard 50-kg bags (<b>{mat['cement']['metric_tonnes']} Metric Tonnes</b>)</p>
                <p><b>CPWD Consumption Norm:</b> {mat['cement']['norm_reference']}</p>
                <p style="font-size: 0.85rem; color: #94a3b8;">Calibrated for M25/M30 structural RCC elements and plastering mortars.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------
    # CONCEPTUAL 3D ARCHITECTURAL RENDERING (POLLINATIONS AI / FLUX)
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Conceptual 3D Architectural Rendering (Pollinations AI / Flux Engine)")
    st.markdown(
        "Synthesize high-fidelity photorealistic architectural concept visualizations directly "
        "derived from your project's structural type, built-up area, and finish specifications."
    )

    r_c1, r_c2, r_c3 = st.columns(3)
    with r_c1:
        style_preset = st.selectbox("Architectural Design Typology", list(STYLE_PRESETS.keys()), index=0)
    with r_c2:
        lighting_preset = st.selectbox("Daylighting & Atmosphere", list(LIGHTING_PRESETS.keys()), index=0)
    with r_c3:
        seed_value = st.number_input("Variation Seed", min_value=1, max_value=999999, value=42, step=1)

    generated_prompt = build_architectural_prompt(
        structure_type=plan["input_parameters"]["structure_type"],
        built_up_sqft=plan["input_parameters"]["built_up_sqft"],
        location_tier=plan["input_parameters"]["location_tier"],
        finish_level=plan["input_parameters"]["finish_level"],
        style_preset=style_preset,
        lighting=lighting_preset,
    )

    st.text_area("Generated Photorealistic 3D Concept Prompt:", value=generated_prompt, height=90)

    render_btn = st.button("Generate 3D Concept Render (Pollinations AI Live)", type="primary")

    if render_btn or "rendered_3d_image" in st.session_state:
        if render_btn:
            with st.spinner("Calling Pollinations AI / Flux high-speed neural renderer..."):
                rendered_img, render_url, render_err = fetch_rendered_image(generated_prompt, seed=seed_value)
                st.session_state["rendered_3d_image"] = rendered_img
                st.session_state["rendered_3d_url"] = render_url
                st.session_state["rendered_3d_err"] = render_err

        rendered_img = st.session_state.get("rendered_3d_image")
        render_url = st.session_state.get("rendered_3d_url")
        render_err = st.session_state.get("rendered_3d_err")

        if rendered_img:
            st.image(rendered_img, caption="Photorealistic 3D Conceptual Render · Pollinations AI (Flux)", use_container_width=True)
            col_d1, col_d2 = st.columns([1, 1])
            with col_d1:
                st.success("3D Conceptual Architectural Render successfully synthesized.")
            with col_d2:
                st.markdown(f"[Open Direct High-Res Image URL]({render_url})")
        elif render_url:
            st.image(render_url, caption="Photorealistic 3D Conceptual Render · Pollinations AI (Flux)", use_container_width=True)
            if render_err:
                st.caption(f"Stream direct: {render_err}")

    col_dl, col_raw = st.columns([1, 1])
    with col_dl:
        export_json_button(plan, f"construction_planning_estimate_{PLATFORM_ID}.json")
    with col_raw:
        with st.expander("View Raw JSON Contract (Epic 4)", expanded=False):
            st.json(plan)


# =============================================================
# TAB 4: DAILY SITE ASSISTANT & WEATHER ADVISORY (EPIC 5)
# =============================================================
with tab_weather:
    st.subheader("Daily Site Assistant & Weather-Aware Safety Advisory")
    st.markdown(
        "Real-time dynamic engineering protocols responding to hazardous climatic shifts, "
        "paired with an interactive multi-turn construction engineering assistant."
    )

    st.markdown("### Weather Condition Selector & Dynamic Engineering Protocols")
    selected_weather = st.selectbox(
        "Current Site Meteorological Condition:",
        list(WEATHER_PROTOCOLS.keys()),
        index=0,
    )

    proto = WEATHER_PROTOCOLS[selected_weather]
    severity_pill = f"<span style='background-color: {proto['badge_color']}; color: white; padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 0.85rem;'>{proto['severity']}</span>"
    st.markdown(f"**Site Protocol Status:** {severity_pill}", unsafe_allow_html=True)

    # 4 Interactive Protocol Cards
    w1, w2 = st.columns(2)
    with w1:
        st.markdown(
            f"""
            <div class="audit-card">
                <h4>Tower Crane & Suspended Lifting Protocol</h4>
                <p>{proto['crane_status']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="audit-card">
                <h4>Temporary Electrical & Dewatering Safeguards</h4>
                <p>{proto['electrical_status']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with w2:
        st.markdown(
            f"""
            <div class="audit-card">
                <h4>Concrete Pouring & Curing Protocol (IS 456 / ACI 305R)</h4>
                <p>{proto['concrete_protocol']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="audit-card">
                <h4>Workforce Hydration & Shift Ergonomics</h4>
                <p>{proto['workforce_guidelines']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(f"**Daily Site Directive:** {proto['special_instructions']}")

    # -------------------------------------------------------------
    # MULTI-TURN CONSTRUCTION ENGINEERING ASSISTANT CHATBOT
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Interactive Construction Engineering Assistant")
    st.markdown(
        "Ask queries regarding IS 456 concrete curing, OSHA excavation benching, tower crane wind thresholds, "
        "formwork stripping periods, or rebar seismic detailing (Fe 500D vs Fe 500)."
    )

    # Initialize chat state
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "**Hello Site Engineer!** I am your Multimodal Construction Intelligence Assistant.\n\n"
                    "I can answer technical questions regarding IS 456:2000, OSHA 1926 regulations, concrete slump testing, "
                    "rebar grade specifications, crane safety limits, and crack remediation protocols. How can I assist today?"
                ),
            }
        ]

    # Quick Suggestion Chips
    st.markdown("**Suggested Engineering Queries:**")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    suggested_q = None
    if q_col1.button("IS 456 Curing Times", use_container_width=True):
        suggested_q = "What is the minimum concrete curing duration under IS 456 for OPC vs PPC?"
    if q_col2.button("Formwork Stripping Days", use_container_width=True):
        suggested_q = "What are the minimum formwork stripping times for slabs, beams, and columns under IS 456?"
    if q_col3.button("Tower Crane Wind Limit", use_container_width=True):
        suggested_q = "At what wind speed must tower crane operations be halted under OSHA and IS codes?"
    if q_col4.button("Fe 500 vs Fe 500D Rebar", use_container_width=True):
        suggested_q = "Why is Fe 500D mandated over Fe 500 for seismic ductile detailing in IS 13920?"

    # Display Chat History
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    user_prompt = st.chat_input("Ask a construction engineering question...")
    prompt_to_process = suggested_q or user_prompt

    if prompt_to_process:
        st.session_state["chat_messages"].append({"role": "user", "content": prompt_to_process})
        with st.chat_message("user"):
            st.markdown(prompt_to_process)

        with st.spinner("Formulating code-compliant engineering response..."):
            reply = query_engineering_assistant(
                question=prompt_to_process,
                chat_history=st.session_state["chat_messages"],
                api_key=api_key_input if provider_choice == GEMINI_MODE else None,
            )

        st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    if st.button("Clear Conversation"):
        st.session_state["chat_messages"] = []
        st.rerun()


# =============================================================
# TAB 5: ARCHITECTURE & SYSTEM BLUEPRINT (EPIC 1 & 6)
# =============================================================
with tab_architecture:
    st.subheader("Architecture, Epics Breakdown & Data Contracts")
    st.markdown(
        "Complete technical architectural blueprint, Kanban Epics mapping, "
        "and production verification checklist for the Multimodal Construction Intelligence Platform."
    )

    st.markdown("### System Architecture Flow")
    st.markdown(
        """
        ```mermaid
        graph TD
            A[Surveillance Site Photos / Defect Photos] --> B[Multimodal AI Engine]
            B --> C{Execution Mode}
            C -->|Google Gemini API| D[Gemini 2.5 Flash / 1.5 Flash Vision]
            C -->|Demonstration Mode| E[Forensic Expert Rule Engine & Pre-validated Contracts]
            D --> F[Strict JSON Data Contract Parser]
            E --> F
            F --> G[Tab 1: PPE Safety Audit & Hazard Matrix]
            F --> H[Tab 2: Concrete Crack Triage & Repair Blueprint]
            I[Interactive Project Inputs] --> J[Tab 3: CPWD Planning & INR Valuation Engine]
            J --> K[Pollinations AI Flux 3D Architectural Renderer]
            L[Weather Sensor / Manual Select] --> M[Tab 4: Dynamic Site Protocols & Chatbot]
            M --> N[Multi-turn Construction Engineering Assistant]
        ```
        """
    )

    st.markdown("### Epics Implementation Matrix")
    epics_table = [
        {"Epic": "Pre-requisites", "Scope": "Python 3.9+, Streamlit, FastAPI-ready modular structure", "Status": "Completed"},
        {"Epic": "Epic 1", "Scope": "Requirements & Env, Pytest unit tests, .env configuration", "Status": "Completed"},
        {"Epic": "Epic 2", "Scope": "PPE Safety Vision & Crack Diagnostics (OSHA 1926 & IS 456)", "Status": "Completed"},
        {"Epic": "Epic 3", "Scope": "Project Planning & Real Estate Valuation in INR (Lakhs & Crores)", "Status": "Completed"},
        {"Epic": "Epic 4", "Scope": "Multimodal AI & Strict JSON Contracts (Exportable & Validated)", "Status": "Completed"},
        {"Epic": "Epic 5", "Scope": "Site Chatbot & Weather Advisory Protocols (Wind, Rain, Heat)", "Status": "Completed"},
        {"Epic": "Epic 6", "Scope": "High-Tech CSS Theme, 1-Click Streamlit Cloud Deploy Readiness", "Status": "Completed"},
    ]
    st.dataframe(pd.DataFrame(epics_table), use_container_width=True, hide_index=True)

    st.markdown("### Platform Metadata")
    st.code(
        f"""Platform Title: Multimodal Construction Intelligence Platform
Capstone Project: Skill Wallet Project 1
Platform ID: {PLATFORM_ID}
Category: Generative AI | Real Estate Decision Support
Primary Framework: Streamlit 1.38+ / Python 3.9+
Multimodal Vision: Google Gemini (2.5-Flash / 1.5-Flash)
3D Rendering API: Pollinations AI (Flux Model)
Currency Formatting: Indian Rupee (INR - Lakhs & Crores)
Governing Codes: OSHA 1926, IS 456:2000, IS 2925, IS 3521, CPWD 2024
Testing Framework: Pytest 8.0+
Database: Zero external database dependencies (Session State + Exportable JSON)
Streamlit Cloud Deploy: 1-Click Ready (GitHub repository root / app.py)
""",
        language="yaml",
    )
