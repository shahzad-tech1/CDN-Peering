from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, CDNProvider, Resource, PolicyRule

providers_bp = Blueprint("providers", __name__, url_prefix="/providers")


@providers_bp.route("/")
def index():
    """R3 — List providers with aggregated resource stats and policies."""
    providers = CDNProvider.query.order_by(CDNProvider.name).all()

    from sqlalchemy import func

    provider_stats = []
    for p in providers:
        stats = (
            db.session.query(
                func.count(Resource.id).label("count"),
                func.coalesce(func.sum(Resource.cpu), 0).label("cpu"),
                func.coalesce(func.sum(Resource.storage_gb), 0).label("storage"),
                func.coalesce(func.sum(Resource.upload_rate), 0).label("upload"),
                func.coalesce(func.sum(Resource.download_rate), 0).label("download"),
            )
            .filter(Resource.provider_id == p.id, Resource.status == "active")
            .first()
        )
        policy = PolicyRule.query.filter_by(provider_id=p.id).first()
        provider_stats.append({
            "provider": p,
            "resource_count": stats.count,
            "total_cpu": stats.cpu,
            "total_storage": stats.storage,
            "total_upload": stats.upload,
            "total_download": stats.download,
            "policy": policy,
        })

    total_active = CDNProvider.query.filter_by(status="active").count()
    total_policies = PolicyRule.query.count()
    total_egress = db.session.query(
        func.coalesce(func.sum(Resource.download_rate), 0)
    ).scalar()

    return render_template(
        "providers/index.html",
        active_page="providers",
        provider_stats=provider_stats,
        total_active=total_active,
        total_policies=total_policies,
        total_egress=total_egress,
        providers=providers,
    )


@providers_bp.route("/create", methods=["POST"])
def create():
    """Register a new CDN provider."""
    name = request.form.get("name", "").strip()
    asn = request.form.get("asn", "").strip()

    if not name:
        flash("Provider name is required.", "error")
        return redirect(url_for("providers.index"))
    if CDNProvider.query.filter_by(name=name).first():
        flash(f"Provider '{name}' already exists.", "error")
        return redirect(url_for("providers.index"))

    provider = CDNProvider(name=name, asn=asn)
    db.session.add(provider)
    db.session.commit()
    flash(f"Provider '{name}' registered.", "success")
    return redirect(url_for("providers.index"))


@providers_bp.route("/<int:id>/policy", methods=["POST"])
def update_policy(id):
    """R3 — Create or update policy rules for a provider."""
    provider = CDNProvider.query.get_or_404(id)
    min_cpu = request.form.get("min_cpu_available", type=float)
    max_pct = request.form.get("max_delegated_pct", type=float)
    max_rate = request.form.get("max_request_rate", 15000, type=int)

    if min_cpu is None or min_cpu < 0:
        flash("Min CPU must be ≥ 0.", "error")
        return redirect(url_for("providers.index"))
    if max_pct is None or not (0 <= max_pct <= 100):
        flash("Max delegated % must be between 0 and 100.", "error")
        return redirect(url_for("providers.index"))

    policy = PolicyRule.query.filter_by(provider_id=id).first()
    if policy:
        policy.min_cpu_available = min_cpu
        policy.max_delegated_pct = max_pct
        policy.max_request_rate = max_rate
    else:
        policy = PolicyRule(
            provider_id=id,
            min_cpu_available=min_cpu,
            max_delegated_pct=max_pct,
            max_request_rate=max_rate,
        )
        db.session.add(policy)

    db.session.commit()
    flash(f"Policy for '{provider.name}' updated.", "success")
    return redirect(url_for("providers.index"))
