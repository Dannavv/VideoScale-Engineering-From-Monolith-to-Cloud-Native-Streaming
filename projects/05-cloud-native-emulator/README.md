# Project 5: Cloud-Native Emulator

## 🚀 The Goal
Build a distributed, decoupled video pipeline using industry-standard architectural patterns.

## 😰 The Problem
In Project 3, we used a local disk. In a real cloud environment (AWS/Google Cloud), local disks are "Ephemeral"—they get deleted when the server restarts. To scale globally, we need storage that lives outside our servers.

## 💡 The Solution: Object Storage & Task Queues
We replace local paths with the **S3 Architecture**. 
- **MinIO (S3):** Acts as our global file cabinet.
- **Redis (SQS):** Acts as the "Job Broker."
- **Celery (Lambda):** Acts as the "Fleet" of workers that process jobs independently.

## 🛠️ Implementation Idea
**Event-Driven Pipeline:**
1. User uploads to **S3 Ingest Bucket**.
2. API puts a "Job Ticket" into the **Redis Queue**.
3. A **Worker** wakes up, downloads from S3, transcodes, and uploads back to the **S3 Egress Bucket**.

## 🎓 Key Takeaway
**Decouple your compute from your storage.** By using S3 and Queues, your system becomes "Stateless," meaning you can destroy and recreate your servers without losing a single video.

---

## 🚀 How to Run
```bash
docker-compose up -d --build
```
👉 **Cloud Console: http://localhost:8005**

[Back to Roadmap](../../README.md) | [Read the Theory](../../docs/principles-and-architecture.md#5-distributed-storage-project-5)
