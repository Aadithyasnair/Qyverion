import json
from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.log_entry import LogEntry
from app.models.alert import Alert
from app.models.threat_indicator import ThreatIndicator
from app.services.parsers import SyslogParser, JSONParser, WindowsEventParser, ParserError
from app.services.log_ingestion import LogIngestionService


# 1. Unit Tests for Parsers
def test_syslog_parser_rfc5424() -> None:
    parser = SyslogParser()
    raw = '<34>1 2026-07-15T21:30:00.003Z myhost firewall - ID47 - Inbound connection from 192.168.1.105 blocked'
    parsed = parser.parse(raw)
    
    assert parsed.log_source == "firewall"
    assert parsed.severity == "CRITICAL"  # priority 34 -> severity 2 -> CRITICAL
    assert parsed.source_ip == "192.168.1.105"
    assert parsed.event_timestamp == datetime.fromisoformat("2026-07-15T21:30:00.003+00:00")


def test_syslog_parser_rfc3164() -> None:
    parser = SyslogParser()
    raw = '<36>Oct 11 22:14:15 host sshd[1234]: Failed password for invalid user admin from 203.0.113.5'
    parsed = parser.parse(raw)
    assert parsed.log_source == "sshd"
    assert parsed.severity == "WARNING"  # priority 36 -> severity 4 -> WARNING

    assert parsed.source_ip == "203.0.113.5"
    assert parsed.event_timestamp.month == 10
    assert parsed.event_timestamp.day == 11


def test_json_parser_flat_and_nested() -> None:
    parser = JSONParser()
    
    # Nested ECS-style JSON log
    raw = json.dumps({
        "source": {"ip": "10.0.0.1"},
        "destination": {"ip": "10.0.0.2"},
        "service": {"name": "web_server"},
        "log": {"level": "error"},
        "event": {"timestamp": "2026-07-15T21:30:00Z"}
    })
    
    parsed = parser.parse(raw)
    assert parsed.log_source == "web_server"
    assert parsed.severity == "CRITICAL"
    assert parsed.source_ip == "10.0.0.1"
    assert parsed.destination_ip == "10.0.0.2"
    assert parsed.event_timestamp == datetime.fromisoformat("2026-07-15T21:30:00+00:00")


def test_json_parser_invalid() -> None:
    parser = JSONParser()
    with pytest.raises(ParserError):
        parser.parse("{bad json")


def test_windows_parser_security_failure() -> None:
    parser = WindowsEventParser()
    
    raw = json.dumps({
        "EventID": 4625,
        "Channel": "Security",
        "Keywords": "Audit Failure",
        "TimeCreated": {"SystemTime": "2026-07-15T21:30:00.123456Z"},
        "EventData": {
            "IpAddress": "192.168.1.100",
            "TargetUserName": "Administrator"
        }
    })
    
    parsed = parser.parse(raw)
    assert parsed.log_source == "winlog_security_4625"
    assert parsed.severity == "CRITICAL"
    assert parsed.source_ip == "192.168.1.100"


# 2. Integration / End-to-End Ingestion & Threat Intel Matching Tests
def test_ingest_pipeline_with_threat_intel_trigger(db: Session, client: TestClient) -> None:
    # 1. Create a known threat indicator in the database
    ioc = ThreatIndicator(
        indicator_value="198.51.100.99",
        indicator_type="ip",
        description="Active Command and Control Beaconing Server",
        threat_actor="APT28 (Fancy Bear)",
        risk_score=95,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(ioc)
    db.commit()

    # Verify threat indicator exists
    db_ioc = db.query(ThreatIndicator).filter(ThreatIndicator.indicator_value == "198.51.100.99").first()
    assert db_ioc is not None

    # 2. Ingest a log showing traffic from this IP address
    payload = {
        "raw_data": json.dumps({
            "source": {"ip": "198.51.100.99"},
            "service": "firewall_cisco",
            "level": "warning",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }),
        "log_source": "json",
        "severity": "WARNING",
        "event_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/logs/ingest", json=payload)
    assert response.status_code == 201
    
    # 3. Verify the log is successfully saved to the database
    db_log = db.query(LogEntry).filter(LogEntry.source_ip == "198.51.100.99").first()
    assert db_log is not None
    assert db_log.log_source == "firewall_cisco"

    # 4. Verify an alert was automatically triggered by the threat match
    db_alert = db.query(Alert).filter(Alert.title.contains("198.51.100.99")).first()
    assert db_alert is not None
    assert "APT28 (Fancy Bear)" in db_alert.description
    assert db_alert.severity == "CRITICAL"
    assert db_alert.status == "NEW"
