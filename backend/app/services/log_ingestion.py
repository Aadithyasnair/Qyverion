import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.log_entry import LogEntry
from app.models.alert import Alert
from app.models.threat_indicator import ThreatIndicator
from app.services.parsers import SyslogParser, JSONParser, WindowsEventParser, ParserError
from app.schemas.log_entry import LogEntryCreate

logger = logging.getLogger("app.services.log_ingestion")


class LogIngestionService:
    """
    Ingestion service that coordinates raw log parsing, database storage, 
    threat intelligence cross-referencing, and automatic alerting.
    """

    def __init__(self, db: Session):
        self.db = db
        self.syslog_parser = SyslogParser()
        self.json_parser = JSONParser()
        self.windows_parser = WindowsEventParser()

    def _detect_and_parse(self, raw_data: str, source_hint: str) -> any:
        """
        Heuristically selects the most appropriate parser based on raw data format
        and metadata source hint.
        """
        trimmed = raw_data.strip()
        source_lower = source_hint.lower()

        # 1. Windows Event Ingestion
        if "windows" in source_lower or "winlog" in source_lower:
            try:
                return self.windows_parser.parse(trimmed)
            except ParserError as e:
                logger.warning(f"Windows parser failed, attempting JSON fallback: {str(e)}")

        # 2. JSON Ingestion
        if trimmed.startswith("{") and trimmed.endswith("}"):
            try:
                return self.json_parser.parse(trimmed)
            except ParserError as e:
                logger.warning(f"JSON parser failed, attempting Syslog fallback: {str(e)}")

        # 3. Syslog / Unstructured Ingestion
        return self.syslog_parser.parse(trimmed)

    def _check_threat_intel(self, ip: str) -> None:
        """
        Query threat intelligence database for known malicious IPs.
        Automatically triggers a critical alert upon match.
        """
        if not ip:
            return

        # Query the database
        indicator = (
            self.db.query(ThreatIndicator)
            .filter(ThreatIndicator.indicator_value == ip)
            .first()
        )

        if indicator:
            logger.warning(f"THREAT INTEL MATCH DETECTED: IP address {ip} found in threat indicators!")
            
            # Auto-generate a security incident alert
            alert = Alert(
                title=f"Threat Intelligence Match: {ip}",
                description=(
                    f"A log event matched threat indicator '{ip}' associated with threat actor "
                    f"'{indicator.threat_actor}' (Risk Score: {indicator.risk_score}/100)."
                ),
                severity="CRITICAL" if indicator.risk_score >= 80 else "HIGH",
                status="NEW",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            self.db.add(alert)

    def ingest(self, payload: LogEntryCreate) -> LogEntry:
        """
        Main entrypoint to ingest, parse, match threat intel, and persist logs.
        """
        # Parse log payload
        parsed = self._detect_and_parse(payload.raw_data, payload.log_source)

        # Create database entity
        db_log = LogEntry(
            raw_data=parsed.raw_data,
            log_source=parsed.log_source if parsed.log_source != "syslog_unstructured" else payload.log_source,
            severity=parsed.severity,
            source_ip=parsed.source_ip,
            destination_ip=parsed.destination_ip,
            event_timestamp=parsed.event_timestamp,
            ingested_at=datetime.now(timezone.utc),
        )

        self.db.add(db_log)
        self.db.flush()
        
        # Check source and destination IPs against active threat indicators
        if parsed.source_ip:
            self._check_threat_intel(parsed.source_ip)
        if parsed.destination_ip:
            self._check_threat_intel(parsed.destination_ip)

        # 3. Evaluate correlation rules against the active log history
        try:
            from app.services.correlation_engine import CorrelationEngine
            corr_engine = CorrelationEngine(self.db)
            triggered_alerts = corr_engine.evaluate(db_log)
            for alert in triggered_alerts:
                self.db.add(alert)
        except Exception as e:
            logger.error(f"Correlation Engine failed to process log entry: {str(e)}")

        # Commit transaction
        self.db.commit()
        self.db.refresh(db_log)

        return db_log
