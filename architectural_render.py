"""
Architectural 3D Render Generator Module (Epic 3 & Pollinations AI Integration)
Generates high-fidelity architectural visualization prompts and directly fetches
conceptual 3D photorealistic renderings using the Pollinations AI / Flux engine.
Platform ID: 6ac4c98d1dcde6d7857c1642
"""

import io
import urllib.parse
from typing import Optional, Tuple
from PIL import Image
import requests

PLATFORM_ID = "6ac4c98d1dcde6d7857c1642"

STYLE_PRESETS = {
    "Contemporary Indian Urbanism": "contemporary Indian architecture, sleek glass curtain walls, ventilated terracotta louvers, lush hanging garden balconies, natural limestone cladding",
    "Biophilic & Sustainable (LEED Platinum)": "biophilic architectural design, vertical green walls, solar canopy pergolas, rainwater collection swales, cross-laminated timber accents, ambient daylight",
    "Modern Minimalist & Brutalist Concrete": "board-marked fair-faced concrete, cantilevered architectural volumes, dramatic geometric light wells, recessed shadow lines, slate pavers",
    "Luxury High-End Hospitality & Villa": "double-height glazing, infinity water reflection pool, Italian travertine marble facade, bronze metallic mullions, warm perimeter cove lighting",
    "Industrial PEB Logistics Hub": "clean architectural pre-engineered steel structure, metallic insulated sandwich panels, clearspan high-bay roof monitors, polished industrial concrete apron, docking bays",
}

LIGHTING_PRESETS = {
    "Golden Hour Sunset": "warm golden hour natural sunlight, long dramatic architectural shadows, dusk sky gradient, illuminated warm interior glow",
    "Crisp Architectural Midday": "bright crystal-clear daylight, pristine blue sky, sharp shadows, true-to-life material textures, neutral 5500K color temperature",
    "Dramatic Twilight / Blue Hour": "dramatic twilight blue hour, warm architectural spot illumination, glowing perimeter LEDs, deep navy sky",
}


def build_architectural_prompt(
    structure_type: str,
    built_up_sqft: float,
    location_tier: str,
    finish_level: str = "Standard",
    style_preset: str = "Contemporary Indian Urbanism",
    lighting: str = "Golden Hour Sunset",
) -> str:
    """Builds a rich, production-grade architectural prompt for Flux/Pollinations."""
    style_desc = STYLE_PRESETS.get(style_preset, STYLE_PRESETS["Contemporary Indian Urbanism"])
    light_desc = LIGHTING_PRESETS.get(lighting, LIGHTING_PRESETS["Golden Hour Sunset"])

    # Extract clean city context
    city_context = "modern Indian metropolitan skyline"
    if "Tier 1" in location_tier:
        city_context = "contemporary Mumbai / Bengaluru skyline with lush tropical landscaping and asphalt boulevard"
    elif "Tier 2" in location_tier:
        city_context = "progressive Indian smart city with landscaped road frontage and native neem/gulmohar trees"
    else:
        city_context = "suburban Indian commercial zone with ample green setback and perimeter paved driveways"

    prompt = (
        f"Masterpiece 3D architectural exterior visualization rendering of a newly constructed {structure_type}, "
        f"spanning {built_up_sqft:,.0f} square feet built-up footprint, {finish_level.lower()} grade finishes. "
        f"{style_desc}. Set in {city_context}. "
        f"{light_desc}. "
        f"Shot on Hasselblad H6D-100c, 24mm tilt-shift architectural lens, razor-sharp textures, photorealistic materials, "
        f"unreal engine 5 architectural render, 8k resolution, octane render quality, no watermarks, no distorted geometry, no text."
    )
    return prompt


def generate_pollinations_url(
    prompt: str,
    seed: int = 42,
    width: int = 1024,
    height: int = 768,
    model: str = "flux",
) -> str:
    """Constructs the encoded Pollinations AI / Flux generation endpoint."""
    encoded_prompt = urllib.parse.quote(prompt.strip())
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true&model={model}"
    return url


def fetch_rendered_image(
    prompt: str,
    seed: int = 42,
    timeout_seconds: int = 20,
) -> Tuple[Optional[Image.Image], str, Optional[str]]:
    """
    Calls the Pollinations AI endpoint and returns (PIL_Image, url, error_message).
    If network is unavailable or times out, gracefully returns None with error message.
    """
    url = generate_pollinations_url(prompt, seed=seed)
    try:
        response = requests.get(url, timeout=timeout_seconds)
        if response.status_code == 200:
            image_data = io.BytesIO(response.content)
            pil_image = Image.open(image_data).convert("RGB")
            return pil_image, url, None
        else:
            return None, url, f"Pollinations API returned status code {response.status_code}"
    except Exception as exc:
        return None, url, f"Could not retrieve image from Pollinations API: {exc}"
