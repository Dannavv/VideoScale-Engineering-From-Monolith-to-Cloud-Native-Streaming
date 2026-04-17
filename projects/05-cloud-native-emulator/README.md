# Project 5: Cloud-Native Emulator (Distributed Pipelines)

## 🎯 The Goal
Understand the **Event-Driven Architecture** used by massive streaming platforms. In this project, we simulate an AWS environment locally to see how "Serverless" pipelines actually scale.

### The "Decoupled" Pipeline
In Project 3, our backend did everything. If the backend crashed, the transcoding stopped.
In Project 5, the components don't even know each other exist:
1. **Upload Service**: Just puts a file in **S3 (Minio)**.
2. **Broker (Redis)**: Holds a "ticket" (Task) saying a new video is ready.
3. **Worker (Lambda simulation)**: Picks up the ticket, downloads the file from S3, encodes it, and puts the result back.

---

## 🛠️ Concepts to Master
- **Object Storage (S3 API):** Interacting with files using buckets and access keys rather than local paths.
- **Message Queues:** Ensuring system reliability. If a worker dies, another one takes the job.
- **Distributed Tasks (Celery):** Running logic on separate CPU cores or even separate machines.
- **Visibility & Monitoring:** Seeing the queue "depth" and worker health.

---

## 🏗️ Architecture
- **API (FastAPI):** Simple gateway for uploads.
- **Storage (Minio):** S3-compatible object store.
- **Queue (Redis):** The message broker between API and Workers.
- **Workers (Python + FFmpeg):** The "Muscle" that does the heavy lifting.

---

## 🚀 How to Run
```bash
docker-compose up -d --build
```
Access the Cloud Console (Dashboard) at:
👉 **http://localhost:8005**

Access the Minio Console (S3 Admin) at:
👉 **http://localhost:9005** (Login: minioadmin / minioadmin)

---

[Back to Roadmap](../../README.md)
