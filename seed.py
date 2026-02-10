"""Import software_directory.json into the SQLite database."""

import json
import sys

from app import create_app, db
from app.models import Category, Software


def seed():
    app = create_app()

    with open("software_directory.json", "r") as f:
        entries = json.load(f)

    with app.app_context():
        # Clear existing data for a clean seed
        db.session.execute(db.text("DELETE FROM software_categories"))
        Software.query.delete()
        Category.query.delete()
        db.session.commit()

        # Build category cache
        category_cache = {}

        for entry in entries:
            software = Software(
                name=entry.get("name", ""),
                url=entry.get("url", ""),
                tagline=entry.get("tagline", ""),
                content=entry.get("content", ""),
                logo=entry.get("logo", ""),
                featured=entry.get("featured", False),
            )
            db.session.add(software)

            for cat_name in entry.get("categories", []):
                cat_name = cat_name.strip()
                if not cat_name:
                    continue

                if cat_name not in category_cache:
                    category = Category(
                        name=cat_name,
                        category_type=Category.classify(cat_name),
                    )
                    db.session.add(category)
                    db.session.flush()
                    category_cache[cat_name] = category
                else:
                    category = category_cache[cat_name]

                software.categories.append(category)

        db.session.commit()

        software_count = Software.query.count()
        category_count = Category.query.count()
        print(f"Seeded {software_count} software entries with {category_count} categories.")


if __name__ == "__main__":
    seed()
