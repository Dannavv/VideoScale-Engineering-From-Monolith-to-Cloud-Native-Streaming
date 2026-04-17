from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import boto3
from celery import Celery
import os
import uuid

app = FastAPI()

# S3 Configuration (Minio)
s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_ENDPOINT", "http://localhost:9000"),
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin"
)

# Celery Configuration (Redis)
celery_app = Celery("video_tasks", broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"))

RAW_BUCKET = "raw-videos"
PROCESSED_BUCKET = "processed-hls"

@app.on_event("startup")
def startup_event():
    # Create buckets if they don't exist
    for b in [RAW_BUCKET, PROCESSED_BUCKET]:
        try:
            s3.create_bucket(Bucket=b)
        except:
            pass

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    video_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    s3_key = f"{video_id}.{file_extension}"
    
    # 1. Upload to S3 (Standard Cloud Practice)
    s3.upload_fileobj(file.file, RAW_BUCKET, s3_key)
    
    # 2. Trigger Worker (Like a Lambda Trigger)
    # We send the job to the queue, the API doesn't wait for transcoding
    celery_app.send_task("tasks.transcode_video", args=[video_id, s3_key])
    
    return {
        "message": "Video uploaded to S3. Processing triggered.",
        "video_id": video_id,
        "s3_path": f"s3://{RAW_BUCKET}/{s3_key}"
    }

@app.get("/list")
async def list_videos():
    """List processed HLS streams from S3"""
    try:
        response = s3.list_objects_v2(Bucket="processed-hls", Delimiter='/')
        folders = response.get('CommonPrefixes', [])
        return {"videos": [f['Prefix'].strip('/') for f in folders]}
    except:
        return {"videos": []}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
