from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, CDNProvider, PeeringArrangement, NegotiationLog

arrangements_bp = Blueprint("arrangements", __name__, url_prefix="/arrangements")


@arrangements_bp.route("/")
def index():
    """R4/R5/R6 — List all peering arrangements with accounting data."""
    arrangements = (
        PeeringArrangement.query
        .order_by(PeeringArrangement.created_at.desc())
        .all()
    )

    active_count = PeeringArrangement.query.filter_by(status="active").count()
    total_count = PeeringArrangement.query.count()
    from sqlalchemy import func
    total_units = db.session.query(
        func.coalesce(func.sum(PeeringArrangement.accounting_units), 0)
    ).scalar()

    # Recent audit log entries
    logs = (
        NegotiationLog.query
        .filter(NegotiationLog.arrangement_id.isnot(None))
        .order_by(NegotiationLog.created_at.desc())
        .limit(6)
        .all()
    )

    return render_template(
        "arrangements/index.html",
        active_page="arrangements",
        arrangements=arrangements,
        active_count=active_count,
        total_count=total_count,
        total_units=total_units,
        logs=logs,
    )


@arrangements_bp.route("/<int:id>/accounting", methods=["POST"])
def add_accounting(id):
    """R5 — Record accounting units for billing."""
    arrangement = PeeringArrangement.query.get_or_404(id)
    if arrangement.status != "active":
        flash("Can only add accounting to active arrangements.", "error")
        return redirect(url_for("arrangements.index"))

    units = request.form.get("units", type=float)
    if units is None or units <= 0:
        flash("Accounting units must be a positive number.", "error")
        return redirect(url_for("arrangements.index"))

    arrangement.accounting_units += units
    log = NegotiationLog(
        arrangement_id=arrangement.id,
        action="accounting",
        message=f"Added {units:.0f} TU (total: {arrangement.accounting_units:.0f})",
    )
    db.session.add(log)
    db.session.commit()
    flash(f"Added {units:.0f} TU to ARR-{arrangement.id}.", "success")
    return redirect(url_for("arrangements.index"))


@arrangements_bp.route("/<int:id>/disband", methods=["POST"])
def disband(id):
    """R6 — Disband a peering arrangement."""
    arrangement = PeeringArrangement.query.get_or_404(id)
    if arrangement.status == "disbanded":
        flash("Arrangement is already disbanded.", "error")
        return redirect(url_for("arrangements.index"))

    arrangement.status = "disbanded"
    log = NegotiationLog(
        arrangement_id=arrangement.id,
        action="disbanded",
        message=f"Arrangement ARR-{arrangement.id} disbanded ({arrangement.primary_provider.name} <-> {arrangement.peer_provider.name})",
    )
    db.session.add(log)
    db.session.commit()
    flash(f"ARR-{arrangement.id} disbanded.", "success")
    return redirect(url_for("arrangements.index"))


@arrangements_bp.route("/<int:id>/rearrange", methods=["POST"])
def rearrange(id):
    """R6 — Re-arrange: shift to a new peer provider."""
    arrangement = PeeringArrangement.query.get_or_404(id)
    new_peer_id = request.form.get("new_peer_id", type=int)

    if not new_peer_id:
        flash("New peer provider is required.", "error")
        return redirect(url_for("arrangements.index"))
    if new_peer_id == arrangement.primary_provider_id:
        flash("New peer must be different from primary provider.", "error")
        return redirect(url_for("arrangements.index"))

    new_peer = CDNProvider.query.get_or_404(new_peer_id)
    old_peer_name = arrangement.peer_provider.name
    arrangement.peer_provider_id = new_peer_id
    arrangement.status = "rearranged"
    log = NegotiationLog(
        arrangement_id=arrangement.id,
        action="rearranged",
        message=f"Rearranged from {old_peer_name} → {new_peer.name}",
    )
    db.session.add(log)
    db.session.commit()
    flash(f"ARR-{arrangement.id} rearranged to peer with {new_peer.name}.", "success")
    return redirect(url_for("arrangements.index"))


@arrangements_bp.route("/<int:id>/evaluate", methods=["POST"])
def evaluate(id):
    """R6 — Check termination conditions."""
    arrangement = PeeringArrangement.query.get_or_404(id)
    messages = []

    # Check accounting unit threshold
    if arrangement.accounting_units >= arrangement.max_accounting_units:
        messages.append(f"Accounting threshold exceeded ({arrangement.accounting_units:.0f}/{arrangement.max_accounting_units:.0f} TU)")

    # Check utilization ratio
    pct = (arrangement.accounting_units / arrangement.max_accounting_units * 100) if arrangement.max_accounting_units > 0 else 0
    if pct < 15:
        messages.append(f"Under-utilization alert ({pct:.1f}% < 15% threshold)")

    if messages:
        log = NegotiationLog(
            arrangement_id=arrangement.id,
            action="evaluation",
            message="Termination conditions flagged: " + "; ".join(messages),
        )
        db.session.add(log)
        db.session.commit()
        flash(f"ARR-{arrangement.id} flagged: " + "; ".join(messages), "error")
    else:
        log = NegotiationLog(
            arrangement_id=arrangement.id,
            action="evaluation",
            message="All termination conditions passed — arrangement healthy",
        )
        db.session.add(log)
        db.session.commit()
        flash(f"ARR-{arrangement.id} evaluation passed — all conditions healthy.", "success")

    return redirect(url_for("arrangements.index"))
