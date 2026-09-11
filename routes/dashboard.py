from flask import Blueprint, render_template
from models import db, CDNProvider, Resource, PeeringRequest, PeeringArrangement, NegotiationLog

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    """Dashboard — R8 Performance/QoS overview."""
    active_providers = CDNProvider.query.filter_by(status="active").count()
    pending_requests = PeeringRequest.query.filter_by(status="pending").count()
    active_treaties = PeeringArrangement.query.filter_by(status="active").count()
    total_nodes = Resource.query.count()
    active_nodes = Resource.query.filter_by(status="active").count()
    alert_nodes = Resource.query.filter(Resource.status != "active").count()

    # Aggregated stats
    from sqlalchemy import func

    total_cpu = db.session.query(func.coalesce(func.sum(Resource.cpu), 0)).scalar()
    total_storage = db.session.query(func.coalesce(func.sum(Resource.storage_gb), 0)).scalar()
    total_upload = db.session.query(func.coalesce(func.sum(Resource.upload_rate), 0)).scalar()
    total_download = db.session.query(func.coalesce(func.sum(Resource.download_rate), 0)).scalar()

    # Recent negotiation events
    recent_events = (
        NegotiationLog.query
        .order_by(NegotiationLog.created_at.desc())
        .limit(5)
        .all()
    )

    # Providers for load test selector
    providers = CDNProvider.query.filter_by(status="active").all()

    return render_template(
        "dashboard/index.html",
        active_page="dashboard",
        active_providers=active_providers,
        pending_requests=pending_requests,
        active_treaties=active_treaties,
        total_nodes=total_nodes,
        active_nodes=active_nodes,
        alert_nodes=alert_nodes,
        total_cpu=total_cpu,
        total_storage=total_storage,
        total_upload=total_upload,
        total_download=total_download,
        recent_events=recent_events,
        providers=providers,
    )
