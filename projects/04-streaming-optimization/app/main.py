from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import hmac
import hashlib
import time
import base64
import os

app = FastAPI(title="Streaming Optimization Engine")

SECRET_KEY = b"my-streaming-secret"
SAMPLE_VIDEO = "/samples/sample1.mp4"

# --- Security Logic ---
def verify_token(resource_path: str, expires: int, token: str):
    if int(time.time()) > expires:
        return False
    message = f"{resource_path}:{expires}".encode()
    expected_signature = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()
    expected_token = base64.urlsafe_b64encode(expected_signature).decode().rstrip("=")
    return hmac.compare_digest(token, expected_token)

# --- Routes ---

@app.get("/api/sign")
async def sign_resource(path: str):
    """API for the UI to get a signed link"""
    expires = int(time.time()) + 60 # Valid for 60 seconds for demo
    message = f"{path}:{expires}".encode()
    signature = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return {"signed_url": f"{path}?expires={expires}&token={token}"}

@app.get("/secure-video")
async def get_video(expires: int = Query(...), token: str = Query(...)):
    """A protected endpoint that requires a valid signature"""
    if not verify_token("/secure-video", expires, token):
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid or Expired Token")
    
    # In a real app, this would be a .ts segment
    if os.path.exists(SAMPLE_VIDEO):
        return FileResponse(SAMPLE_VIDEO)
    else:
        raise HTTPException(status_code=404, detail="Video sample not found")

@app.get("/status")
async def get_status(request: Request):
    """Used to check Nginx Cache Headers in the UI"""
    return {
        "message": "Origin reached!",
        "timestamp": time.time(),
        "headers": dict(request.headers)
    }

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
