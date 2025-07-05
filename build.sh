#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Only run migrations if database is configured
if [ -n "$DB_NAME" ]; then
    echo "Database configured, running migrations..."
    python manage.py migrate
else
    echo "No database configured, skipping migrations..."
fi 