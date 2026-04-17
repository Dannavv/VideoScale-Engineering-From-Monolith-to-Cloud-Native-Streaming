# 🎬 VideoScale: Scaling from 1k to 100M Users

This isn't just a collection of streaming projects; it is a **Masterclass in System Evolution.** Most platforms fail not because their code is bad, but because their architecture can't handle the next 10x growth spurt. 

This repository simulates the journey of a streaming start-up, solving real-world bottlenecks at every phase: from raw file serving to a globally distributed, DRM-protected, microservices-driven ecosystem.

---

## 📊 Engineering Constraints & Scale Targets

| Phase | Targeted RPS | Concurrency | Latency Budget | Storage Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **1. Scratch** | 10 | 10 Users | < 500ms (TTFB) | Local Disk (RAW) |
| **2. Monolith** | 100 | 1k Users | < 200ms (HLS) | Local Disk (Chunked) |
| **3. Cloud** | 1,000 | 100k Users | < 500ms (Cold) | S3 Object Partitions |
| **4. Elite** | 5,000 | 500k Users | < 50ms (RTC) | Distributed Cache |
| **5. Mesh** | 10,000+ | 1M+ Users | Service-Specific | Multi-Region Mesh |

---

## 🔄 The Life of a Packet (End-to-End)

### 📤 The Upload Flow (Ingest)
`Broadcaster (OBS) → [RTMP Push] → Nginx Ingest → [Event Trigger] → Task Queue (Redis) → Transcoder (FFmpeg) → [Segmenting] → Object Storage (S3)`

### 📥 The Playback Flow (Egress)
`User Player → [GET Manifest] → API Gateway → [Edge Cache Check] → S3 Fallback → [Signed URL Validation] → Packet Stream → Decoder → Screen`

---

## 🗺️ The Roadmap

### 🧠 Phase 0: The Mental Model
Before code, understand the pipeline: `Capture → Encode → Store → Process → Deliver → Play → Scale`.
- [**Master Principles & Architecture Guide**](docs/principles-and-architecture.md) 📕
- [**Mastering FFmpeg: The Field Manual**](docs/ffmpeg-mastery.md) 🛠️
- [**System Failure & Resilience Modeling**](docs/failure-modeling.md) 🐜

### 🧩 Phase 1: From Scratch (Raw Basics) 
- **Project 1:** [Basic Video Streaming Server](projects/01-basic-streaming-server/README.md) - Mastery of `206 Partial Content` and Range Requests.
- **Project 2:** [DIY HLS & Adaptive Bitrate](projects/02-build-your-own-hls/README.md) - Implementing ABR with FFmpeg and HLS.js.

### ⚙️ Phase 2: System Thinking (The Monolith) 
- **Project 3:** [Scalable Monolith](projects/03-scalable-backend/README.md) - Automated FastAPI pipeline with background workers and real-time dashboard.
- **Project 4:** [Streaming Optimization](projects/04-streaming-optimization/README.md) - Nginx Edge Caching, Proxying, and HMAC-SHA256 Signed URLs.

### ☁️ Phase 3: Industry Standards (The Cloud Emulator) 
- **Project 5:** [Cloud-Native Emulator](projects/05-cloud-native-emulator/README.md) - Simulating AWS S3 (Minio), SQS (Redis), and Lambda (Celery) in a distributed cluster.
- **Project 6:** [Chaos & Resilience](projects/06-chaos-and-resilience/README.md) - Designing for failure with Chaos Monkey (Pumba) and Retry logic.

### 🎥 Phase 4: Real-Time & Security (The Elite Level)
- **Project 7:** [Real-time Live Streaming](projects/07-live-streaming/README.md)  - RTMP ingestion and Live HLS repackaging.
- **Project 8:** [DRM & Content Protection](projects/08-drm-protection/README.md)  - AES-128 Encryption and ClearKey License Servers.
- **Project 9:** [Ultra-Low Latency (WebRTC)](projects/09-webrtc-low-latency/README.md)  - Real-time communication with <500ms delay.

### 🧱 Phase 5: Distributed Scale (Microservices) 
- **Project 10:** [Microservices Migration](projects/10-microservices-migration/README.md)  - Transitioning to a decoupled Service Mesh.

---

## 📂 Repository Structure

- `docs/`: Deep dives into concepts (The "Book" portion).
- `projects/`: Hands-on implementations for each phase.
- `samples/`: Centralized raw media assets.
- `assets/`: Architectural diagrams.

---

## 🛠️ Global Tech Stack
- **Languages:** Node.js, Python (FastAPI)
- **Engine:** FFmpeg
- **Storage:** Local FS, Minio (S3 Compatible)
- **Brokers:** Redis
- **Infra:** Docker, Nginx, Pumba
