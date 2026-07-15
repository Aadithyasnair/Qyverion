from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.log_entry import LogEntry
from app.models.alert import Alert
from app.models.threat_indicator import ThreatIndicator


def test_health_check(client: TestClient) -> None:
    """
    Test the system health check endpoint.
    It returns 200/500 depending on DB availability, but check structure.
    """
    response = client.get("/api/v1/health")
    assert response.status_code in [200, 500]
    data = response.json()
    assert "status" in data
    assert data["project"] == "Qyverion"


def test_logs_endpoints(db: Session, client: TestClient) -> None:
    """
    Tests logs retrieval and ingest validation.
    """
    # Seed baseline logs in test database session
    db.add(LogEntry(raw_data="log1", log_source="firewall", severity="INFO", event_timestamp=datetime.now(timezone.utc)))
    db.add(LogEntry(raw_data="log2", log_source="firewall", severity="INFO", event_timestamp=datetime.now(timezone.utc)))
    db.commit()

    # 1. Read existing logs
    response = client.get("/api/v1/logs/")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)
    assert len(logs) >= 2
    assert "raw_data" in logs[0]
    assert "log_source" in logs[0]

    # 2. Ingest a new valid log
    payload = {
        "raw_data": "Dec 10 09:12:01 server cron[1234]: (root) CMD (sys-backup)",
        "log_source": "syslog_cron",
        "severity": "INFO",
        "source_ip": None,
        "destination_ip": None,
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post("/api/v1/logs/ingest", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["log_source"] == "syslog_cron"
    assert "id" in data
    assert "ingested_at" in data

    # 3. Read again to confirm addition
    response = client.get("/api/v1/logs/")
    assert len(response.json()) == len(logs) + 1


def test_logs_ingest_validation(client: TestClient) -> None:
    """
    Tests that logs ingest endpoint returns validation errors for bad payloads.
    """
    # Missing required field 'raw_data'
    payload = {
        "log_source": "firewall",
        "severity": "INFO",
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post("/api/v1/logs/ingest", json=payload)
    assert response.status_code == 422


def test_alerts_endpoints(db: Session, client: TestClient) -> None:
    """
    Tests alert retrieval, creation, and status patch transitions.
    """
    # Seed baseline alerts in test database session
    db.add(Alert(title="alert1", description="desc1", severity="HIGH", status="NEW"))
    db.add(Alert(title="alert2", description="desc2", severity="HIGH", status="NEW"))
    db.commit()

    # 1. Read alerts
    response = client.get("/api/v1/alerts/")
    assert response.status_code == 200
    alerts = response.json()
    assert len(alerts) >= 2

    # 2. Create mock alert
    payload = {
        "title": "SQL Injection Suspected",
        "description": "Detection pattern matches SQL keywords in query params",
        "severity": "HIGH",
        "status": "NEW",
        "assigned_to_id": None,
    }
    response = client.post("/api/v1/alerts/", json=payload)
    assert response.status_code == 201
    alert_id = response.json()["id"]

    # 3. Transition status to RESOLVED
    response = client.patch(
        f"/api/v1/alerts/{alert_id}/status", json={"status": "RESOLVED"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "RESOLVED"
    assert data["closed_at"] is not None


def test_indicators_endpoints(db: Session, client: TestClient) -> None:
    """
    Tests threat intelligence IoC retrieval and posting.
    """
    # Seed baseline indicators in test database session
    db.add(ThreatIndicator(indicator_value="198.51.100.1", indicator_type="ip", threat_actor="Actor1", risk_score=80))
    db.add(ThreatIndicator(indicator_value="198.51.100.2", indicator_type="ip", threat_actor="Actor2", risk_score=80))
    db.commit()

    # 1. Read threat indicators
    response = client.get("/api/v1/indicators/")
    assert response.status_code == 200
    indicators = response.json()
    assert len(indicators) >= 2

    # 2. Create new indicator
    payload = {
        "indicator_value": "198.51.100.42",
        "indicator_type": "ip",
        "description": "Known phishing campaigns traffic server host",
        "threat_actor": "PawnStorm (APT28)",
        "risk_score": 90,
    }
    response = client.post("/api/v1/indicators/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["indicator_value"] == "198.51.100.42"

    # 3. Test duplicate insertion failure
    response = client.post("/api/v1/indicators/", json=payload)
    assert response.status_code == 400
