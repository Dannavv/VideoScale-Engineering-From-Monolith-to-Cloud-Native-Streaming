# 🎬 Video Streaming Platform: An Engineering Journey

Welcome to the ultimate engineering guide to building video streaming systems. This repository is structured as a **progressive systems journey**, evolving from a single-machine server to a global-scale distributed architecture.

> **Goal:** To build, break, and scale video systems while understanding every bottleneck along the way.

---

## 🗺️ The Roadmap

### 🧠 Phase 0: The Mental Model
Before code, understand the pipeline: `Capture → Encode → Store → Process → Deliver → Play → Scale`.
- [Conceptual Overview](docs/phase-0-mental-model.md)

### 🧩 Phase 1: From Scratch (Raw Basics) ✅
- **Project 1:** [Basic Video Streaming Server](projects/01-basic-streaming-server/README.md) - Mastery of `206 Partial Content` and Range Requests.
- **Project 2:** [DIY HLS & Adaptive Bitrate](projects/02-build-your-own-hls/README.md) - Implementing ABR with FFmpeg and HLS.js.

### ⚙️ Phase 2: System Thinking (The Monolith) ✅
- **Project 3:** [Scalable Monolith](projects/03-scalable-backend/README.md) - Automated FastAPI pipeline with background workers and real-time dashboard.
- **Project 4:** [Streaming Optimization](projects/04-streaming-optimization/README.md) - Nginx Edge Caching, Proxying, and HMAC-SHA256 Signed URLs.

### ☁️ Phase 3: Industry Standards (The Cloud Emulator) ✅
- **Project 5:** [Cloud-Native Emulator](projects/05-cloud-native-emulator/README.md) - Simulating AWS S3 (Minio), SQS (Redis), and Lambda (Celery) in a distributed, event-driven cluster.

### 🏗️ Phase 4: The Next Frontier
- **Project 6:** Chaos & Resilience (Simulating Network Failures and Worker Crashes)
- **Project 7:** Real-time Live Streaming (RTMP, WebSockets)

---

## 📂 Repository Structure

- `docs/`: Deep dives into concepts (The "Book" portion).
- `projects/`: Hands-on implementations for each phase.
- `samples/`: Centralized raw media assets used across all projects.
- `assets/`: Architectural diagrams and media assets.

---

## 🛠️ Global Tech Stack
- **Languages:** Node.js, Python (FastAPI)
- **Engine:** FFmpeg
- **Storage:** Local FS, Minio (S3 Compatible)
- **Brokers:** Redis
- **Infra:** Docker, Nginx, Traefik
