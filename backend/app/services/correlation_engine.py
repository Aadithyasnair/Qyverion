import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.log_entry import LogEntry
from app.models.alert import Alert

logger = logging.getLogger("app.services.correlation_engine")


class CorrelationEngine:
    """
    Security Correlation Rules Engine.
    Analyzes ingested log entries against historical windows in the database
    to detect complex multi-event attack patterns.
    """

    def __init__(self, db: Session):
        self.db = db

    def evaluate(self, log_entry: LogEntry) -> list[Alert]:
        """
        Runs all active correlation rules against the newly ingested log entry.
        Returns a list of triggered Alert instances.
        """
        alerts_triggered = []

        # Rule 1: Multi-Failure logon Brute Force Detection
        raw_lower = log_entry.raw_data.lower()
        is_login_failure = (
            "4625" in raw_lower
            or "failed password" in raw_lower
            or "failed logon" in raw_lower
            or (log_entry.log_source == "sshd" and "failed" in raw_lower)
        )

        if is_login_failure and log_entry.source_ip:
            # Strip timezone to match SQLite timezone-naive timestamp string formats safely
            time_threshold = (datetime.now(timezone.utc) - timedelta(seconds=60)).replace(tzinfo=None)
            
            # Count logon failures from this source IP in the last 60 seconds
            failed_count = (
                self.db.query(LogEntry)
                .filter(LogEntry.source_ip == log_entry.source_ip)
                .filter(LogEntry.ingested_at >= time_threshold)
                .filter(
                    (LogEntry.raw_data.ilike("%4625%")) |
                    (LogEntry.raw_data.ilike("%failed password%")) |
                    (LogEntry.raw_data.ilike("%failed logon%")) |
                    ((LogEntry.log_source == "sshd") & (LogEntry.raw_data.ilike("%failed%")))
                )
                .count()
            )

            # Trigger alert on 5+ failures
            if failed_count >= 5:
                # Anti-flooding duplicate check
                duplicate_alert = (
                    self.db.query(Alert)
                    .filter(Alert.title == f"Brute Force detected from {log_entry.source_ip}")
                    .filter(Alert.created_at >= time_threshold)
                    .first()
                )
                if not duplicate_alert:
                    alert = Alert(
                        title=f"Brute Force detected from {log_entry.source_ip}",
                        description=(
                            f"Multiple failed logon attempts ({failed_count}) detected from host "
                            f"at IP {log_entry.source_ip} within a 60-second window."
                        ),
                        severity="HIGH",
                        status="NEW",
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
                    alerts_triggered.append(alert)

        # Rule 2: Anomalous Multi-Service Access Probe
        if log_entry.source_ip:
            time_threshold_probe = (datetime.now(timezone.utc) - timedelta(minutes=2)).replace(tzinfo=None)
            
            # Get list of unique log sources targeted by this IP in the last 2 minutes
            recent_services = (
                self.db.query(LogEntry.log_source)
                .filter(LogEntry.source_ip == log_entry.source_ip)
                .filter(LogEntry.ingested_at >= time_threshold_probe)
                .distinct()
                .all()
            )
            service_list = [s[0] for s in recent_services if s[0]]
            
            if len(service_list) >= 3:
                # Anti-flooding duplicate check
                duplicate_probe = (
                    self.db.query(Alert)
                    .filter(Alert.title == f"Anomalous Service Probe from {log_entry.source_ip}")
                    .filter(Alert.created_at >= time_threshold_probe)
                    .first()
                )
                if not duplicate_probe:
                    alert = Alert(
                        title=f"Anomalous Service Probe from {log_entry.source_ip}",
                        description=(
                            f"Host at IP {log_entry.source_ip} generated log entries targeting "
                            f"{len(service_list)} distinct services ({', '.join(service_list)}) inside a 2-minute window."
                        ),
                        severity="MEDIUM",
                        status="NEW",
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
                    alerts_triggered.append(alert)

        return alerts_triggered
