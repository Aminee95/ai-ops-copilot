import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, Float, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


def gen_uuid():
    return str(uuid.uuid4())


class Severity(str, enum.Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class IncidentStatus(str, enum.Enum):
    DETECTED = "detected"
    TRIAGED = "triaged"
    DIAGNOSING = "diagnosing"
    RESOLVING = "resolving"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Alert(Base):
    """Une alerte brute, telle qu'émise par le système de monitoring (simulé)."""

    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    source = Column(String, nullable=False)
    metric_name = Column(String, nullable=False)
    value = Column(Float, nullable=True)
    message = Column(Text, nullable=False)
    raw_payload = Column(JSON, nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow)

    incident_id = Column(UUID(as_uuid=False), ForeignKey("incidents.id"), nullable=True)
    incident = relationship("Incident", back_populates="alerts")


class Incident(Base):
    """Un incident consolidé, résultat du regroupement d'une ou plusieurs alertes."""

    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    severity = Column(Enum(Severity), nullable=False, default=Severity.MINOR)
    status = Column(Enum(IncidentStatus), nullable=False, default=IncidentStatus.DETECTED)

    root_cause_hypothesis = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)

    resolution_action = Column(Text, nullable=True)
    auto_resolved = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    alerts = relationship("Alert", back_populates="incident")
    timeline_events = relationship(
        "TimelineEvent", back_populates="incident", order_by="TimelineEvent.timestamp"
    )


class TimelineEvent(Base):
    """Chaque étape du traitement d'un incident, tracée pour le dashboard et le post-mortem."""

    __tablename__ = "timeline_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    incident_id = Column(UUID(as_uuid=False), ForeignKey("incidents.id"), nullable=False)
    agent_name = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="timeline_events")