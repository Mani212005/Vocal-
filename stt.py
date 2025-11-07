import asyncio
import base64
import os
import contextlib
from sarvamai import AsyncSarvamAI
from converttowav import save_audio, ogg_to_wav_ffmpeg  # ✅ import from your helper
import dotenv

dotenv.load_dotenv()  # ✅ load environment variables

# Fetch your API key from .env
sarvam_api_key = os.getenv("SARVAM_API_KEY")


async def stream_to_sarvam(wav_path, api_key):
    """Send the given wav file to Sarvam STT and print live transcript"""
    with open(wav_path, "rb") as f:
         audio_data = f.read()

    client = AsyncSarvamAI(api_subscription_key=api_key)

    async with client.speech_to_text_streaming.connect(
        language_code="en-IN",
        model="saarika:v2.5",
        sample_rate=16000,
        input_audio_codec="wav",
        high_vad_sensitivity=True,
        #vad_signals=True,
        flush_signal=False,
    ) as ws:
        print("🔗 Connected to Saarika v2.5 streaming service")

        # Send audio data
        await ws.transcribe(audio=audio_data, encoding="audio/wav", sample_rate=16000)
        #await ws.transcribe(audio=audio_data, encoding="audio/wav", sample_rate=16000)
        print("🎧 Audio data sent for transcription")

        # Optional flush to force immediate processing
        await asyncio.sleep(2)
        await ws.flush()
        print("⚡ Flush signal sent (forces immediate processing)")

        print("⌛ Waiting for transcription results...\n")
        with contextlib.suppress(asyncio.TimeoutError):
            async with asyncio.timeout(20):  # wait max 20s for messages
                async for message in ws:
                    if message.type == "speech_start":
                        print("🎤 Speech detection started")
                    elif message.type == "speech_end":
                        print("🔇 Speech detection ended")
                    elif message.type == "transcript":
                        print(f"📝 Transcription: {message.text}")


if __name__ == "__main__":
    audio_url = "https://phone91.com/461220/whatsapp/70529281-935d-4ef4-ad58-682554548d94.file.ogg"

    # ✅ Step 1: Download .ogg and convert to .wav
    ogg_file = save_audio(audio_url)
    wav_file = ogg_to_wav_ffmpeg(ogg_file)

    # ✅ Step 2: Stream .wav file to Sarvam
    asyncio.run(stream_to_sarvam(wav_file, sarvam_api_key))
