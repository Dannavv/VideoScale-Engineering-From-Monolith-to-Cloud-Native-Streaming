from fastapi import FastAPI
import time

app = FastAPI()

@app.post("/auth/login")
def login():
    return {
        "access_token": "mock-jwt-token-" + str(int(time.time())),
        "expires_in": 3600
    }

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}
