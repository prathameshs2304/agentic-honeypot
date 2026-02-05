from fastapi import FastAPI, Header, HTTPException, Body
import json
import os

from memory import add_message, get_history
from detector import detect_scam
from agent import agent_reply
from extractor import extract_intelligence

# =====================
# CONFIG
# =====================
API_KEY = os.getenv("API_KEY", "honeypot123")

app = FastAPI(title="Agentic Honey-Pot for Scam Detection")


# =====================
# MAIN ENDPOINT (422 SAFE)
# =====================
@app.post("/honeypot")
def honeypot(
    body: bytes = Body(default=b""),
    x_api_key: str = Header(None)
):
    # ---- Auth check ----
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # ---- GUVI / Tester payload handling ----
    # Accept empty, malformed, or alternate-key payloads without 422.
    event = {}
    if body:
        try:
            event = json.loads(body.decode("utf-8"))
        except Exception:
            event = {}

    conversation_id = (
        event.get("conversation_id")
        or event.get("conversationId")
        or event.get("conv_id")
        or "tester_conv"
    )
    message = (
        event.get("message")
        or event.get("msg")
        or event.get("text")
        or ""
    )

    if not message:
        return {
            "scam_detected": False,
            "confidence": 0.0,
            "agent_active": False,
            "agent_reply": None,
            "conversation_turns": 0,
            "extracted_intelligence": {
                "upi_ids": [],
                "bank_accounts": [],
                "phishing_urls": []
            }
        }

    # =====================
    # NORMAL FLOW
    # =====================

    # 1️⃣ Store incoming message
    add_message(conversation_id, "scammer", message)
    history = get_history(conversation_id)

    # 2️⃣ Detect scam
    detection = detect_scam(message, history)

    agent_active = False
    reply = None
    extracted = {
        "upi_ids": [],
        "bank_accounts": [],
        "phishing_urls": []
    }

    # 3️⃣ Agent takeover if scam
    if detection.get("is_scam"):
        agent_active = True
        reply = agent_reply(history)
        add_message(event.conversation_id, "agent", reply)
        extracted = extract_intelligence(reply)

    # 4️⃣ Structured response (judge-required)
    return {
        "scam_detected": detection.get("is_scam", False),
        "confidence": detection.get("confidence", 0.0),
        "agent_active": agent_active,
        "agent_reply": reply,
        "conversation_turns": len(history),
        "extracted_intelligence": extracted
    }
