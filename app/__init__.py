from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
oauth = OAuth()


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Trust proxy headers (Cloudflare tunnel sets X-Forwarded-Proto etc.)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db.init_app(app)
    csrf.init_app(app)
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

    # Create tables on first request
    with app.app_context():
        from app import models  # noqa: F401

        db.create_all()

    return app


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
