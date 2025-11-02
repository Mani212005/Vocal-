# LiveKit Setup Guide

## Option 1: LiveKit Cloud (Recommended - Free Tier Available)

1. **Sign up for LiveKit Cloud:**
   - Go to https://cloud.livekit.io
   - Create a free account
   - You'll get free credits to get started

2. **Get your credentials:**
   - After signing up, go to your project dashboard
   - Copy your **WebSocket URL** (looks like `wss://xxxxx.livekit.cloud`)
   - Go to **Settings** → **Keys** → Create a new API key
   - Copy the **API Key** and **API Secret**

3. **Add to your `.env` file:**
   ```env
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_api_key_here
   LIVEKIT_API_SECRET=your_api_secret_here
   ```

## Option 2: Run LiveKit Server Locally (Docker)

1. **Install Docker** (if not already installed)

2. **Run LiveKit server:**
   ```bash
   docker run --rm \
     -p 7880:7880 \
     -p 7881:7881 \
     -p 7882:7882/udp \
     -e LIVEKIT_KEYS="devkey: devsecret" \
     livekit/livekit-server \
     --dev
   ```

3. **Add to your `.env` file:**
   ```env
   LIVEKIT_URL=ws://localhost:7880
   LIVEKIT_API_KEY=devkey
   LIVEKIT_API_SECRET=devsecret
   ```

## Quick Start (Testing Without Server)

If you just want to test the agent first without setting up a server, you can use console mode:
```bash
python livekit_basic_agent.py console
```

This doesn't require LiveKit server setup!

