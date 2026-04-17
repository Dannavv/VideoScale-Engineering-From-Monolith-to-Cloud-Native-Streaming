from celery import Celery
import boto3
import os
import subprocess
from tenacity import retry, stop_after_attempt, wait_exponential

# Celery setup
app = Celery("tasks", broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"))

# S3 Client (Minio)
s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_ENDPOINT", "http://localhost:9000"),
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin"
)

RAW_BUCKET = "raw-videos"
PROCESSED_BUCKET = "processed-hls"

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def download_resiliently(s3_key, local_path):
    print(f"📥 Attempting download of {s3_key}...")
    s3.download_file(RAW_BUCKET, s3_key, local_path)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def upload_resiliently(local_path, s3_path):
    print(f"📤 Attempting upload of {s3_path}...")
    s3.upload_file(local_path, PROCESSED_BUCKET, s3_path)

@app.task(name="tasks.transcode_video")
def transcode_video(video_id, s3_key):
    print(f"🚀 Starting Resilience Task for {video_id}...")
    local_input = f"/tmp/{s3_key}"
    
    # 1. Download with Retry Logic
    try:
        download_resiliently(s3_key, local_input)
    except Exception as e:
        print(f"❌ Failed to download after retries: {e}")
        return {"status": "FAILED", "reason": "S3 Download Error"}

    # 2. Transcode
    output_dir = f"/tmp/{video_id}"
    os.makedirs(output_dir, exist_ok=True)
    local_output = f"{output_dir}/index.m3u8"
    
    cmd = [
        "ffmpeg", "-i", local_input,
        "-profile:v", "baseline", "-level", "3.0",
        "-s", "1280x720", "-start_number", "0",
        "-hls_time", "10", "-hls_list_size", "0",
        "-f", "hls", local_output
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"❌ FFmpeg Error: {e}")
        return {"status": "FAILED", "reason": "Transcoding Error"}
    
    # 3. Upload with Retry Logic
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            local_path = os.path.join(root, file)
            s3_path = f"{video_id}/{file}"
            upload_resiliently(local_path, s3_path)
    
    print(f"✅ Resilience Task Success for {video_id}")
    
    # Cleanup
    os.remove(local_input)
    import shutil
    shutil.rmtree(output_dir)
    return {"status": "SUCCESS", "video_id": video_id}
