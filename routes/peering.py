from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import (
    db, CDNProvider, Resource, PolicyRule,
    PeeringRequest, PeeringArrangement, NegotiationLog,
)
from datetime import datetime, timezone

peering_bp = Blueprint("peering", __name__, url_prefix="/peering")


def _check_malicious(request_rate, policy):
    """R7 — Detect malicious/abusive request rates."""
    ceiling = policy.max_request_rate if policy else 15000
    if request_rate > ceiling:
        return True, f"Rate exceeded ceiling (>{ceiling}/s) during ingress storm"
    return False, ""


def _check_policy(provider, load_pct, policy):
    """R3 — Mediator checks provider policy for accept/reject gate."""
    if not policy:
        return True, "No policy configured — defaulting to accept"

    # Check if provider has enough CPU (not all delegated)
    from sqlalchemy import func
    total_cpu = (
        db.session.query(func.coalesce(func.sum(Resource.cpu), 0))
        .filter_by(provider_id=provider.id, status="active")
        .scalar()
    )
    if total_cpu < policy.min_cpu_available:
        return False, f"Insufficient CPU: {total_cpu} available < {policy.min_cpu_available} required"

    # Check load threshold
    if load_pct > (100 - policy.max_delegated_pct):
        return False, f"Load {load_pct}% exceeds max delegated threshold ({policy.max_delegated_pct}%)"

    return True, "Policy SLA matched"


@peering_bp.route("/")
def index():
    """List peering requests with status filtering."""
    status_filter = request.args.get("status", "all")

    query = PeeringRequest.query
    if status_filter != "all":
        query = query.filter_by(status=status_filter)

    requests_list = query.order_by(PeeringRequest.created_at.desc()).all()

    # Count by status
    count_all = PeeringRequest.query.count()
    count_pending = PeeringRequest.query.filter_by(status="pending").count()
    count_accepted = PeeringRequest.query.filter_by(status="accepted").count()
    count_rejected = PeeringRequest.query.filter_by(status="rejected").count()

    providers = CDNProvider.query.filter_by(status="active").all()

    return render_template(
        "peering/index.html",
        active_page="peering",
        requests=requests_list,
        providers=providers,
        status_filter=status_filter,
        count_all=count_all,
        count_pending=count_pending,
        count_accepted=count_accepted,
        count_rejected=count_rejected,
    )


@peering_bp.route("/simulate", methods=["POST"])
def simulate():
    """R2/R3/R7 — Trigger simulation, evaluate policy, detect malicious."""
    provider_id = request.form.get("provider_id", type=int)
    target_provider_id = request.form.get("target_provider_id", type=int)
    load_pct = request.form.get("load_pct", type=float)
    request_rate = request.form.get("request_rate", type=int)

    # Input validation
    if not provider_id or not target_provider_id:
        flash("Origin and target providers are required.", "error")
        return redirect(url_for("peering.index"))
    if provider_id == target_provider_id:
        flash("Origin and target providers must be different.", "error")
        return redirect(url_for("peering.index"))
    if load_pct is None or not (0 <= load_pct <= 100):
        flash("Load percentage must be between 0 and 100.", "error")
        return redirect(url_for("peering.index"))
    if request_rate is None or request_rate < 1000:
        flash("Request rate must be at least 1000 req/s.", "error")
        return redirect(url_for("peering.index"))

    provider = CDNProvider.query.get_or_404(provider_id)
    target = CDNProvider.query.get_or_404(target_provider_id)
    policy = PolicyRule.query.filter_by(provider_id=provider_id).first()

    # Create the request record
    pr = PeeringRequest(
        provider_id=provider_id,
        target_provider_id=target_provider_id,
        load_pct=load_pct,
        request_rate=request_rate,
        status="pending",
    )
    db.session.add(pr)
    db.session.flush()  # get pr.id

    # R7 — Malicious check first
    is_malicious, malicious_reason = _check_malicious(request_rate, policy)
    if is_malicious:
        pr.status = "rejected"
        pr.reject_reason = malicious_reason
        log = NegotiationLog(
            request_id=pr.id,
            action="rejected",
            message=f"[MALICIOUS] {malicious_reason} — {provider.name} → {target.name}",
        )
        db.session.add(log)
        db.session.commit()
        flash(f"REQ-{pr.id} Rejected: {malicious_reason}", "error")
        return redirect(url_for("peering.index"))

    # R3 — Policy gate
    accepted, policy_msg = _check_policy(provider, load_pct, policy)
    if accepted:
        pr.status = "accepted"
        # R4 — Create peering arrangement
        arrangement = PeeringArrangement(
            primary_provider_id=provider_id,
            peer_provider_id=target_provider_id,
            request_id=pr.id,
            status="active",
        )
        db.session.add(arrangement)
        db.session.flush()

        log = NegotiationLog(
            request_id=pr.id,
            arrangement_id=arrangement.id,
            action="accepted",
            message=f"[ACCEPTED] {policy_msg} — {provider.name} → {target.name} (Load: {load_pct}%, Rate: {request_rate}/s)",
        )
        db.session.add(log)
        db.session.commit()
        flash(f"REQ-{pr.id} Accepted: {policy_msg}. Arrangement ARR-{arrangement.id} created.", "success")
    else:
        pr.status = "rejected"
        pr.reject_reason = policy_msg
        log = NegotiationLog(
            request_id=pr.id,
            action="rejected",
            message=f"[REJECTED] {policy_msg} — {provider.name} → {target.name}",
        )
        db.session.add(log)
        db.session.commit()
        flash(f"REQ-{pr.id} Rejected: {policy_msg}", "error")

    return redirect(url_for("peering.index"))


@peering_bp.route("/<int:id>/evaluate", methods=["POST"])
def evaluate(id):
    """Manually evaluate a pending request."""
    pr = PeeringRequest.query.get_or_404(id)
    if pr.status != "pending":
        flash("Only pending requests can be evaluated.", "error")
        return redirect(url_for("peering.index"))

    provider = CDNProvider.query.get(pr.provider_id)
    target = CDNProvider.query.get(pr.target_provider_id) if pr.target_provider_id else None
    policy = PolicyRule.query.filter_by(provider_id=pr.provider_id).first()

    # Check malicious
    is_malicious, malicious_reason = _check_malicious(pr.request_rate, policy)
    if is_malicious:
        pr.status = "rejected"
        pr.reject_reason = malicious_reason
        db.session.add(NegotiationLog(
            request_id=pr.id, action="rejected",
            message=f"[MALICIOUS] {malicious_reason}",
        ))
        db.session.commit()
        flash(f"REQ-{pr.id} Rejected: {malicious_reason}", "error")
        return redirect(url_for("peering.index"))

    accepted, msg = _check_policy(provider, pr.load_pct, policy)
    if accepted:
        pr.status = "accepted"
        arrangement = PeeringArrangement(
            primary_provider_id=pr.provider_id,
            peer_provider_id=pr.target_provider_id or pr.provider_id,
            request_id=pr.id,
            status="active",
        )
        db.session.add(arrangement)
        db.session.flush()
        db.session.add(NegotiationLog(
            request_id=pr.id, arrangement_id=arrangement.id,
            action="accepted", message=f"[ACCEPTED] {msg}",
        ))
        db.session.commit()
        flash(f"REQ-{pr.id} Accepted. Arrangement ARR-{arrangement.id} created.", "success")
    else:
        pr.status = "rejected"
        pr.reject_reason = msg
        db.session.add(NegotiationLog(
            request_id=pr.id, action="rejected",
            message=f"[REJECTED] {msg}",
        ))
        db.session.commit()
        flash(f"REQ-{pr.id} Rejected: {msg}", "error")

    return redirect(url_for("peering.index"))
