from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.alert import Alert
from app.models.log_entry import LogEntry
from app.services.ai_service import AIService
import re
import json

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


@router.post("/playbook/{alert_id}/stream", summary="Stream playbook generation for alert (SSE)")
def stream_alert_playbook(alert_id: int, db: Session = Depends(get_db)) -> StreamingResponse:
    """
    Streams the playbook response as Server-Sent Events (SSE).
    The frontend reads chunks token-by-token and renders them progressively,
    eliminating the perceived cutoff from token budget limits.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found."
        )

    ip_matches = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", alert.description)
    if ip_matches:
        ip = ip_matches[0]
        logs = (
            db.query(LogEntry)
            .filter((LogEntry.source_ip == ip) | (LogEntry.destination_ip == ip))
            .limit(5)
            .all()
        )
    else:
        logs = db.query(LogEntry).order_by(LogEntry.ingested_at.desc()).limit(5).all()

    ai_service = AIService()

    def event_generator():
        try:
            for chunk in ai_service.generate_playbook_stream(alert, logs):
                # Encode chunk as SSE data frame
                payload = json.dumps({"chunk": chunk})
                yield f"data: {payload}\n\n"
        except Exception as err:
            error_payload = json.dumps({"error": str(err)})
            yield f"data: {error_payload}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


class RemediateResponse(BaseModel):
    success: bool
    message: str
    blocked_ips: list[str]
    execution_log: list[str]


@router.post("/playbook/{alert_id}/remediate", response_model=RemediateResponse, summary="Execute active playbook remediation")
def execute_remediation(alert_id: int, db: Session = Depends(get_db)) -> RemediateResponse:
    """
    Parses IPs from the alert description, logs blocked rules in the firewall BlockedIP table,
    and returns a simulated active execution log.
    """
    from app.models.blocked_ip import BlockedIP
    import re
    
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found."
        )

    # Extract IP indicators
    ip_matches = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", alert.description)
    if not ip_matches:
        ip_matches = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", alert.title)

    blocked_list = []
    logs = [
        "Initializing active playbook containment executor...",
        "Querying threat details...",
        f"Alert: {alert.title} (Severity: {alert.severity})",
    ]

    for ip in ip_matches:
        # Check if already active
        existing = db.query(BlockedIP).filter(BlockedIP.ip_address == ip).first()
        if existing:
            logs.append(f"Attacker IP {ip} is already blocked in active database.")
            blocked_list.append(ip)
        else:
            blocked_ip = BlockedIP(
                ip_address=ip,
                alert_id=alert.id,
                rule_name=alert.title,
                status="ACTIVE"
            )
            db.add(blocked_ip)
            logs.append(f"Found attacker IP: {ip}")
            logs.append(f"Simulating network rule: sudo iptables -A INPUT -s {ip} -j DROP")
            logs.append(f"Successfully added block entry for {ip} to active firewall database.")
            blocked_list.append(ip)

    if blocked_list:
        db.commit()
        logs.append("Containment transaction committed. Network block policy synchronized.")
        return RemediateResponse(
            success=True,
            message="Containment active block rules executed successfully.",
            blocked_ips=blocked_list,
            execution_log=logs
        )
    else:
        logs.append("No public attacker IP indicators found in the alert details.")
        return RemediateResponse(
            success=False,
            message="No containment actions executed: No attacker IP indicators identified.",
            blocked_ips=[],
            execution_log=logs
        )
