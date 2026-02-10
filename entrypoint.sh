#!/bin/sh
set -e

# Run seed if database doesn't exist yet
if [ ! -f /app/instance/catalog.db ]; then
    echo "Initializing database and seeding data..."
    mkdir -p /app/instance
    python seed.py
fi

exec "$@"
