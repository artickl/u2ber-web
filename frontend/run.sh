#!/bin/bash
cd "$(dirname "$0")"

npm install

# Load environment from .env.local if it exists
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '#' | xargs)
fi

# Run Vite dev server
npm run dev
