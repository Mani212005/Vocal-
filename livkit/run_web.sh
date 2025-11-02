#!/bin/bash
# Script to run the web server and agent together

cd "$(dirname "$0")"
source ../myenv/bin/activate

echo "Starting LiveKit Voice Agent Web Interface..."
echo ""
echo "To use this:"
echo "1. Make sure your .env file has LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET"
echo "2. In a separate terminal, run: python livekit_basic_agent.py dev"
echo "3. Then open http://localhost:8000 in your browser"
echo ""

python web_server.py

