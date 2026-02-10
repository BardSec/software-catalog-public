import os
from datetime import datetime, timezone

from flask import Blueprint, redirect, url_for, flash, render_template, current_app, session
from flask_login import login_user, logout_user, current_user

from app import db, oauth
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("catalog.index"))

    ms_enabled = bool(current_app.config["MICROSOFT_CLIENT_ID"])
    google_enabled = bool(current_app.config["GOOGLE_CLIENT_ID"])

    # Check for a custom logo in static/img/
    login_logo = None
    img_dir = os.path.join(current_app.static_folder, "img")
    for ext in ("png", "svg", "jpg", "webp"):
        if os.path.isfile(os.path.join(img_dir, f"logo.{ext}")):
            login_logo = url_for("static", filename=f"img/logo.{ext}")
            break

    return render_template(
        "auth/login.html",
        ms_enabled=ms_enabled,
        google_enabled=google_enabled,
        login_logo=login_logo,
    )


@auth_bp.route("/login/microsoft")
def login_microsoft():
    redirect_uri = url_for("auth.callback_microsoft", _external=True)
    return oauth.microsoft.authorize_redirect(redirect_uri)


@auth_bp.route("/callback/microsoft")
def callback_microsoft():
    try:
        token = oauth.microsoft.authorize_access_token()
        userinfo = token.get("userinfo")
        if not userinfo:
            userinfo = oauth.microsoft.get(
                "https://graph.microsoft.com/oidc/userinfo",
                token=token,
            ).json()
    except Exception:
        flash("Microsoft sign-in failed. Please try again.", "error")
        return redirect(url_for("auth.login"))

    email = userinfo.get("email", "").lower().strip()
    name = userinfo.get("name", "")
    return _handle_login(email, name, "microsoft")


@auth_bp.route("/login/google")
def login_google():
    redirect_uri = url_for("auth.callback_google", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/callback/google")
def callback_google():
    try:
        token = oauth.google.authorize_access_token()
        userinfo = token.get("userinfo")
        if not userinfo:
            userinfo = oauth.google.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                token=token,
            ).json()
    except Exception:
        flash("Google sign-in failed. Please try again.", "error")
        return redirect(url_for("auth.login"))

    email = userinfo.get("email", "").lower().strip()
    name = userinfo.get("name", "")
    return _handle_login(email, name, "google")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    session.clear()
    flash("You have been signed out.", "info")
    resp = redirect(url_for("auth.login"))
    resp.delete_cookie("remember_token")
    return resp


def _handle_login(email, name, provider):
    """Common login handler for both providers."""
    if not email:
        flash("Could not retrieve your email address.", "error")
        return redirect(url_for("auth.login"))

    # Check domain restriction
    allowed = current_app.config["ALLOWED_DOMAINS"]
    if allowed:
        domain = email.split("@")[-1]
        if domain not in allowed:
            flash("Your email domain is not authorized to access this application.", "error")
            return redirect(url_for("auth.login"))

    # Find or create user
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(email=email, name=name, provider=provider)
        db.session.add(user)

    user.name = name
    user.last_login = datetime.now(timezone.utc)

    # Check admin status
    admin_emails = current_app.config["ADMIN_EMAILS"]
    user.is_admin = email in admin_emails

    db.session.commit()
    login_user(user, remember=True)

    return redirect(url_for("catalog.index"))
