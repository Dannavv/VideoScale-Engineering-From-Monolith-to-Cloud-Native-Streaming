# Project 5: Cloud-Native Emulator

## 🚀 The Goal
Build a distributed, decoupled video pipeline using industry-standard architectural patterns.

## 😰 The Problem
In Project 3, we used a local disk. In a real cloud environment (AWS/Google Cloud), local disks are "Ephemeral"—they get deleted when the server restarts. To scale globally, we need storage that lives outside our servers.

## 💡 The Solution: Object Storage & Task Queues
We replace local paths with the **S3 Architecture**, simulating a high-scale environment where storage, compute, and messaging are decoupled.

```mermaid
graph LR
    User[Web Client] -->|Upload| S3[(MinIO S3)]
    S3 -->|PutEvent| Redis[(Redis Broker)]
    Redis -->|Task| Worker[Celery/Lambda Worker]
    Worker -->|Read/Write| S3
```

### 🧠 Systems Thinking: Scaling Object Storage
In a real production environment (AWS S3), scaling isn't just about disk space; it's about **IOPS Partitioning**. 
- **The Secret:** S3 scales throughput based on your **Object Key Prefix**.
- **The Hack:** By hashing your file names (e.g., `af/12/video.mp4`), you distribute the load across multiple S3 partitions, avoiding "Hot Index" issues.

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
