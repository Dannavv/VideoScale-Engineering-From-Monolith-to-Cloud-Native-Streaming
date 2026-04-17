from fastapi import FastAPI
import os

app = FastAPI()

# Simulated database
CATEGORIES = {
    "trending": ["Video 1", "Video 2"],
    "new": ["Video 3", "Video 4"],
    "live": ["Real-time Stream"]
}

@app.get("/catalog")
def get_catalog():
    return {
        "service": "Catalog-v1",
        "status": "Healthy",
        "data": CATEGORIES
    }

@app.get("/health")
def health():
    return {"status": "ok", "service": "catalog"}
