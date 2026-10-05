import os
import json
from google import genai
from google.genai import types

def generate_insight(metrics_dict, api_key=None):
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
            "Do not claim causation when data only establishes association. "
            "Do not use words like 'guaranteed', 'caused', 'main driver', or 'primarily driven by'. "
            "Instead of 'primarily driven by', use evidence-safe wording like 'The largest concentration of breaches is in Night-created tickets, especially Chat and Email.' "
            "NEVER recommend hiring, increasing total headcount, or adding agents. "
            "ONLY recommend testing/reallocating existing headcount where appropriate (e.g., "
            "'Pilot reallocating one existing Chat/Email coverage shift to Night and monitor Night breach rate and Morning/Day impact for four weeks.'). "
            "Do not rank or blame individual agents. "
            "In the caveat, follow these rules about volume: "
            "1. Never say the current period tickets are below the export average if they are equal or above. "
            "2. If current period tickets are around the export average, say it is broadly consistent with the export average. "
            "3. Explicitly state the export's observed weekly volume is substantially below the ~650/week figure quoted in the brief. "
            "4. Never compare a single period's ticket count directly to the ~650 brief figure without explaining that ~650 is a quoted weekly volume. "
            "5. Explicitly mention uncertainty around 3 agents missing from later roster data, and no queue/utilization data to prove causation. "
            "Do NOT output numerical evidence. Numerical evidence is handled by Python. "
            "Respond strictly in JSON with this exact schema:\n"
            "{\n"
            '  "what_happened": "High-level summary of the breach rate and key signal (qualitative only)",\n'
            '  "interpretation": "What this means for the operation",\n'
            '  "recommended_test": "A suggested operational change or test to address the issue (must use existing headcount)",\n'
            '  "caveat": "Material limitations of this analysis (must include volume, roster, and queue data limits as instructed)"\n'
            "}"
        )

        prompt = f"Analyze these aggregate SLA metrics for a support team:\n{json.dumps(metrics_dict, indent=2)}"

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True, maximum_remote_calls=None)
            )
        )
        data = json.loads(response.text)

        # Lightweight validation layer
        required_keys = {"what_happened", "interpretation", "recommended_test", "caveat"}
        if not required_keys.issubset(data.keys()):
            return None

        banned_words = ["guaranteed", "caused", "main driver", "primarily driven by", "hire", "adding agents", "increasing headcount", "increase headcount", "new headcount"]
        for k, v in data.items():
            if isinstance(v, str):
                v_lower = v.lower()
                if any(w in v_lower for w in banned_words):
                    return None

        return data
    except Exception:
        # Silently fail and fallback to deterministic report
        return None
