import re
from datetime import datetime, timezone
from typing import Optional
from app.services.parsers.base import BaseParser, ParsedLog, ParserError


class SyslogParser(BaseParser):
    """
    Parser for standard Syslog formats (RFC 3164 and RFC 5424).
    Extracts timestamps, hostnames, severities, and source IPs where possible.
    """
    
    # RFC 5424 regex pattern: <PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCTURED-DATA MSG
    RFC5424_PATTERN = re.compile(
        r"^<(?P<pri>\d+)>1\s+"
        r"(?P<timestamp>[^\s]+)\s+"
        r"(?P<hostname>[^\s]+)\s+"
        r"(?P<appname>[^\s]+)\s+"
        r"(?P<procid>[^\s]+)\s+"
        r"(?P<msgid>[^\s]+)\s+"
        r"(?P<sd>-\s*|\[.*\])\s*"
        r"(?P<msg>.*)$"
    )

    # RFC 3164 regex pattern: <PRI>TIMESTAMP HOSTNAME TAG: MSG
    RFC3164_PATTERN = re.compile(
        r"^<(?P<pri>\d+)>"
        r"(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+"
        r"(?P<hostname>[^\s]+)\s+"
        r"(?P<tag>[a-zA-Z0-9_\-\/\(\)]+)(?:\[\d+\])?:?\s+"
        r"(?P<msg>.*)$"
    )


    IP_PATTERN = re.compile(
        r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
    )

    def _priority_to_severity(self, pri_str: str) -> str:
        """
        Maps Syslog numerical priority (<PRI>) to standard platform severity levels.
        Formula: Priority = (Facility * 8) + Severity
        """
        try:
            pri = int(pri_str)
            syslog_severity = pri % 8
            # Syslog severity maps:
            # 0: Emergency, 1: Alert, 2: Critical, 3: Error -> CRITICAL
            # 4: Warning -> WARNING
            # 5: Notice, 6: Informational, 7: Debug -> INFO
            if syslog_severity <= 3:
                return "CRITICAL"
            elif syslog_severity == 4:
                return "WARNING"
            else:
                return "INFO"
        except Exception:
            return "INFO"

    def _extract_ip(self, text: str) -> Optional[str]:
        """Helper to extract the first IPv4 address found in a string."""
        match = self.IP_PATTERN.search(text)
        return match.group(0) if match else None

    def parse(self, raw_data: str) -> ParsedLog:
        # Trim whitespace
        line = raw_data.strip()

        # Try RFC 5424 matching
        match_5424 = self.RFC5424_PATTERN.match(line)
        if match_5424:
            gd = match_5424.groupdict()
            try:
                # Parse RFC 3339 timestamp (e.g. 2003-10-11T22:14:15.003Z)
                ts_str = gd["timestamp"]
                # Replace Z with timezone info
                if ts_str.endswith("Z"):
                    ts_str = ts_str[:-1] + "+00:00"
                dt = datetime.fromisoformat(ts_str)
            except Exception:
                dt = datetime.now(timezone.utc)
            
            severity = self._priority_to_severity(gd["pri"])
            msg = gd["msg"]
            source_ip = self._extract_ip(msg)
            
            return ParsedLog(
                raw_data=line,
                log_source=gd["appname"] or "syslog_rfc5424",
                severity=severity,
                source_ip=source_ip,
                destination_ip=None,
                event_timestamp=dt
            )

        # Try RFC 3164 matching
        match_3164 = self.RFC3164_PATTERN.match(line)
        if match_3164:
            gd = match_3164.groupdict()
            try:
                # Parse classic syslog month day time (no year) -> use current year
                ts_str = f"{gd['timestamp']} {datetime.now(timezone.utc).year}"
                dt = datetime.strptime(ts_str, "%b %d %H:%M:%S %Y")
                dt = dt.replace(tzinfo=timezone.utc)
            except Exception:
                dt = datetime.now(timezone.utc)
                
            severity = self._priority_to_severity(gd["pri"])
            msg = gd["msg"]
            source_ip = self._extract_ip(msg)
            
            return ParsedLog(
                raw_data=line,
                log_source=gd["tag"] or "syslog_rfc3164",
                severity=severity,
                source_ip=source_ip,
                destination_ip=None,
                event_timestamp=dt
            )

        # Fallback parser for unstructured logs
        # Attempt to find standard timestamp patterns, severity flags, and IPs
        severity = "INFO"
        if "CRITICAL" in line.upper() or "ERROR" in line.upper() or "FAILURE" in line.upper():
            severity = "CRITICAL"
        elif "WARN" in line.upper():
            severity = "WARNING"

        source_ip = self._extract_ip(line)
        
        return ParsedLog(
            raw_data=line,
            log_source="syslog_unstructured",
            severity=severity,
            source_ip=source_ip,
            destination_ip=None,
            event_timestamp=datetime.now(timezone.utc)
        )
