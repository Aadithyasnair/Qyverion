import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.services.parsers.base import BaseParser, ParsedLog, ParserError


class JSONParser(BaseParser):
    """
    Parser for structured JSON logs.
    Handles dynamic schema mappings, extracting security variables nested inside fields.
    """

    def _get_nested_field(self, data: Dict[str, Any], keys: list) -> Optional[Any]:
        """Traverses a nested dictionary given a list of keys."""
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
                raise ParserError("JSON log payload must be a JSON object.")
        except json.JSONDecodeError as e:
            raise ParserError(f"Invalid JSON string payload: {str(e)}")

        # Extract log source
        # Prioritize string service/app name over network 'source' dictionary
        log_source = None
        for key in ["log_source", "app_name", "service", "source"]:
            val = data.get(key)
            if isinstance(val, str) and val:
                log_source = val
                break
            elif isinstance(val, dict):
                val_name = val.get("name") or val.get("service")
                if isinstance(val_name, str) and val_name:
                    log_source = val_name
                    break
        
        if not log_source:
            log_source = "json_source"


        # Extract severity & standardize
        raw_severity = (
            data.get("severity")
            or data.get("level")
            or data.get("log_level")
            or self._get_nested_field(data, ["log", "level"])
            or "INFO"
        )
        raw_severity = str(raw_severity).upper()
        if "CRIT" in raw_severity or "ERR" in raw_severity or "FATAL" in raw_severity:
            severity = "CRITICAL"
        elif "WARN" in raw_severity:
            severity = "WARNING"
        else:
            severity = "INFO"

        # Extract source IP (checks common flattened and nested keys)
        source_ip = (
            data.get("source_ip")
            or data.get("src_ip")
            or self._get_nested_field(data, ["source", "ip"])
            or self._get_nested_field(data, ["network", "source", "ip"])
        )
        if source_ip:
            source_ip = str(source_ip)

        # Extract destination IP
        destination_ip = (
            data.get("destination_ip")
            or data.get("dest_ip")
            or self._get_nested_field(data, ["destination", "ip"])
            or self._get_nested_field(data, ["network", "destination", "ip"])
        )
        if destination_ip:
            destination_ip = str(destination_ip)

        # Extract timestamp
        ts_val = (
            data.get("event_timestamp")
            or data.get("timestamp")
            or data.get("@timestamp")
            or data.get("time")
            or self._get_nested_field(data, ["event", "timestamp"])
        )
        
        dt = None
        if ts_val:
            try:
                # Handle numeric unix timestamps (seconds or milliseconds)
                if isinstance(ts_val, (int, float)):
                    if ts_val > 1e11:  # Milliseconds timestamp
                        ts_val = ts_val / 1000.0
                    dt = datetime.fromtimestamp(ts_val, tz=timezone.utc)
                else:
                    # String ISO format
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
            log_source=str(log_source),
            severity=severity,
            source_ip=source_ip,
            destination_ip=destination_ip,
            event_timestamp=dt
        )
