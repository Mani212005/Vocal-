import os
import sys
import base64
import json
import asyncio
import websockets
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Load environment variables from .env
load_dotenv()

SARVAM_WS_URL = os.getenv("SARVAM_WS_URL", "wss://api.sarvam.ai/speech-to-text-websocket")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en-IN")
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", 16000))
HIGH_VAD_SENSITIVITY = os.getenv("HIGH_VAD_SENSITIVITY", "false")
API_KEY = os.getenv("SARVAM_API_KEY")

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established with client.")

    if not API_KEY:
        await websocket.send_text("Error: SARVAM_API_KEY missing. Please set it in .env file.")
        await websocket.close()
        return

    try:
        # Connect to Sarvam AI WebSocket
        headers = [("Authorization", f"Bearer {API_KEY}")]
        # async with websockets.connect(SARVAM_WS_URL, extra_headers=headers) as sarvam_ws:
        async with websockets.connect(SARVAM_WS_URL, additional_headers=headers) as sarvam_ws:
            print("Connected to Sarvam AI WebSocket.")

            # Send config to Sarvam AI
            config = {
                "language-code": DEFAULT_LANGUAGE,
                "high_vad_sensitivity": HIGH_VAD_SENSITIVITY,
            }
            await sarvam_ws.send(json.dumps({"event": "config", "data": config}))

            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                if message["type"] == "audio":
                    # Frontend sends base64, decode it
                    audio_base64 = message["data"].split(",")[1] # Remove "data:audio/webm;base64," prefix
                    
                    # Send audio to Sarvam AI
                    await sarvam_ws.send(json.dumps({
                        "event": "transcribe",
                        "data": {
                            "audio": audio_base64,
                            "sample_rate": SAMPLE_RATE,
                            "encoding": "audio/webm", # Assuming webm from frontend
                        }
                    }))

                    # Receive and forward transcription from Sarvam AI
                    sarvam_response = await sarvam_ws.recv()
                    sarvam_data = json.loads(sarvam_response)
                    if "text" in sarvam_data:
                        await websocket.send_text(sarvam_data["text"])
                    elif "error" in sarvam_data:
                        print(f"Sarvam AI Error: {sarvam_data['error']}")
                        await websocket.send_text(f"Error: {sarvam_data['error']}")

                elif message["type"] == "stop":
                    print("Client requested to stop recording.")
                    break

    except websockets.exceptions.ConnectionClosedOK:
        print("Sarvam AI WebSocket connection closed normally.")
    except WebSocketDisconnect:
        print("Client WebSocket disconnected.")
    except Exception as e:
        print(f"An error occurred: {e}")
        await websocket.send_text(f"Server error: {e}")
    finally:
        print("Closing client WebSocket connection.")
        await websocket.close()

# The command-line transcription part is removed as it's no longer the primary function.
# If needed, it can be re-added as a separate utility or API endpoint. 
