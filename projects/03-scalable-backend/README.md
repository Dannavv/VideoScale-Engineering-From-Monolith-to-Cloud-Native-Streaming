# Project 3: Scalable Monolith Backend

## 🎯 The Goal
Transition from manual FFmpeg scripts to an **automated processing pipeline**. In this project, we build the "Brain" of the video platform.

### Key Evolutionary Step:
In Project 1 & 2, you manually handled files. In Project 3:
1. A user uploads a video via an API.
2. The server saves the "Raw" file to **S3-compatible storage (MinIO)**.
3. An **asynchronous worker** is triggered to transcode the video into HLS.
4. The database tracks the status (Pending, Processing, Completed).

---

## 🛠️ Architecture
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL (Video Metadata & User info)
- **Storage:** MinIO (Self-hosted S3)
- **Queue/Worker:** Celery + Redis (or FastAPI BackgroundTasks for simplicity)
- **Containerization:** Docker Compose for infrastructure.

---

## 🏗️ The System Flow
1. `POST /upload`: Client sends file.
2. `Save`: Raw file stored in `raw-uploads` bucket.
3. `Task`: `transcode_task.delay(video_id)`
4. `Process`: FFmpeg runs inside a worker container.
5. `Store`: HLS segments stored in `processed-videos` bucket.
6. `Query`: `GET /videos` returns a list of playable HLS URLs.

---

## 🚀 Getting Started

### 1. Spin up Infrastructure
We use Docker to run PostgreSQL and MinIO instantly.
```bash
docker-compose up -d
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the API
```bash
uvicorn app.main:app --reload --port 8000
```

---

[Back to Roadmap](../../README.md)
