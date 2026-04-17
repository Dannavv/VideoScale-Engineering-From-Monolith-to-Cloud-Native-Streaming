# 🎬 Video Streaming Platform: An Engineering Journey

Welcome to the ultimate engineering guide to building video streaming systems. This repository is structured as a **progressive systems journey**, evolving from a single-machine server to a global-scale distributed architecture.

> **Goal:** To build, break, and scale video systems while understanding every bottleneck along the way.

---

## 🗺️ The Roadmap

### 🧠 Phase 0: The Mental Model
Before code, understand the pipeline: `Capture → Encode → Store → Process → Deliver → Play → Scale`.
- [**Master Principles & Architecture Guide**](docs/principles-and-architecture.md) 📕
- [**Mastering FFmpeg: The Field Manual**](docs/ffmpeg-mastery.md) 🛠️

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
