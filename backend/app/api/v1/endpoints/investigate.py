import re
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.log_entry import LogEntry
from app.models.alert import Alert

router = APIRouter()


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # e.g., "attacker", "service", "alert", "log"
    group: str
    severity: str = "INFO"


class GraphLink(BaseModel):
    source: str
    target: str
    label: str


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]


@router.get("/{ip_or_host}", response_model=GraphResponse, summary="Retrieve forensic graph timeline for host")
def investigate_host(ip_or_host: str, db: Session = Depends(get_db)) -> GraphResponse:
    """
    Retrieves associated alerts, service connections, and log parameters
    for a given IP address, forming a node-link network map.
    """
    nodes_map: Dict[str, GraphNode] = {}
    links: List[GraphLink] = []

    # 1. Add primary source entity
    nodes_map[ip_or_host] = GraphNode(
        id=ip_or_host,
        label=ip_or_host,
        type="attacker",
        group="attacker",
        severity="CRITICAL"
    )

    # 2. Query logs matching the IP address
    matching_logs = (
        db.query(LogEntry)
        .filter((LogEntry.source_ip == ip_or_host) | (LogEntry.destination_ip == ip_or_host))
        .limit(20)
        .all()
    )

    services_discovered = set()
    for log in matching_logs:
        service_name = log.log_source if log.log_source else "unknown_service"
        services_discovered.add(service_name)
        
        # Add log details as small nodes linked to services
        log_node_id = f"log_{log.id}"
        nodes_map[log_node_id] = GraphNode(
            id=log_node_id,
            label=f"Log #{log.id} ({log.severity})",
            type="log",
            group="log",
            severity=log.severity
        )
        # Link log to service
        links.append(GraphLink(
            source=f"service_{service_name}",
            target=log_node_id,
            label="EVENT"
        ))

    # Add service nodes and link to central IP
    for service_name in services_discovered:
        service_node_id = f"service_{service_name}"
        nodes_map[service_node_id] = GraphNode(
            id=service_node_id,
            label=service_name.upper(),
            type="service",
            group="service",
            severity="INFO"
        )
        links.append(GraphLink(
            source=ip_or_host,
            target=service_node_id,
            label="ACCESS"
        ))

    # 3. Query alerts matching the IP address in description or title
    ip_esc = re.escape(ip_or_host)
    all_alerts = db.query(Alert).all()
    matching_alerts = []
    for alert in all_alerts:
        if ip_or_host in alert.title or ip_or_host in alert.description:
            matching_alerts.append(alert)

    for alert in matching_alerts:
        alert_node_id = f"alert_{alert.id}"
        nodes_map[alert_node_id] = GraphNode(
            id=alert_node_id,
            label=alert.title,
            type="alert",
            group="alert",
            severity=alert.severity
        )
        # Link alert directly to the actor IP node
        links.append(GraphLink(
            source=ip_or_host,
            target=alert_node_id,
            label="TRIGGERED"
        ))

    return GraphResponse(
        nodes=list(nodes_map.values()),
        links=links
    )
