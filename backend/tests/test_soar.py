import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.log_entry import LogEntry
from app.models.blocked_ip import BlockedIP
from app.models.threat_indicator import ThreatIndicator


def test_investigate_endpoint(client: TestClient, db: Session):
    # Ingest a sample log
    from datetime import datetime, timezone
    log = LogEntry(
        raw_data="Failed login from 198.51.100.100",
        log_source="sshd",
        severity="HIGH",
        source_ip="198.51.100.100",
        destination_ip="10.0.0.1",
        event_timestamp=datetime.now(timezone.utc)
    )
    db.add(log)
    db.commit()

    response = client.get("/api/v1/investigate/198.51.100.100")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data

    # Verify primary attacker node exists
    nodes = data["nodes"]
    attacker_node = next((n for n in nodes if n["id"] == "198.51.100.100"), None)
    assert attacker_node is not None
    assert attacker_node["type"] == "attacker"


def test_soar_playbook_remediation(client: TestClient, db: Session):
    # Create target alert containing a malicious IP in description
    alert = Alert(
        title="Brute Force Alert",
        description="Multiple failed SSH login attempts detected from origin IP 198.51.100.222",
        severity="HIGH",
        status="NEW"
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # Trigger active response endpoint
    response = client.post(f"/api/v1/ai/playbook/{alert.id}/remediate")
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "198.51.100.222" in data["blocked_ips"]
    assert len(data["execution_log"]) > 0

    # Verify BlockedIP entry exists in the DB
    blocked_entry = db.query(BlockedIP).filter(BlockedIP.ip_address == "198.51.100.222").first()
    assert blocked_entry is not None
    assert blocked_entry.alert_id == alert.id
    assert blocked_entry.status == "ACTIVE"


def test_threat_feeds_sync_endpoint(client: TestClient, db: Session):
    # Perform feed sync
    response = client.post("/api/v1/indicators/sync")
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["added_count"] > 0

    # Verify items are added to threat intelligence catalog
    indicators = db.query(ThreatIndicator).all()
    assert len(indicators) > 0


def test_get_blocked_ips_registry(client: TestClient, db: Session):
    # Create a mock blocked IP
    blocked = BlockedIP(
        ip_address="198.51.100.111",
        rule_name="Manual block",
        status="ACTIVE"
    )
    db.add(blocked)
    db.commit()

    response = client.get("/api/v1/indicators/blocked")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["ip_address"] == "198.51.100.111"
