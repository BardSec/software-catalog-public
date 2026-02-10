from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.models import Software, Category

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@admin_required
def dashboard():
    software = Software.query.order_by(Software.name).all()
    return render_template("admin/dashboard.html", software=software)


@admin_bp.route("/add", methods=["GET", "POST"])
@admin_required
def add():
    categories = Category.query.order_by(Category.category_type, Category.name).all()

    if request.method == "POST":
        software = Software(
            name=request.form.get("name", "").strip(),
            url=request.form.get("url", "").strip(),
            tagline=request.form.get("tagline", "").strip(),
            content=request.form.get("content", "").strip(),
            logo=request.form.get("logo", "").strip(),
            featured="featured" in request.form,
        )

        if not software.name:
            flash("Name is required.", "error")
            return render_template("admin/edit.html", software=software, categories=categories, is_new=True)

        # Handle categories
        selected_ids = request.form.getlist("categories", type=int)
        software.categories = Category.query.filter(Category.id.in_(selected_ids)).all()

        # Handle new categories
        new_cats = request.form.get("new_categories", "").strip()
        if new_cats:
            for cat_name in new_cats.split(","):
                cat_name = cat_name.strip()
                if not cat_name:
                    continue
                existing = Category.query.filter_by(name=cat_name).first()
                if existing:
                    if existing not in software.categories:
                        software.categories.append(existing)
                else:
                    cat = Category(name=cat_name, category_type=Category.classify(cat_name))
                    db.session.add(cat)
                    software.categories.append(cat)

        db.session.add(software)
        db.session.commit()
        flash(f'"{software.name}" has been added.', "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/edit.html", software=None, categories=categories, is_new=True)


@admin_bp.route("/edit/<int:software_id>", methods=["GET", "POST"])
@admin_required
def edit(software_id):
    software = db.get_or_404(Software, software_id)
    categories = Category.query.order_by(Category.category_type, Category.name).all()

    if request.method == "POST":
        software.name = request.form.get("name", "").strip()
        software.url = request.form.get("url", "").strip()
        software.tagline = request.form.get("tagline", "").strip()
        software.content = request.form.get("content", "").strip()
        software.logo = request.form.get("logo", "").strip()
        software.featured = "featured" in request.form

        if not software.name:
            flash("Name is required.", "error")
            return render_template("admin/edit.html", software=software, categories=categories, is_new=False)

        selected_ids = request.form.getlist("categories", type=int)
        software.categories = Category.query.filter(Category.id.in_(selected_ids)).all()

        # Handle new categories
        new_cats = request.form.get("new_categories", "").strip()
        if new_cats:
            for cat_name in new_cats.split(","):
                cat_name = cat_name.strip()
                if not cat_name:
                    continue
                existing = Category.query.filter_by(name=cat_name).first()
                if existing:
                    if existing not in software.categories:
                        software.categories.append(existing)
                else:
                    cat = Category(name=cat_name, category_type=Category.classify(cat_name))
                    db.session.add(cat)
                    software.categories.append(cat)

        db.session.commit()
        flash(f'"{software.name}" has been updated.', "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/edit.html", software=software, categories=categories, is_new=False)


@admin_bp.route("/delete/<int:software_id>", methods=["POST"])
@admin_required
def delete(software_id):
    software = db.get_or_404(Software, software_id)
    name = software.name
    db.session.delete(software)
    db.session.commit()
    flash(f'"{name}" has been deleted.', "success")
    return redirect(url_for("admin.dashboard"))
