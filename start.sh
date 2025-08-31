#!/bin/bash
set -e

echo "🚀 Starting LogicAndStories application..."

# Ensure environment is properly configured
export PYTHONPATH="${PYTHONPATH:-.}"
export FLASK_APP=app.py
export FLASK_ENV=production

# Start the application with gunicorn
exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 --timeout 120 --access-logfile - --error-logfile - app:app