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
    assert "remediation" in data["reply"].lower() or "playbook" in data["reply"].lower()
    assert "192.168.1.50" in data["reply"]
