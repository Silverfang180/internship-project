import os
import json
import re
from google import genai
from google.genai import types

def generate_insight(metrics_dict, api_key=None, retries=1):
    """
    Generate an AI insight based on aggregate SLA metrics.
    Returns a dict with structured keys, or None if the API key is missing or an error occurs.
    """
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        client = genai.Client(api_key=api_key)
        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

        system_instruction = (
            "You are an operations intelligence assistant analyzing support SLA metrics. "
            "Use only the supplied aggregate metrics. Do not invent or calculate numbers. "
            "Do not provide numerical evidence. Numerical evidence is handled by Python. "
            "Do NOT use any digits in your response. Spell out small numbers in words if strictly needed. "
            "Do not claim causation when data only establishes association. "
            "NEVER recommend hiring, increasing total headcount, or adding agents. "
            "ONLY recommend testing/reallocating existing headcount where appropriate (e.g., "
            "'Pilot reallocating one existing Chat/Email coverage shift to Night and monitor Night breach rate and Morning/Day impact for four weeks.'). "
            "Do not rank or blame individual agents. "
            "Do NOT include the numerical caveats in your response. The application will render them automatically. "
            "Respond strictly in JSON with this exact schema:\n"
            "{\n"
            '  "what_happened": "High-level summary of the breach rate and key signal (qualitative only, no digits)",\n'
            '  "interpretation": "What this means for the operation (qualitative only, no digits)",\n'
            '  "recommended_test": "A suggested operational change or test to address the issue (must use existing headcount, no digits)",\n'
            '  "caveat": "Material limitations of this analysis (qualitative only, no digits. Do not restate volume or roster caveats.)"\n'
            "}"
        )

        prompt = f"Analyze these aggregate SLA metrics for a support team:\n{json.dumps(metrics_dict, indent=2)}"

        for attempt in range(retries + 1):
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True, maximum_remote_calls=None)
                )
            )
            try:
                data = json.loads(response.text)
            except json.JSONDecodeError:
                if attempt < retries:
                    continue
                return None

            required_keys = {"what_happened", "interpretation", "recommended_test", "caveat"}
            if not isinstance(data, dict) or not required_keys.issubset(data.keys()):
                if attempt < retries:
                    continue
                return None

            banned_phrases = [
                "hire", "hiring", "recruit", "additional agents", "extra agents", "more agents",
                "additional staff", "extra staff", "more staff", "add headcount", "increase headcount",
                "expand the team", "due to", "because of", "led to", "driven by", "caused by"
            ]

            has_error = False
            for k, v in data.items():
                if isinstance(v, str):
                    # 1. No digits
                    if re.search(r'\d', v):
                        has_error = True
                        break

                    # 2. No banned phrases (whole word)
                    v_lower = v.lower()
                    if any(re.search(r'\b' + re.escape(phrase) + r'\b', v_lower) for phrase in banned_phrases):
                        has_error = True
                        break

            if has_error:
                if attempt < retries:
                    prompt += "\n\nCRITICAL WARNING: Your previous response was rejected because it contained digits or banned causal phrases. You MUST rewrite your response to be strictly qualitative. Do NOT use any digits. Do NOT use causal phrases (like 'driven by', 'caused by', 'due to'); use associative phrases instead."
                    continue
                return "WITHHELD"

            return data

    except Exception:
        pass

    return None
