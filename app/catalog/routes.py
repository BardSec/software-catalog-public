from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

from app import db
from app.models import Software, Category

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.route("/")
@login_required
def index():
    """Main catalog page with search and filter."""
    # Group categories by type for the filter sidebar
    categories = Category.query.order_by(Category.name).all()
    grouped = {}
    for cat in categories:
        grouped.setdefault(cat.category_type, []).append(cat)

    # Define display order and labels for category groups
    group_meta = {
        "dpa_status": "DPA Status",
        "cost": "Cost / School",
        "roster": "Rostering",
        "access": "Access",
        "status": "Status",
        "other": "Subject & Function",
    }

    return render_template(
        "catalog/index.html",
        grouped_categories=grouped,
        group_meta=group_meta,
    )


@catalog_bp.route("/api/software")
@login_required
def api_software():
    """JSON API for software entries, supports search and category filters."""
    search = request.args.get("q", "").strip()
    category_ids = request.args.getlist("cat", type=int)

    query = Software.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Software.name.ilike(like),
                Software.tagline.ilike(like),
            )
        )

    if category_ids:
        valid_ids = {
            c.id for c in Category.query.filter(Category.id.in_(category_ids)).all()
        }
        category_ids = [cid for cid in category_ids if cid in valid_ids]
        for cat_id in category_ids:
            query = query.filter(
                Software.categories.any(Category.id == cat_id)
            )

    # Featured first, then alphabetical
    software = query.order_by(
        Software.featured.desc(), Software.name
    ).all()

    results = []
    for s in software:
        cats = []
        for c in s.categories:
            cats.append({
                "id": c.id,
                "name": c.name,
                "type": c.category_type,
            })
        results.append({
            "id": s.id,
            "name": s.name,
            "url": s.url,
            "tagline": s.tagline,
            "logo": s.logo,
            "featured": s.featured,
            "categories": cats,
        })

    return jsonify(results)


@catalog_bp.route("/software/<int:software_id>")
@login_required
def detail(software_id):
    """Detail view for a single software entry."""
    software = db.get_or_404(Software, software_id)
    return render_template("catalog/detail.html", software=software)
