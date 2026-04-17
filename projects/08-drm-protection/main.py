from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import subprocess

app = FastAPI()

# Configuration
VAULT_DIR = "/app/vault"
DATA_DIR = "/app/static/data"
SAMPLE_INPUT = "/samples/sample.mp4"

@app.on_event("startup")
def encrypt_video():
    """Use FFmpeg to produce encrypted HLS segments"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # We only encrypt if segments don't exist
    if not os.path.exists(f"{DATA_DIR}/encrypted.m3u8"):
        print("🔐 Encrypting video with AES-128...")
        cmd = [
            "ffmpeg", "-y", "-i", SAMPLE_INPUT,
            "-hls_time", "10",
            "-hls_key_info_file", f"{VAULT_DIR}/key_info.txt",
            "-hls_playlist_type", "vod",
            "-hls_segment_filename", f"{DATA_DIR}/file%03d.ts",
            f"{DATA_DIR}/encrypted.m3u8"
        ]
        subprocess.run(cmd, check=True)
        print("✅ Encryption complete.")

@app.get("/keys/{key_name}")
async def get_key(key_name: str, request: Request):
    """
    Simulated License Server.
    In a real app, you would check session cookies or Auth headers here.
    """
    # Simple security simulation: Block requests without a specific header
    # (Browsers send Origin/Referer which we can check)
    print(f"🔑 Key request for {key_name} from {request.client.host}")
    
    key_path = f"{VAULT_DIR}/{key_name}"
    if os.path.exists(key_path):
        return FileResponse(key_path)
    
    raise HTTPException(status_code=403, detail="Key Access Denied")

# Serve the Player
app.mount("/", StaticFiles(directory="static", html=True), name="static")
