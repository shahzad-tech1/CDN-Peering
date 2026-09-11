from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class CDNProvider(db.Model):
    __tablename__ = "cdn_provider"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    asn = db.Column(db.String(20), default="")
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    resources = db.relationship(
        "Resource", backref="provider", lazy="dynamic"
    )
    policy_rules = db.relationship(
        "PolicyRule", backref="provider", lazy="dynamic"
    )


class Resource(db.Model):  # R1 — SR
    __tablename__ = "resource"

    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.String(20), unique=True, nullable=False)
    provider_id = db.Column(
        db.Integer, db.ForeignKey("cdn_provider.id"), nullable=False
    )
    cpu = db.Column(db.Float, nullable=False)
    storage_gb = db.Column(db.Float, nullable=False)
    upload_rate = db.Column(db.Float, nullable=False)
    download_rate = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class PolicyRule(db.Model):  # R3 — PR
    __tablename__ = "policy_rule"

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(
        db.Integer, db.ForeignKey("cdn_provider.id"), nullable=False
    )
    min_cpu_available = db.Column(db.Float, nullable=False)
    max_delegated_pct = db.Column(db.Float, nullable=False)
    max_request_rate = db.Column(db.Integer, default=15000)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )


class PeeringRequest(db.Model):  # R2
    __tablename__ = "peering_request"

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(
        db.Integer, db.ForeignKey("cdn_provider.id"), nullable=False
    )
    target_provider_id = db.Column(
        db.Integer, db.ForeignKey("cdn_provider.id"), nullable=True
    )
    load_pct = db.Column(db.Float, nullable=False)
    request_rate = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="pending")
    reject_reason = db.Column(db.String(255), default="")
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    provider = db.relationship(
        "CDNProvider", foreign_keys=[provider_id], backref="peering_requests"
    )
    target_provider = db.relationship(
        "CDNProvider", foreign_keys=[target_provider_id]
    )


class PeeringArrangement(db.Model):  # R4/R5/R6
    __tablename__ = "peering_arrangement"

    id = db.Column(db.Integer, primary_key=True)
    primary_provider_id = db.Column(
        db.Integer, db.ForeignKey("cdn_provider.id"), nullable=False
    )
    peer_provider_id = db.Column(
        db.Integer, db.ForeignKey("cdn_provider.id"), nullable=False
    )
    request_id = db.Column(
        db.Integer, db.ForeignKey("peering_request.id"), nullable=True
    )
    status = db.Column(db.String(20), default="active")
    accounting_units = db.Column(db.Float, default=0.0)
    max_accounting_units = db.Column(db.Float, default=50000.0)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    primary_provider = db.relationship(
        "CDNProvider", foreign_keys=[primary_provider_id]
    )
    peer_provider = db.relationship(
        "CDNProvider", foreign_keys=[peer_provider_id]
    )
    request = db.relationship("PeeringRequest", backref="arrangement")


class NegotiationLog(db.Model):
    __tablename__ = "negotiation_log"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(
        db.Integer, db.ForeignKey("peering_request.id"), nullable=True
    )
    arrangement_id = db.Column(
        db.Integer, db.ForeignKey("peering_arrangement.id"), nullable=True
    )
    action = db.Column(db.String(50), default="info")
    message = db.Column(db.String(500))
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    request = db.relationship("PeeringRequest", backref="logs")
    arrangement = db.relationship("PeeringArrangement", backref="logs")