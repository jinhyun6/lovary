#!/bin/bash
set -e

# Wait for postgres
python wait-for-postgres.py

# Initialize database
python init_db.py

# Get port from environment variable (Cloud Run provides PORT)
PORT=${PORT:-8000}

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload