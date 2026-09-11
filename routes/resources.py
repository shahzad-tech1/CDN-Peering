from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, CDNProvider, Resource

resources_bp = Blueprint("resources", __name__, url_prefix="/resources")

# ---------- helpers ----------

def _next_resource_id():
    """Generate the next RES-XXXX identifier."""
    last = (
        Resource.query
        .order_by(Resource.id.desc())
        .first()
    )
    if last and last.resource_id.startswith("RES-"):
        try:
            num = int(last.resource_id.split("-")[1]) + 1
        except (ValueError, IndexError):
            num = 1001
    else:
        num = 1001
    return f"RES-{num:04d}"


def _validate_resource_form(form):
    """Server-side validation — returns (data_dict | None, error_msg | None)."""
    errors = []
    provider_id = form.get("provider_id", type=int)
    cpu = form.get("cpu", type=float)
    storage = form.get("storage_gb", type=float)
    upload = form.get("upload_rate", type=float)
    download = form.get("download_rate", type=float)

    if not provider_id:
        errors.append("Provider is required.")
    elif not CDNProvider.query.get(provider_id):
        errors.append("Selected provider does not exist.")
    if cpu is None or cpu <= 0:
        errors.append("CPU cores must be greater than 0.")
    if storage is None or storage <= 0:
        errors.append("Storage must be greater than 0.")
    if upload is None or upload <= 0:
        errors.append("Upload rate must be greater than 0.")
    if download is None or download <= 0:
        errors.append("Download rate must be greater than 0.")

    if errors:
        return None, " ".join(errors)

    return {
        "provider_id": provider_id,
        "cpu": cpu,
        "storage_gb": storage,
        "upload_rate": upload,
        "download_rate": download,
    }, None


# ---------- routes ----------

@resources_bp.route("/")
def index():
    """R1 — List all resources with optional status filter and pagination."""
    status_filter = request.args.get("status", "all")
    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = Resource.query
    if status_filter != "all":
        query = query.filter_by(status=status_filter)

    pagination = query.order_by(Resource.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    resources = pagination.items

    providers = CDNProvider.query.order_by(CDNProvider.name).all()

    # Summary stats
    total_active = Resource.query.filter_by(status="active").count()
    total_alert = Resource.query.filter(Resource.status != "active").count()
    from sqlalchemy import func
    total_download = db.session.query(func.coalesce(func.sum(Resource.download_rate), 0)).scalar()

    return render_template(
        "resources/index.html",
        active_page="resources",
        resources=resources,
        pagination=pagination,
        providers=providers,
        status_filter=status_filter,
        total_active=total_active,
        total_alert=total_alert,
        total_download=total_download,
        next_resource_id=_next_resource_id(),
    )


@resources_bp.route("/create", methods=["POST"])
def create():
    """R1 — Register a new resource in the Service Registry."""
    data, error = _validate_resource_form(request.form)
    if error:
        flash(error, "error")
        return redirect(url_for("resources.index"))

    resource = Resource(
        resource_id=_next_resource_id(),
        **data,
    )
    db.session.add(resource)
    db.session.commit()
    flash(f"Resource {resource.resource_id} registered successfully.", "success")
    return redirect(url_for("resources.index"))


@resources_bp.route("/<int:id>/edit", methods=["POST"])
def edit(id):
    """R1 — Update an existing resource record."""
    resource = Resource.query.get_or_404(id)
    data, error = _validate_resource_form(request.form)
    if error:
        flash(error, "error")
        return redirect(url_for("resources.index"))

    resource.provider_id = data["provider_id"]
    resource.cpu = data["cpu"]
    resource.storage_gb = data["storage_gb"]
    resource.upload_rate = data["upload_rate"]
    resource.download_rate = data["download_rate"]
    db.session.commit()
    flash(f"Resource {resource.resource_id} updated successfully.", "success")
    return redirect(url_for("resources.index"))


@resources_bp.route("/<int:id>/delete", methods=["POST"])
def delete(id):
    """R1 — Remove resource on failure; the record is removed."""
    resource = Resource.query.get_or_404(id)
    rid = resource.resource_id
    db.session.delete(resource)
    db.session.commit()
    flash(f"Resource {rid} removed from registry.", "success")
    return redirect(url_for("resources.index"))
