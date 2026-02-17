import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import _WEAK_KEYS

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
oauth = OAuth()
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Reject known-weak secret keys
    if app.config["SECRET_KEY"] in _WEAK_KEYS:
        raise RuntimeError(
            "SECRET_KEY is not set or uses a known default. "
            "Generate a strong key: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    if len(app.config["SECRET_KEY"]) < 16:
        raise RuntimeError("SECRET_KEY must be at least 16 characters.")

    # Trust proxy headers (Cloudflare tunnel sets X-Forwarded-Proto etc.)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Configure OAuth providers
    _register_oauth_providers(app)

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.catalog.routes import catalog_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' https: data:"
        )
        return response

    # Logging
    _configure_logging(app)

    # Create tables on first request
    with app.app_context():
        from app import models  # noqa: F401

        db.create_all()

    return app


def _configure_logging(app):
    log_dir = os.path.join(app.root_path, "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "catalog.log"),
        maxBytes=10_240_000,
        backupCount=10,
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [%(pathname)s:%(lineno)d]"
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Application startup")


def _register_oauth_providers(app):
    oauth.init_app(app)

    if app.config["MICROSOFT_CLIENT_ID"]:
        tenant = app.config["MICROSOFT_TENANT_ID"] or "common"
        oauth.register(
            name="microsoft",
            client_id=app.config["MICROSOFT_CLIENT_ID"],
            client_secret=app.config["MICROSOFT_CLIENT_SECRET"],
            server_metadata_url=(
                f"https://login.microsoftonline.com/{tenant}"
                "/v2.0/.well-known/openid-configuration"
            ),
            client_kwargs={"scope": "openid email profile"},
        )

    if app.config["GOOGLE_CLIENT_ID"]:
        oauth.register(
            name="google",
            client_id=app.config["GOOGLE_CLIENT_ID"],
            client_secret=app.config["GOOGLE_CLIENT_SECRET"],
            server_metadata_url=(
                "https://accounts.google.com/.well-known/openid-configuration"
            ),
            client_kwargs={"scope": "openid email profile"},
        )
