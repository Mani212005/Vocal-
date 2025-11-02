# LiveKit Voice Agent

A voice assistant using LiveKit, OpenRouter (Phi-4 Multimodal), Sarvam AI, and Silero VAD.

## Setup

1. **Install dependencies:**
   ```bash
   source ../myenv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** in the `livkit` directory with:
   ```env
   # OpenRouter API (required)
   OPENROUTER_API_KEY=your_openrouter_api_key
   OPENROUTER_SITE_URL=https://your-site.com  # Optional
   OPENROUTER_APP_NAME=LiveKit Voice Agent    # Optional
   
   # Sarvam AI API (required)
   SARVAM_API_KEY=your_sarvam_api_key
   
   # LiveKit Server (required for dev/start modes)
   LIVEKIT_URL=wss://your-livekit-server.com
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   ```

## Running the Agent

### Option 1: Console Mode (Easiest - No LiveKit Server Needed)
Test the agent in a console:
```bash
python livekit_basic_agent.py console
```

### Option 2: Development Mode
Run with LiveKit server:
```bash
python livekit_basic_agent.py dev --url wss://your-livekit-server.com --api-key YOUR_KEY --api-secret YOUR_SECRET
```

### Option 3: Production Mode
```bash
python livekit_basic_agent.py start --url wss://your-livekit-server.com --api-key YOUR_KEY --api-secret YOUR_SECRET
```

## Models Used

- **LLM**: Microsoft Phi-4 Multimodal Instruct (via OpenRouter)
- **STT**: Sarvam AI Saarika v2.5 (Hindi)
- **TTS**: Sarvam AI Anushka (Hindi)
- **VAD**: Silero VAD (automatically downloaded)

## Web Interface

A simple web interface with a mic button is available!

### Running the Web Interface

1. **Terminal 1 - Start the LiveKit Agent:**
   ```bash
   python livekit_basic_agent.py dev --url wss://your-livekit-server.com --api-key YOUR_KEY --api-secret YOUR_SECRET
   ```

2. **Terminal 2 - Start the Web Server:**
   ```bash
   python web_server.py
   ```
   Or use the helper script:
   ```bash
   ./run_web.sh
   ```

3. **Open your browser:**
   Navigate to `http://localhost:8000`

4. **Use the interface:**
   - Click the mic button to start/stop recording
   - The assistant will respond to your voice
   - Conversation transcript will appear below

### Web Interface Features

- 🎤 Simple mic button to start/stop
- 📝 Real-time conversation transcript
- 🔄 Connection status indicator
- 🎨 Modern, clean UI

## Troubleshooting

If you see the CLI help menu, you need to specify a command:
- `console` - for testing without a server
- `dev` - for development
- `start` - for production

### Web Interface Issues

- **Connection Error**: Make sure both the agent (`dev` mode) and web server are running
- **Microphone not working**: Check browser permissions for microphone access
- **No audio**: Ensure LiveKit server URL, API key, and secret are correct in `.env`

