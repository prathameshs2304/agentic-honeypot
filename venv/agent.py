from google import genai
import os

# ✅ FORCE v1 API
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
    http_options={"api_version": "v1"}
)

def agent_reply(history):
    prompt = f"""
You are pretending to be a real bank customer.

Conversation so far:
{history}

Reply naturally and continue the conversation.
Try to extract UPI ID, bank name, or links.
Do NOT reveal scam detection.
"""

    response = client.models.generate_content(
        model="models/gemini-1.5-flash",
        contents=prompt
    )

    return response.text.strip() if response.text else ""
