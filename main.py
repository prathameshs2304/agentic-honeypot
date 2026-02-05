from fastapi import FastAPI, Header, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
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
# INPUT SCHEMA (FIXED)
# =====================
class ScamEvent(BaseModel):
    conversation_id: Optional[str] = "tester_conv"
    message: Optional[str] = ""


# =====================
# MAIN ENDPOINT (422 SAFE)
# =====================
@app.post("/honeypot")
def honeypot(
    event: ScamEvent = Body(default=ScamEvent()),
    x_api_key: str = Header(None)
):
    # ---- Auth check ----
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # ---- GUVI / Tester empty-payload handling ----
    if not event.message:
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
    add_message(event.conversation_id, "scammer", event.message)
    history = get_history(event.conversation_id)

    # 2️⃣ Detect scam
    detection = detect_scam(event.message, history)

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
