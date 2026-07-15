from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.alert import Alert


def test_chat_copilot_general_response(client: TestClient) -> None:
    """
    Tests that a general chat message receives a 200 reply response.
    """
    payload = {
        "message": "Explain how port scanning works"
    }
    response = client.post("/api/v1/ai/chat", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 0


def test_playbook_generation_remediation(db: Session, client: TestClient) -> None:
    """
    Tests playbook endpoint fetches alert, logs and constructs markdown text.
    """
    # Seed an alert
    alert = Alert(
        title="Brute Force detected from 192.168.1.50",
        description="Multiple failed logon attempts from 192.168.1.50 within a 60-second window.",
        severity="HIGH",
        status="NEW",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    response = client.post(f"/api/v1/ai/playbook/{alert.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "reply" in data
    reply_lower = data["reply"].lower()
    # The structured prompt produces 4 labelled sections; accept any of these markers
    # (Ollama may or may not include the word "playbook" / "remediation" depending on context)
    security_keywords = [
        "remediation", "playbook", "executive summary", "containment",
        "investigation", "hardening", "block", "iptables", "fail2ban"
    ]
    assert any(kw in reply_lower for kw in security_keywords), (
        f"Expected at least one security keyword in reply. Got: {data['reply'][:300]}"
    )
    assert "192.168.1.50" in data["reply"]

