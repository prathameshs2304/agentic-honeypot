from google import genai
import json
import re
import os

# Allow overriding API version/model without code changes.
API_VERSION = os.getenv("GOOGLE_API_VERSION", "v1beta")
MODEL_NAME = os.getenv("GOOGLE_MODEL_NAME", "gemini-1.5-flash")

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
    http_options={"api_version": API_VERSION}
)

def detect_scam(message, history):
    prompt = f"""
You are a scam detection AI.

Conversation history:
{history}

Latest message:
"{message}"

Return ONLY valid JSON.
No markdown. No explanation.

Format:
{{
  "is_scam": true,
  "confidence": 0.0
}}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
    except Exception:
        # Fail closed: if the model call fails, treat as not-a-scam with low confidence.
        return {"is_scam": False, "confidence": 0.0}

    text = response.text.strip()

    # 🛡️ Safe JSON extraction
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"is_scam": False, "confidence": 0.0}

    return json.loads(match.group())
