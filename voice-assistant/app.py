import os
import asyncio
import logging
import base64
import tempfile
import json
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from sarvamai import AsyncSarvamAI
from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
app = FastAPI()

# Mount the 'static' directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

llm_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

async def process_audio_chunk(audio_chunk: bytes, client: AsyncSarvamAI, retry: int = 0):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio_file:
            temp_audio_file.write(audio_chunk)
            temp_audio_file_path = temp_audio_file.name

        job = await client.speech_to_text_job.create_job(
            model="saarika:v2.5",
            with_diarization=True,
            with_timestamps=True,
            language_code="en-IN",
            num_speakers=1,
        )
        logging.info(f"Created STT job: {job._job_id}")

        await job.upload_files(file_paths=[temp_audio_file_path])
        await job.start()
        logging.info("Transcription job started.")
        await job.wait_until_complete(poll_interval=1, timeout=60)

        if await job.is_failed():
            status = await job.get_status()
            logging.error(f"Transcription job failed: {status}")
            return " "

        result = await job.get_result()
        os.remove(temp_audio_file_path)
        
        if result:
            transcript_text = getattr(result, "text", None) or getattr(result, "transcript", None) or result.get("text") or result.get("transcript")
            return transcript_text or ""
        else:
            return ""

    except Exception as e:
        if "TooManyRequests" in str(e) and retry < 3:
            wait = 2 * (retry + 1)
            logging.warning(f"Rate limit hit. Retrying in {wait}s...")
            await asyncio.sleep(wait)
            return await process_audio_chunk(audio_chunk, client, retry + 1)
        else:
            logging.error(f"Error processing audio chunk: {e}", exc_info=True)
            return ""



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logging.info("Client WebSocket connection accepted.")
    client = AsyncSarvamAI(api_subscription_key=SARVAM_API_KEY)
    
    try:
        while True:
            data = await websocket.receive_json()
            if data['type'] == 'stop':
                logging.info("Client sent STOP message.")
                break
            elif data['type'] == 'audio':
                # The data is a base64 data URL, we need to extract the base64 part
                header, encoded = data['data'].split(",", 1)
                audio_chunk = base64.b64decode(encoded)
                transcript = await process_audio_chunk(audio_chunk, client) 
                if transcript:
                    logging.info(f"Transcript: {transcript}")
                    await websocket.send_text(f"Transcript: {transcript}")
                    
                    # Call the LLM with the transcript
                    response = await llm_client.chat.completions.create(
                        model=OPENROUTER_MODEL,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": transcript},
                        ],
                    )
                    llm_response = response.choices[0].message.content
                    logging.info(f"LLM Response: {llm_response}")
                    await websocket.send_text(f"LLM: {llm_response}")

    except WebSocketDisconnect:
        logging.info("Client disconnected.")
    except Exception as e:
        logging.error(f"WebSocket Error: {e}", exc_info=True)
    finally:
        logging.info("Closing client WebSocket connection.")
        if websocket.client_state.value != 3: # 3 is DISCONNECTED
            await websocket.close()