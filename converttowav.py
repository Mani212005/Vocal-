import requests
import time
import subprocess
import os
import ffmpeg

def save_audio(audio_url):
    """Download WhatsApp audio (.ogg) file."""
    print("Downloading audio...")
    response = requests.get(audio_url, allow_redirects=True)
    response.raise_for_status()

    filename = f"voice-{int(time.time())}.ogg"
    with open(filename, "wb") as f:
        f.write(response.content)

    print(f"Saved to {filename}")
    return filename


def ogg_to_wav_ffmpeg(in_path, sr=16000):
    """Convert .ogg file to .wav using ffmpeg."""
    out_path = os.path.splitext(in_path)[0] + ".wav"
    cmd = ["ffmpeg", "-y", "-i", in_path, "-ar", str(sr), "-ac", "1", out_path]

    print(f"Converting {in_path} → {out_path} ...")
    subprocess.run(cmd, check=True)
    print(f"Conversion complete: {out_path}")
    return out_path


# 🔽 Example flow: Download from WhatsApp and convert
audio_url = "https://phone91.com/461220/whatsapp/70529281-935d-4ef4-ad58-682554548d94.file.ogg"

# Step 1: Download the OGG file
ogg_file = save_audio(audio_url)

# Step 2: Convert it to WAV
wav_file = ogg_to_wav_ffmpeg(ogg_file)

print("✅ All done! Ready to send to Sarvam:", wav_file)
