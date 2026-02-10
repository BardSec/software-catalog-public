import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///catalog.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Microsoft OIDC
    MICROSOFT_CLIENT_ID = os.environ.get("MICROSOFT_CLIENT_ID", "")
    MICROSOFT_CLIENT_SECRET = os.environ.get("MICROSOFT_CLIENT_SECRET", "")
    MICROSOFT_TENANT_ID = os.environ.get("MICROSOFT_TENANT_ID", "")

    # Google OIDC
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

    # Access control
    ADMIN_EMAILS = [
        e.strip().lower()
        for e in os.environ.get("ADMIN_EMAILS", "").split(",")
        if e.strip()
    ]
    ALLOWED_DOMAINS = [
        d.strip().lower()
        for d in os.environ.get("ALLOWED_DOMAINS", "").split(",")
        if d.strip()
    ]
