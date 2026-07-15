import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.services.parsers.base import BaseParser, ParsedLog, ParserError


class WindowsEventParser(BaseParser):
    """
    Parser for Windows Event Logs (JSON structures emitted by Winlogbeat, NXLog, or Event Forwarding).
    Identifies Windows security event IDs (e.g., successful/failed logins, account creation).
    """

    # Security event IDs mappings:
    CRITICAL_EVENT_IDS = {
        4625,  # An account failed to log on
        4720,  # A user account was created (needs tracking)
        4722,  # A user account was enabled
        4724,  # An attempt was made to reset an account's password
        4728,  # A member was added to a security-enabled global group
        4732,  # A member was added to a security-enabled local group (e.g., Administrators)
        4756,  # A member was added to a security-enabled universal group
        1102,  # The audit log was cleared (Very Critical)
    }

    def _get_nested(self, data: Dict[str, Any], keys: list) -> Optional[Any]:
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def parse(self, raw_data: str) -> ParsedLog:
        try:
            data = json.loads(raw_data)
            if not isinstance(data, dict):
                raise ParserError("Windows Event payload must be a JSON object.")
        except json.JSONDecodeError as e:
            raise ParserError(f"Invalid JSON string payload: {str(e)}")

        # Extract Event ID
        event_id_val = (
            data.get("EventID")
            or data.get("event_id")
            or self._get_nested(data, ["winlog", "event_id"])
            or self._get_nested(data, ["event", "code"])
        )
        
        event_id = None
        if event_id_val is not None:
            try:
                event_id = int(event_id_val)
            except ValueError:
                pass

        # Extract Channel (Log Name)
        channel = (
            data.get("Channel")
            or data.get("LogName")
            or self._get_nested(data, ["winlog", "channel"])
            or "Security"
        )

        # Extract Source IP
        # In Winlogbeat / NXLog, source IP is typically nested inside EventData/IpAddress or winlog/event_data/IpAddress
        source_ip = (
            self._get_nested(data, ["EventData", "IpAddress"])
            or self._get_nested(data, ["winlog", "event_data", "IpAddress"])
            or self._get_nested(data, ["winlog", "event_data", "IpAddress"])
            or data.get("IpAddress")
            or data.get("source_ip")
        )
        if source_ip and str(source_ip).strip() in ["-", ""]:
            source_ip = None

        # Determine Severity based on Event ID and Keywords
        severity = "INFO"
        keyword = str(data.get("Keywords") or data.get("level") or "").upper()
        
        if event_id in self.CRITICAL_EVENT_IDS or "AUDIT FAILURE" in keyword or "ERROR" in keyword:
            severity = "CRITICAL"
        elif "WARNING" in keyword:
            severity = "WARNING"
        elif event_id == 4624:  # Successful logon is INFO, but we track it
            severity = "INFO"

        # Build Source Name
        log_source = f"windows_event_{event_id}" if event_id else "windows_event"
        if channel:
            log_source = f"winlog_{str(channel).lower()}"
            if event_id:
                log_source += f"_{event_id}"

        # Extract Timestamp
        ts_val = (
            data.get("TimeCreated")
            or data.get("Time")
            or self._get_nested(data, ["winlog", "time_created"])
            or self._get_nested(data, ["event", "created"])
        )
        if isinstance(ts_val, dict):
            # Sometimes TimeCreated is represented as {"SystemTime": "2026-07-15T21:30:00.000000000Z"}
            ts_val = ts_val.get("SystemTime") or ts_val.get("@SystemTime")

        dt = None
        if ts_val:
            try:
                ts_str = str(ts_val)
                if ts_str.endswith("Z"):
                    ts_str = ts_str[:-1] + "+00:00"
                dt = datetime.fromisoformat(ts_str)
            except Exception:
                dt = None

        if dt is None:
            dt = datetime.now(timezone.utc)

        return ParsedLog(
            raw_data=raw_data,
            log_source=log_source,
            severity=severity,
            source_ip=str(source_ip) if source_ip else None,
            destination_ip=None,
            event_timestamp=dt
        )
