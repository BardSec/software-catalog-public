from datetime import datetime, timezone

from flask_login import UserMixin

from app import db, login_manager

# Many-to-many association table
software_categories = db.Table(
    "software_categories",
    db.Column(
        "software_id", db.Integer, db.ForeignKey("software.id"), primary_key=True
    ),
    db.Column(
        "category_id", db.Integer, db.ForeignKey("category.id"), primary_key=True
    ),
)


class Software(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    url = db.Column(db.String(500), default="")
    tagline = db.Column(db.String(500), default="")
    content = db.Column(db.Text, default="")
    logo = db.Column(db.String(500), default="")
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    categories = db.relationship(
        "Category", secondary=software_categories, back_populates="software_items"
    )

    def __repr__(self):
        return f"<Software {self.name}>"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    category_type = db.Column(db.String(50), nullable=False, default="other")
    # Types: dpa_status, cost, roster, access, status, subject, other

    software_items = db.relationship(
        "Software", secondary=software_categories, back_populates="categories"
    )

    def __repr__(self):
        return f"<Category {self.name}>"

    @staticmethod
    def classify(name):
        """Auto-classify a category name into a type based on patterns."""
        n = name.strip()
        if n.startswith(("0-", "1-", "2-", "3-", "4-")) or "DPA" in n.upper():
            return "dpa_status"
        if n.startswith("$"):
            return "cost"
        if n.startswith("Roster:"):
            return "roster"
        if n.startswith("#"):
            return "status"
        access_keywords = [
            "staff only",
            "staff use only",
            "account-required",
            "no account required",
            "parental-consent",
            "paid license",
            "external accounts",
        ]
        if n.lower() in access_keywords or any(
            kw in n.lower() for kw in access_keywords
        ):
            return "access"
        return "other"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    name = db.Column(db.String(200), default="")
    provider = db.Column(db.String(50), default="")  # "microsoft" or "google"
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
