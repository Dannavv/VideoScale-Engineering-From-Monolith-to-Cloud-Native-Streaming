from celery import Celery
import boto3
import os
import subprocess

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

@app.task(name="tasks.transcode_video")
def transcode_video(video_id, s3_key):
    print(f"🚀 Starting task for {video_id}...")
    
    # 1. Download from S3
    local_input = f"/tmp/{s3_key}"
    s3.download_file(RAW_BUCKET, s3_key, local_input)
    print(f"📥 Downloaded {s3_key}")
    
    # 2. Transcode (Simulating HLS creation)
    # For speed in this demo, we just create one 720p version
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
    
    subprocess.run(cmd, check=True)
    print(f"🎬 Transcoding complete for {video_id}")
    
    # 3. Upload Output back to S3 (Processed Bucket)
    # We upload the whole directory
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            local_path = os.path.join(root, file)
            s3_path = f"{video_id}/{file}"
            s3.upload_file(local_path, PROCESSED_BUCKET, s3_path)
    
    print(f"📤 Uploaded HLS to s3://{PROCESSED_BUCKET}/{video_id}/")
    
    # Cleanup
    os.remove(local_input)
    import shutil
    shutil.rmtree(output_dir)
    return {"status": "SUCCESS", "video_id": video_id}
