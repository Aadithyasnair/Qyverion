import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.log_entry import LogEntry
from app.models.alert import Alert


def test_brute_force_correlation_alert(db: Session, client: TestClient) -> None:
    """
    Tests that 5 failed logon attempts within 60s triggers a Brute Force Alert.
    """
    test_ip = "198.51.100.200"

    # 1. Ingest 4 failed logon events
    for i in range(4):
        payload = {
            "raw_data": f"Failed password for user admin{i} from {test_ip} port 22 sshd",
            "log_source": "sshd",
            "severity": "WARNING",
            "event_timestamp": datetime.now(timezone.utc).isoformat()
        }
        response = client.post("/api/v1/logs/ingest", json=payload)
        assert response.status_code == 201

    # Verify no Brute Force alerts generated yet
    brute_alerts = (
        db.query(Alert)
        .filter(Alert.title.contains("Brute Force"))
        .filter(Alert.title.contains(test_ip))
        .all()
    )
    assert len(brute_alerts) == 0

    # 2. Ingest the 5th failed logon event
    payload = {
        "raw_data": f"Failed password for user admin_final from {test_ip} port 22 sshd",
        "log_source": "sshd",
        "severity": "WARNING",
        "event_timestamp": datetime.now(timezone.utc).isoformat()
    }
    response = client.post("/api/v1/logs/ingest", json=payload)
    assert response.status_code == 201

    # Verify a Brute Force alert HAS been created
    triggered_alerts = (
        db.query(Alert)
        .filter(Alert.title.contains("Brute Force"))
        .filter(Alert.title.contains(test_ip))
        .all()
    )
    assert len(triggered_alerts) == 1
    assert triggered_alerts[0].severity == "HIGH"
    assert "Multiple failed logon attempts" in triggered_alerts[0].description


def test_service_probing_correlation_alert(db: Session, client: TestClient) -> None:
    """
    Tests that accessing 3 distinct services from the same IP triggers a Probe Alert.
    """
    test_ip = "198.51.100.220"

    # Ingest logs targeting 3 distinct services (sshd, apache, firewall)
    services = ["sshd", "apache", "firewall"]
    for service in services:
        payload = {
            "raw_data": f"Access initiated from {test_ip} to service {service}",
            "log_source": service,
            "severity": "INFO",
            "event_timestamp": datetime.now(timezone.utc).isoformat()
        }
        response = client.post("/api/v1/logs/ingest", json=payload)
        assert response.status_code == 201

    # Verify an Anomalous Service Probe alert was created
    probe_alerts = (
        db.query(Alert)
        .filter(Alert.title.contains("Anomalous Service Probe"))
        .filter(Alert.title.contains(test_ip))
        .all()
    )
    assert len(probe_alerts) == 1
    assert probe_alerts[0].severity == "MEDIUM"
    assert "distinct services" in probe_alerts[0].description
