from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.alert import Alert
from app.models.log_entry import LogEntry
from app.services.ai_service import AIService

router = APIRouter()


class AIChatRequest(BaseModel):
    message: str
    raw_log: Optional[str] = None


class AIChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=AIChatResponse, summary="Send message to AI Copilot")
def chat_copilot(payload: AIChatRequest) -> AIChatResponse:
    """
    Accepts user prompt and optional raw log to explain.
    Returns response generated from local Ollama or fallback experts.
    """
    ai_service = AIService()
    
    if payload.raw_log:
        reply = ai_service.analyze_log(payload.raw_log)
    else:
        messages = [
            {"role": "system", "content": ai_service.system_prompt},
            {"role": "user", "content": payload.message}
        ]
        reply = ai_service._call_ollama(messages)
        if not reply:
            reply = (
                f"### 🤖 Local Copilot Fallback Response\n\n"
                f"I received your question: \"{payload.message}\"\n\n"
                f"**General Security Guidance:**\n"
                f"- Ensure security rules are evaluated recursively across directories.\n"
                f"- For brute-force incidents, isolate the endpoint immediately.\n"
                f"- Enable detailed file auditing for access logs.\n\n"
                f"*(Note: Local Ollama server at http://localhost:11434 was unreachable, showing fallback expert rule answer)*"
            )
            
    return AIChatResponse(reply=reply)


@router.post("/playbook/{alert_id}", response_model=AIChatResponse, summary="Generate response playbook for alert")
def generate_alert_playbook(alert_id: int, db: Session = Depends(get_db)) -> AIChatResponse:
    """
    Queries alert and matching logs from the database,
    and returns a step-by-step markdown containment playbook.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found."
        )
        
    # Find logs associated with this alert by matching IP addresses
    logs = []
    # Check if description contains an IP address
    import re
    ip_matches = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", alert.description)
    if ip_matches:
        ip = ip_matches[0]
        logs = (
            db.query(LogEntry)
            .filter((LogEntry.source_ip == ip) | (LogEntry.destination_ip == ip))
            .limit(10)
            .all()
        )
    else:
        # Fallback to last 10 logs
        logs = db.query(LogEntry).order_by(LogEntry.ingested_at.desc()).limit(10).all()

    ai_service = AIService()
    playbook_reply = ai_service.generate_playbook(alert, logs)
    return AIChatResponse(reply=playbook_reply)
