#!/bin/bash
# Script to start a local LiveKit development server

echo "Starting local LiveKit server..."
echo "Note: This requires Docker. If you don't have Docker, use LiveKit Cloud instead."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running or not installed."
    echo "Please:"
    echo "1. Install Docker Desktop from https://www.docker.com/products/docker-desktop"
    echo "2. Start Docker Desktop"
    echo "3. Or use LiveKit Cloud (free tier) from https://cloud.livekit.io"
    exit 1
fi

echo "Starting LiveKit server on localhost:7880..."
echo "Press Ctrl+C to stop"
echo ""

docker run --rm \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 7882:7882/udp \
  -e LIVEKIT_KEYS="devkey: devsecret" \
  livekit/livekit-server \
  --dev

