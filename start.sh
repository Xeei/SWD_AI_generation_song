#!/bin/bash

# Get the directory where start.sh is located
BASE_DIR=$(pwd)

# Function to kill background processes on exit
trap "exit" INT TERM
trap "kill 0" EXIT

echo "🚀 Launching development environment..."

# 1. Start Frontend
echo "📦 Starting Frontend..."
(cd "$BASE_DIR/frontend" && npm run dev) &

# Give the frontend a second to initialize logs
sleep 1

# 2. Start Backend
echo "🐍 Starting Backend..."
if [ -f "$BASE_DIR/.venv/bin/activate" ]; then
    source "$BASE_DIR/.venv/bin/activate"
    # Removed the quotes from around runserver
    python "$BASE_DIR/manage.py" runserver
else
    echo "❌ Error: .venv not found in $BASE_DIR"
    exit 1
fi