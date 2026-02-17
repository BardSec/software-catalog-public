import os

_WEAK_KEYS = {"dev-secret-change-me", "change-me", "secret", ""}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{_DEFAULT_DB_PATH}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cookie security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_DURATION = 604800  # 7 days

    # Enable Secure flag when a real secret is configured (i.e. production)
    _secure = SECRET_KEY not in _WEAK_KEYS
    SESSION_COOKIE_SECURE = _secure
    REMEMBER_COOKIE_SECURE = _secure

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
