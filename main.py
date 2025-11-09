from sarvamai import SarvamAI
from converttowav import save_audio, ogg_to_wav_ffmpeg
import os
import dotenv

def main():
    # ✅ Load API key
    dotenv.load_dotenv()
    sarvam_api_key = os.getenv("SARVAM_API_KEY")

    # ✅ Step 1: Download and convert audio
    audio_url = "https://phone91.com/461220/whatsapp/70529281-935d-4ef4-ad58-682554548d94.file.ogg"
    ogg_file = save_audio(audio_url)
    wav_file = ogg_to_wav_ffmpeg(ogg_file)

    # ✅ Step 2: Initialize Sarvam client
    client = SarvamAI(api_subscription_key=sarvam_api_key)

    # ✅ Step 3: Create transcription job
    print("📤 Creating STT job...")
    job = client.speech_to_text_job.create_job(
        language_code="en-IN",
        model="saarika:v2.5",
        with_diarization=True,
        num_speakers=1
    )

    # ✅ Step 4: Upload converted WAV
    print("⬆️ Uploading audio file...")
    job.upload_files(file_paths=[wav_file])

    # ✅ Step 5: Start and wait
    job.start()
    print("🚀 Transcription started. Waiting for completion...")
    job.wait_until_complete()

    if job.is_failed():
        print("❌ STT job failed.")
        return

    # ✅ Step 6: Download output
    output_dir = "./output"
    job.download_outputs(output_dir=output_dir)
    print(f"✅ Transcription completed and saved in {output_dir}")

if __name__ == "__main__":
    main()
