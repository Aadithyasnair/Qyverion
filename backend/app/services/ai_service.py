import json
import logging
import httpx
from typing import Generator
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
        Communicates with local Ollama service. Returns full text response.
        """
        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": 1200,
                "temperature": 0.2,
                "stop": ["</s>", "[INST]", "[/INST]"]
            }
        }
        try:
            logger.info(f"Sending prompt to local Ollama service at {OLLAMA_URL} with model '{DEFAULT_MODEL}'")
            response = httpx.post(OLLAMA_URL, json=payload, timeout=120.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                logger.warning(f"Ollama returned HTTP error status: {response.status_code}")
                payload["model"] = "llama3"
                logger.info("Attempting fallback with model 'llama3'...")
                response_fb = httpx.post(OLLAMA_URL, json=payload, timeout=120.0)
                if response_fb.status_code == 200:
                    return response_fb.json().get("message", {}).get("content", "")
        except Exception as err:
            logger.warning(f"Ollama connection failed or timed out: {str(err)}. Falling back to local security rules.")
        
        return ""

    def _call_ollama_stream(self, messages: list[dict]) -> Generator[str, None, None]:
        """
        Communicates with local Ollama using streaming mode.
        Yields text chunks as they are produced by the model.
        Falls back to yielding the non-streamed full response if streaming fails.
        """
        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": 0.2,
                "stop": ["</s>", "[INST]", "[/INST]"]
            }
        }
        try:
            logger.info(f"Opening streaming connection to Ollama at {OLLAMA_URL}")
            with httpx.stream("POST", OLLAMA_URL, json=payload, timeout=120.0) as response:
                if response.status_code == 200:
                    for raw_line in response.iter_lines():
                        if not raw_line:
                            continue
                        try:
                            data = json.loads(raw_line)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield content
                            if data.get("done"):
                                return
                        except json.JSONDecodeError:
                            continue
                else:
                    # Fallback: try llama3 model
                    payload["model"] = "llama3"
                    with httpx.stream("POST", OLLAMA_URL, json=payload, timeout=120.0) as fb:
                        if fb.status_code == 200:
                            for raw_line in fb.iter_lines():
                                if not raw_line:
                                    continue
                                try:
                                    data = json.loads(raw_line)
                                    content = data.get("message", {}).get("content", "")
                                    if content:
                                        yield content
                                    if data.get("done"):
                                        return
                                except json.JSONDecodeError:
                                    continue
        except Exception as err:
            logger.warning(f"Ollama streaming failed: {str(err)}")

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
        logs_context = "\n".join([f"- [{log.event_timestamp}] {log.raw_data[:120]}" for log in logs[:5]])
        
        prompt = (
            f"Generate a concise incident response playbook for this security alert. "
            f"Keep the ENTIRE response under 600 words. Use only these 4 sections with ### headers:\n\n"
            f"### Executive Summary\n"
            f"### Immediate Containment (include 1-2 bash commands)\n"
            f"### Investigation Steps (3 bullet points max)\n"
            f"### Hardening Recommendations (3 bullet points max)\n\n"
            f"Alert Title: {alert.title}\n"
            f"Severity: {alert.severity}\n"
            f"Description: {alert.description}\n\n"
            f"Recent Logs:\n{logs_context}\n\n"
            f"Write the complete playbook now. Do not add extra sections or lengthy explanations."
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

    def generate_playbook_stream(self, alert: Alert, logs: list) -> Generator[str, None, None]:
        """
        Streaming version of generate_playbook.
        Yields text chunks from the Ollama streaming API.
        If Ollama is unreachable, yields the fallback playbook text as a single chunk.
        """
        logs_context = "\n".join([f"- [{log.event_timestamp}] {log.raw_data[:120]}" for log in logs[:5]])

        prompt = (
            f"Generate a concise incident response playbook for this security alert. "
            f"Keep the ENTIRE response under 600 words. Use only these 4 sections with ### headers:\n\n"
            f"### Executive Summary\n"
            f"### Immediate Containment (include 1-2 bash commands)\n"
            f"### Investigation Steps (3 bullet points max)\n"
            f"### Hardening Recommendations (3 bullet points max)\n\n"
            f"Alert Title: {alert.title}\n"
            f"Severity: {alert.severity}\n"
            f"Description: {alert.description}\n\n"
            f"Recent Logs:\n{logs_context}\n\n"
            f"Write the complete playbook now. Do not add extra sections or lengthy explanations."
        )

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        # Try Ollama streaming first
        yielded_any = False
        for chunk in self._call_ollama_stream(messages):
            yielded_any = True
            yield chunk

        # If Ollama was unreachable, yield the fallback playbook
        if not yielded_any:
            title_lower = alert.title.lower()
            if "brute force" in title_lower:
                fallback = (
                    f"# 📋 Security Playbook: Brute Force Containment\n\n"
                    f"**Alert:** {alert.title} | **Severity:** {alert.severity}\n\n"
                    f"### Executive Summary\n"
                    f"Multiple failed login attempts from a single source IP indicate a brute-force credentials attack.\n\n"
                    f"### Immediate Containment\n"
                    f"Block the attacker IP on the perimeter gateway:\n"
                    f"```bash\n"
                    f"iptables -A INPUT -s {alert.description.split('IP ')[1].split(' ')[0] if 'IP ' in alert.description else 'ATTACKER_IP'} -j DROP\n"
                    f"fail2ban-client set sshd banip ATTACKER_IP\n"
                    f"```\n\n"
                    f"### Investigation Steps\n"
                    f"- Review auth.log for successful logins from the same IP.\n"
                    f"- Check if any accounts were compromised during the window.\n"
                    f"- Audit target service (SSH/RDP) for exposed credentials.\n\n"
                    f"### Hardening Recommendations\n"
                    f"- Enable fail2ban with maxretry=3 and bantime=3600.\n"
                    f"- Disable password auth for SSH; enforce key-based login.\n"
                    f"- Restrict admin access to known IP allowlists.\n\n"
                    f"*(Fallback: Ollama unreachable — showing expert rule-based playbook)*"
                )
            elif "threat" in title_lower or "indicator" in title_lower:
                fallback = (
                    f"# 📋 Security Playbook: Threat Intelligence Match\n\n"
                    f"**Alert:** {alert.title} | **Severity:** {alert.severity}\n\n"
                    f"### Executive Summary\n"
                    f"A connection matched an active Threat Intelligence IoC linked to a known malicious actor.\n\n"
                    f"### Immediate Containment\n"
                    f"```bash\n"
                    f"iptables -A INPUT -s MALICIOUS_IP -j DROP\n"
                    f"iptables -A OUTPUT -d MALICIOUS_IP -j DROP\n"
                    f"```\n\n"
                    f"### Investigation Steps\n"
                    f"- Identify internal hosts communicating with the flagged IP.\n"
                    f"- Examine payload content for C2 beacon patterns.\n"
                    f"- Check DNS query history for domain association.\n\n"
                    f"### Hardening Recommendations\n"
                    f"- Subscribe to automated threat feed sync (AbuseIPDB, OTX).\n"
                    f"- Enable egress filtering on perimeter firewall.\n"
                    f"- Deploy DNS sinkholing for known malicious domains.\n\n"
                    f"*(Fallback: Ollama unreachable — showing expert rule-based playbook)*"
                )
            else:
                fallback = (
                    f"# 📋 Security Playbook: Incident Remediation\n\n"
                    f"**Alert:** {alert.title} | **Severity:** {alert.severity}\n\n"
                    f"### Executive Summary\n"
                    f"A security event was detected requiring immediate analyst attention.\n\n"
                    f"### Immediate Containment\n"
                    f"```bash\n"
                    f"# Isolate affected host\n"
                    f"iptables -A INPUT -s AFFECTED_IP -j DROP\n"
                    f"```\n\n"
                    f"### Investigation Steps\n"
                    f"- Collect full packet capture from affected network segment.\n"
                    f"- Review all authentication events in the past 24 hours.\n"
                    f"- Correlate alert with concurrent anomalies in other services.\n\n"
                    f"### Hardening Recommendations\n"
                    f"- Enforce least-privilege access controls across all services.\n"
                    f"- Enable centralized SIEM alerting for all authentication events.\n"
                    f"- Schedule quarterly security posture reviews.\n\n"
                    f"*(Fallback: Ollama unreachable — showing expert rule-based playbook)*"
                )
            yield fallback

