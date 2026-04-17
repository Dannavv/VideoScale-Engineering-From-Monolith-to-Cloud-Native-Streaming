from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
import time
import asyncio
from asyncio import subprocess

app = FastAPI(title="VideoScale Pipeline Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

videos_db = {}

# Folder Structure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "temp_uploads")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

@app.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    video_id = str(uuid.uuid4())
    filename = f"{video_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    videos_db[video_id] = {
        "id": video_id,
        "name": file.filename,
        "status": "Queued",
        "progress": 0,
        "url": None,
        "created_at": time.strftime("%H:%M:%S")
    }
    
    background_tasks.add_task(run_transcoding_pipeline, video_id, file_path)
    
    return {"id": video_id}

@app.get("/videos")
async def get_videos():
    return list(videos_db.values())

async def run_transcoding_pipeline(video_id: str, input_path: str):
    video = videos_db[video_id]
    output_folder = os.path.join(PROCESSED_DIR, video_id)
    os.makedirs(output_folder, exist_ok=True)
    
    playlist_path = "index.m3u8"
    
    video["status"] = "Generating HLS"
    video["progress"] = 20
    
    # FFmpeg command for basic HLS (Project 3 focus is on the system, not just the encoding)
    # We produce localized segments in the 'processed' folder
    cmd = [
        "ffmpeg", "-i", input_path,
        "-codec:v", "libx264", "-codec:a", "aac",
        "-hls_time", "10", "-hls_playlist_type", "vod",
        "-hls_segment_filename", f"{output_folder}/seg%03d.ts",
        os.path.join(output_folder, playlist_path)
    ]
    
    try:
        # Run ffmpeg as a subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Monitor progress while ffmpeg runs
        while True:
            try:
                # Check if process finished (wait for 1 second)
                await asyncio.wait_for(process.wait(), timeout=1.0)
                break # Process finished
            except asyncio.TimeoutError:
                # Still running, increment progress
                if video["progress"] < 90:
                    video["progress"] += 5
        
        video["status"] = "Completed"
        video["progress"] = 100
        video["url"] = f"/stream/{video_id}/{playlist_path}"
        
        # Cleanup raw upload
        if os.path.exists(input_path):
            os.remove(input_path)
            
    except Exception as e:
        video["status"] = f"Error: {str(e)}"
        video["progress"] = 0

# Serve HLS content
app.mount("/stream", StaticFiles(directory=PROCESSED_DIR), name="stream")
# Serve UI
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True), name="static")
