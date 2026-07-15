import logging
import httpx
from datetime import datetime, timezone
from app.models.alert import Alert

logger = logging.getLogger("app.services.ai_service")

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3.2"


class AIService:
    """
    AI Security Analyst Service powered by a local Ollama instance running Llama 3.2.
    Falls back to a high-fidelity local security playbook engine if Ollama is unreachable.
    """

    def __init__(self):
        self.system_prompt = (
            "You are Qyverion AI Copilot, a Senior Staff Security Analyst and Incident Responder. "
            "Your job is to analyze security logs, explain incident alerts, suggest remediation actions, "
            "and output detailed mitigation playbooks in clean markdown format."
        )

    def _call_ollama(self, messages: list[dict]) -> str:
        """
        Communicates with local Ollama service.
        """
        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": 300,
                "temperature": 0.2
            }
        }
        try:
            logger.info(f"Sending prompt to local Ollama service at {OLLAMA_URL} with model '{DEFAULT_MODEL}' (snappy limits)")
            # Connect with a 90-second timeout to allow local model generation to finish on CPU
            response = httpx.post(OLLAMA_URL, json=payload, timeout=90.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                logger.warning(f"Ollama returned HTTP error status: {response.status_code}")
                # Try fallback model llama3
                payload["model"] = "llama3"
                logger.info("Attempting fallback with model 'llama3'...")
                response_fb = httpx.post(OLLAMA_URL, json=payload, timeout=90.0)
                if response_fb.status_code == 200:
                    return response_fb.json().get("message", {}).get("content", "")
        except Exception as err:
            logger.warning(f"Ollama connection failed or timed out: {str(err)}. Falling back to local security rules.")
        
        return ""

    def analyze_log(self, raw_log: str) -> str:
        """
        Explains a raw log and details potential security impacts.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": (
                    f"Analyze the following raw log entry. Explain what it means, what potential "
                    f"threats are associated with it, and what next steps an analyst should take:\n\n"
                    f"Raw Log: {raw_log}"
                )
            }
        ]
        
        response = self._call_ollama(messages)
        if response:
            return response
            
        # Hardcoded High-Fidelity Fallback Response
        return (
            f"### 🛡️ Local Security Analysis Fallback\n\n"
            f"**Log Received:** `{raw_log[:100]}...`\n\n"
            f"**Heuristic Interpretation:**\n"
            f"- **Classification:** Unstructured / General System activity\n"
            f"- **Recommended Actions:**\n"
            f"  1. Verify if the source IP matches known organization assets.\n"
            f"  2. Check target application parameters for payload anomalies.\n"
            f"  3. Correlate with concurrent alerts from the same segment.\n\n"
            f"*(Note: Local Ollama server at http://localhost:11434 was unreachable, showing fallback expert rule analysis)*"
        )

    def generate_playbook(self, alert: Alert, logs: list) -> str:
        """
        Generates a contextual response playbook for a triggered Alert.
        """
        logs_context = "\n".join([f"- [{log.event_timestamp}] {log.raw_data}" for log in logs])
        
        prompt = (
            f"Create a detailed incident response remediation playbook for this alert:\n"
            f"- Alert Title: {alert.title}\n"
            f"- Severity: {alert.severity}\n"
            f"- Description: {alert.description}\n\n"
            f"Associated Log History:\n{logs_context}\n\n"
            f"Please structure the output with clean markdown headings: Executive Summary, "
            f"Immediate Containment Actions (including blocking CLI commands), Investigation Steps, "
            f"and Long-Term Hardening Recommendations."
        )

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        response = self._call_ollama(messages)
        if response:
            return response

        # Hardcoded Custom Fallback Playbooks based on Alert Title
        title_lower = alert.title.lower()
        if "brute force" in title_lower:
            return (
                f"# 📋 Security Playbook: Logon Brute Force Containment\n\n"
                f"**Target Alert:** {alert.title}\n"
                f"**Severity:** {alert.severity}\n\n"
                f"### 1. Executive Summary\n"
                f"Multiple authentication failures from a single IP suggest a credentials brute-forcing campaign or a dictionary attack.\n\n"
                f"### 2. Immediate Containment Actions\n"
                f"Block the offending IP immediately. Run the following command on the perimeter gateway / host:\n"
                f"```bash\n"
                f"# Linux iptables containment\n"
                f"iptables -A INPUT -s {alert.description.split('IP ')[1].split(' ')[0] if 'IP ' in alert.description else 'offending_ip'} -j DROP\n"
                f"```\n\n"
                f"### 3. Investigation Steps\n"
                f"- Audit target account login success states in logs.\n"
                f"- Check if accounts have multi-factor authentication (MFA) enabled.\n"
                f"- Conduct network flow analysis to detect outbound scan behavior.\n\n"
                f"### 4. Hardening Recommendations\n"
                f"- Enforce fail2ban limits (maxretry = 3).\n"
                f"- Disable password logins for SSH; enforce key-based authentication.\n\n"
                f"*(Note: Local Ollama server at http://localhost:11434 was unreachable, showing fallback expert rule analysis)*"
            )
        elif "threat" in title_lower or "indicator" in title_lower:
            return (
                f"# 📋 Security Playbook: Malicious IP Traffic Detected\n\n"
                f"**Target Alert:** {alert.title}\n"
                f"**Severity:** {alert.severity}\n\n"
                f"### 1. Executive Summary\n"
                f"Connection attempt matches an active Threat Intelligence indicator associated with known malicious actors.\n\n"
                f"### 2. Immediate Containment Actions\n"
                f"Add block rules on external firewalls for the indicator IP:\n"
                f"```bash\n"
                f"# Cisco ASA block command\n"
                f"access-list OUTSIDE_IN extended deny ip host {alert.title.split(': ')[1] if ': ' in alert.title else 'malicious_ip'} any\n"
                f"```\n\n"
                f"### 3. Investigation Steps\n"
                f"- Identify internal target nodes communicating with this IP.\n"
                f"- Examine payload size for data exfiltration patterns.\n\n"
                f"*(Note: Local Ollama server at http://localhost:11434 was unreachable, showing fallback expert rule analysis)*"
            )
        
        # General Fallback Playbook
        return (
            f"# 📋 Security Playbook: Incident Remediation\n\n"
            f"**Target Alert:** {alert.title}\n"
            f"**Severity:** {alert.severity}\n\n"
            f"### Actions:\n"
            f"1. Isolate the target host from the network.\n"
            f"2. Audit all credentials active during the event.\n"
            f"3. Re-image compromised assets.\n\n"
            f"*(Note: Local Ollama server at http://localhost:11434 was unreachable, showing fallback expert rule analysis)*"
        )
