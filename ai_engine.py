"""
AI Engine Module - Multimodal Construction Intelligence Platform
Unified Gemini Client supporting google-genai and google-generativeai with robust JSON mode,
multi-turn conversational assistant, and graceful demonstration fallback.
Platform ID: 6ac4c98d1dcde6d7857c1642
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image

# Mode identifiers
DEMO_MODE = "Demonstration Mode (Zero Key / Offline)"
GEMINI_MODE = "Google Gemini Multimodal AI"

SUPPORTED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]


def resolve_api_key(session_key: Optional[str] = None) -> str:
    """Retrieve Gemini API key from session state, parameter, or environment."""
    if session_key and session_key.strip():
        return session_key.strip()
    return os.getenv("GEMINI_API_KEY", "").strip()


def sanitize_json_response(raw_text: str) -> Dict[str, Any]:
    """
    Robust JSON parser that extracts valid JSON even if wrapped in markdown
    fences, prefixed with explanations, or trailing commentary.
    """
    text = (raw_text or "").strip()

    # 1. Clean markdown code fences
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # 2. Try direct json.loads
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
        if isinstance(parsed, list):
            return {"data": parsed}
    except Exception:
        pass

    # 3. Locate the outermost curly braces
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    if start_idx != -1 and end_idx > start_idx:
        candidate = text[start_idx : end_idx + 1]
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            # Try cleaning trailing commas
            candidate_cleaned = re.sub(r",\s*([\]}])", r"\1", candidate)
            try:
                parsed = json.loads(candidate_cleaned)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

    raise ValueError(f"Failed to parse model output into structured JSON. Raw snippet: {text[:200]}")


def call_gemini_multimodal(
    prompt: str,
    image: Optional[Image.Image] = None,
    system_instruction: str = "You are an expert construction safety and structural engineering decision support assistant.",
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    json_mode: bool = True,
) -> str:
    """
    Execute multimodal request against Gemini using modern google-genai SDK
    with automatic fallback to google-generativeai.
    """
    key = resolve_api_key(api_key)
    if not key:
        raise ValueError("No Gemini API key provided.")

    # Try modern google.genai first
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)
        contents = [prompt]
        if image is not None:
            contents.append(image)

        config_args = {
            "system_instruction": system_instruction,
            "temperature": 0.2,
        }
        if json_mode:
            config_args["response_mime_type"] = "application/json"

        config = types.GenerateContentConfig(**config_args)
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )
        return response.text or ""

    except ImportError:
        pass
    except Exception as exc:
        # If model name failed, try fallback to gemini-1.5-flash
        if "not found" in str(exc).lower() and model_name != "gemini-1.5-flash":
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=key)
                contents = [prompt]
                if image is not None:
                    contents.append(image)
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                    response_mime_type="application/json" if json_mode else None,
                )
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=contents,
                    config=config,
                )
                return response.text or ""
            except Exception:
                pass
        raise exc

    # Fallback to legacy google.generativeai if google.genai is absent
    try:
        import google.generativeai as legacy_genai

        legacy_genai.configure(api_key=key)
        generation_config = {"temperature": 0.2}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        # Model mapping for legacy SDK
        legacy_model_name = "gemini-1.5-flash"
        model = legacy_genai.GenerativeModel(
            model_name=legacy_model_name,
            system_instruction=system_instruction,
            generation_config=generation_config,
        )

        content_list = [prompt]
        if image is not None:
            content_list.append(image)

        response = model.generate_content(content_list)
        return response.text or ""
    except Exception as exc:
        raise RuntimeError(f"Gemini API invocation error: {exc}")


def call_gemini_chat(
    chat_history: List[Dict[str, str]],
    system_instruction: str = "You are a seasoned construction project manager and structural engineer. Provide concise, code-compliant answers citing OSHA and IS standards.",
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
) -> str:
    """Multi-turn chat invocation."""
    key = resolve_api_key(api_key)
    if not key:
        raise ValueError("No Gemini API key provided.")

    history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in chat_history[-10:]])
    prompt = f"Previous conversation:\n{history_text}\n\nRespond to the last USER message directly, clearly, and constructively."

    return call_gemini_multimodal(
        prompt=prompt,
        image=None,
        system_instruction=system_instruction,
        api_key=key,
        model_name=model_name,
        json_mode=False,
    )
