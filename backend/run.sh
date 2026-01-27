#!/bin/bash
cd "$(dirname "$0")"

# check if venv exists, if not create it and install dependencies
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Load environment from .env.local if it exists
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '#' | xargs)
fi

# Run with configured settings
python3 -m uvicorn app.main:app --reload --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000}
