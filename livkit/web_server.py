"""
Web server for LiveKit Voice Agent
Serves the frontend and generates LiveKit access tokens
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
import os
from pathlib import Path
from livekit import api

# Load environment variables - use absolute path
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the main HTML page"""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.post("/api/token")
async def get_token():
    """
    Generate a LiveKit access token for the client
    """
    try:
        # Get LiveKit credentials from environment
        livekit_url = os.getenv("LIVEKIT_URL")
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        if not all([livekit_url, api_key, api_secret]):
            raise HTTPException(
                status_code=500,
                detail="LiveKit credentials not configured. Please set LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET in your .env file"
            )
        
        # Check if using localhost (development) credentials
        if livekit_url.startswith("ws://localhost") or livekit_url.startswith("ws://127.0.0.1"):
            raise HTTPException(
                status_code=500,
                detail="Please update LIVEKIT_URL in your .env file with your LiveKit Cloud URL (should start with wss://your-project.livekit.cloud). Get credentials from https://cloud.livekit.io"
            )
        
        # Generate a unique room name (you could make this dynamic)
        room_name = "voice-assistant-room"
        participant_name = "user"
        
        # Create access token
        token = api.AccessToken(api_key, api_secret) \
            .with_identity(participant_name) \
            .with_name(participant_name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            ))
        
        token_str = token.to_jwt()
        
        return JSONResponse(content={
            "token": token_str,
            "url": livekit_url,
            "room": room_name
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

