from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os

from memory import add_message, get_history
from detector import detect_scam
from agent import agent_reply
from extractor import extract_intelligence

API_KEY = "honeypot123"

app = FastAPI(title="Agentic Honey-Pot for Scam Detection")


# ===== Input schema from Mock Scammer API =====
class ScamEvent(BaseModel):
    conversation_id: str
    message: str


# ===== Main Honeypot Endpoint =====
@app.post("/honeypot")
def honeypot(
    event: ScamEvent,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 1️⃣ Store incoming message
    add_message(event.conversation_id, "scammer", event.message)
    history = get_history(event.conversation_id)

    # 2️⃣ Scam detection (AI)
    detection = detect_scam(event.message, history)

    agent_active = False
    reply = ""
    extracted = {
        "upi_ids": [],
        "bank_accounts": [],
        "phishing_urls": []
    }

    # 3️⃣ Agent handoff
    if detection["is_scam"]:
        agent_active = True
        reply = agent_reply(history)
        add_message(event.conversation_id, "agent", reply)
        extracted = extract_intelligence(reply)

    # 4️⃣ Structured response
    return {
        "scam_detected": detection["is_scam"],
        "confidence": detection["confidence"],
        "agent_active": agent_active,
        "agent_reply": reply,
        "conversation_turns": len(history),
        "extracted_intelligence": extracted
    }
