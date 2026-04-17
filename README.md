# 🎬 VideoScale: Scaling from 1k to 100M Users

This isn't a collection of streaming projects; it is a **system design artifact** that simulates the engineering journey of a streaming startup — from raw file serving to a globally distributed, DRM-protected, microservices-driven ecosystem.

Every phase documents what broke, what we built to fix it, and what new problems we introduced.

---

## 📊 Quantitative Pressure Model

| Scale | Concurrent Users | Upload RPS | Playback RPS | DB CPU | Transcode Queue | Breaking Symptom |
|---|---|---|---|---|---|---|
| **Prototype** | 10 | 1/s | 10/s | 5% | 0 | Nothing breaks |
| **Launch** | 1,000 | 10/s | 500/s | 25% | 2-3 jobs | TTFB > 800ms on cold starts |
| **Growth** | 10,000 | 50/s | 5,000/s | 65% | 15-20 jobs | Upload latency > 2.8s. Transcoder falls behind |
| **Viral** | 100,000 | 200/s | 50,000/s | 85% | 200+ jobs | DB lock contention. API 502s spike to 3% |
| **Scale** | 1,000,000 | 500/s | 200,000/s | N/A (sharded) | Distributed | Single-region CDN saturates. Latency > 500ms for distant users |
| **Global** | 10,000,000+ | 2,000/s | 1,000,000/s | N/A (multi-region) | Multi-region | Requires geo-routed CDN + edge transcoding |

### What Breaks When (The Pressure Points)

```
At 1,000 users:
  └─► Single server handles it. No issues.

At 10,000 users:
  └─► Upload latency = 2.8s (target: < 500ms)
  └─► Transcoder queue depth = 20 (target: < 5)
  └─► FFmpeg CPU usage = 92% → API starved

At 100,000 users:
  └─► DB CPU = 85% → write latency = 450ms (target: < 50ms)
  └─► 3% of API requests return 502
  └─► CDN cache miss rate = 12% (target: < 5%)
  └─► Estimated monthly cost: $2,300

At 1,000,000 users:
  └─► DB lock contention → catalog writes fail intermittently
  └─► Single-origin bandwidth saturated (10 Gbps NIC maxed)
  └─► CDN egress cost = $23,000/month
  └─► Must shard database and deploy multi-region
```

---

## 🔄 Data Flow Pipelines

### Upload Flow (Ingest)

```mermaid
graph LR
    Client[Client App] -->|POST /upload| GW[API Gateway]
    GW -->|Auth Check| Auth[Auth Service]
    GW -->|Store Raw| S3[(Object Storage)]
    S3 -->|Event| Queue[Redis Task Queue]
    Queue -->|Dequeue| Worker[Transcoder Worker]
    Worker -->|FFmpeg| Worker
    Worker -->|PUT segments| S3cdn[(CDN Storage)]
    Worker -->|Update status| DB[(Catalog DB)]
```

### Playback Flow (Egress)

```mermaid
graph LR
    Player[Video Player] -->|GET master.m3u8| CDN[CDN Edge]
    CDN -->|Cache HIT| Player
    CDN -->|Cache MISS| Origin[API Gateway]
    Origin -->|Signed URL Check| Auth[Auth Service]
    Origin -->|Fetch Segment| S3[(Object Storage)]
    S3 -->|.ts chunk| Origin
    Origin -->|Cache + Respond| CDN
    CDN -->|segment_001.ts| Player
    Player -->|ABR Decision| Player
```

### Live Streaming Flow

```mermaid
graph LR
    OBS[OBS/Camera] -->|RTMP Push| Ingest[Nginx RTMP Module]
    Ingest -->|Real-time Transcode| FFmpeg[FFmpeg]
    FFmpeg -->|6s .ts segments| Disk[/tmp/hls/]
    Disk -->|Nginx Static Serve| CDN[CDN Edge]
    CDN -->|HLS .m3u8 + .ts| Player[HLS.js Player]
    Player -->|ABR Switch| Player
```

---

## 🎬 HLS Streaming Lifecycle (Center Stage)

This is a **streaming-first** system. Every architectural decision serves the goal of delivering `.ts` segments to the player as fast and reliably as possible.

### The Life of a Video Segment

```
1. RAW UPLOAD
   └─► User uploads sample.mp4 (H.264, 1080p, 2GB)

2. TRANSCODE (FFmpeg)
   └─► Split into 4 quality ladders: 1080p / 720p / 480p / 360p
   └─► Each quality encoded with constrained bitrate (-maxrate, -bufsize)
   └─► Output: 4 streams × ~200 segments each = ~800 .ts files

3. SEGMENT (.ts chunk lifecycle)
   └─► Each segment = exactly 6 seconds of video
   └─► Segment naming: stream_0/seg_000.ts, stream_0/seg_001.ts, ...
   └─► Segment size: 360p=0.7MB, 480p=1.1MB, 720p=2.2MB, 1080p=3.8MB
   └─► Stored in S3 with hash-prefix keys for IOPS distribution

4. MANIFEST (.m3u8 playlist generation)
   └─► Master playlist: lists all quality levels with BANDWIDTH tags
   └─► Media playlist (per quality): ordered list of .ts segment URLs
   └─► EXT-X-TARGETDURATION: 6 (tells player the max segment length)
   └─► For DRM: EXT-X-KEY tag points to license server URL

5. ABR SWITCHING (client-side, HLS.js)
   └─► Player downloads 1st segment at lowest quality (fast startup)
   └─► Measures download speed: segment_size / download_time
   └─► If bandwidth > 2× next level requirement → upgrade quality
   └─► If buffer < 5 seconds → emergency drop to lowest quality
   └─► Stability guard: max 3 quality switches per 60s

6. BUFFER → DECODE → RENDER
   └─► Browser maintains 15-30s buffer ahead of playhead
   └─► Each .ts is demuxed (video + audio separated)
   └─► H.264 decoded by hardware (GPU) or software (CPU)
   └─► Frames rendered at display refresh rate (60fps)
```

### Segment Request Volume at Scale

| Viewers | Segments/sec (6s chunks) | CDN Requests/min | Bandwidth (720p avg) |
|---|---|---|---|
| 1,000 | 167/s | 10,000/min | 2.8 Gbps |
| 100,000 | 16,700/s | 1M/min | 280 Gbps |
| 1,000,000 | 167,000/s | 10M/min | 2.8 Tbps |

---

## 📈 Operational Baseline (SLIs / SLOs)

| Signal (SLI) | Target (SLO) | Alert Threshold | Measured At |
|---|---|---|---|
| Stream startup time | < 2.0s (p95) | > 3.0s | Client-side beacon |
| Rebuffer ratio | < 0.5% of watch time | > 1.0% | Client-side beacon |
| API p99 latency | < 200ms | > 500ms | Nginx access log |
| Transcode queue depth | < 5 jobs | > 20 jobs | Redis LLEN |
| CDN cache hit ratio | > 95% | < 90% | Nginx $upstream_cache_status |
| Upload success rate | > 99.5% | < 98% | API 2xx/total ratio |
| Error rate (5xx) | < 0.1% | > 1.0% | Nginx error log |

### Scaling Triggers

```
IF   CPU > 70% sustained 5min     → add API container (max 10)
IF   transcode queue > 20         → add worker container (max 20)
IF   WebRTC sessions > 500/server → reject new connections (503)
IF   CDN miss rate > 10%          → pre-warm cache for trending content
IF   p99 latency > 500ms          → enable request shedding (drop 10% lowest-priority)
```

### Reliability Patterns (Implemented)

| Pattern | Where | Behavior |
|---|---|---|
| Exponential backoff | Transcoder → S3 | 0s → 2s → 4s → 8s → fail to DLQ |
| Circuit breaker | Worker → MinIO | Open after 5 failures/60s. Probe every 30s |
| Idempotent workers | Celery tasks | `IF EXISTS output → skip` (no duplicate segments) |
| Rate limiting | Nginx gateway | 50 req/s per IP, 5 uploads/min per user |
| Request collapsing | Nginx proxy_cache | `proxy_cache_lock on` (1 origin fetch per segment) |

---

## 💰 Cost at Scale

| Scale | Compute | Storage (S3) | CDN Egress | Total/month | Per-User/month |
|---|---|---|---|---|---|
| 1K users | $50 | $12 | $30 | **$92** | $0.092 |
| 10K users | $200 | $120 | $300 | **$620** | $0.062 |
| 100K users | $800 | $500 | $3,000 | **$4,300** | $0.043 |
| 1M users | $5,000 | $2,500 | $23,000 | **$30,500** | $0.031 |

### Where the Money Goes

```
At 100K users:
  CDN Egress:   70% of total cost  ← THIS IS THE #1 COST DRIVER
  Compute:      18% (transcoding + API)
  Storage:      12% (4 quality levels × all videos)

Cost Optimization Levers:
  1. CDN cache hit > 95%        → saves 19× origin egress
  2. Default to 480p (not 1080p) → halves avg bandwidth/user
  3. Transcode only popular videos → skip 4K for <100 view videos
  4. Storage tiering:
     ├─► HOT  (SSD, S3 Standard):   last 7 days of segments
     ├─► WARM (HDD, S3 IA):         8-90 day old segments
     └─► COLD (S3 Glacier):         >90 days, restore in 5-12 hours
  5. Spot instances for workers → 70% compute savings
```

---

## 🗺️ The Roadmap

### 🧠 Phase 0: The Mental Model
Before code, understand the pipeline: `Capture → Encode → Store → Process → Deliver → Play → Scale`.
- [**Master Principles & Architecture Guide**](docs/principles-and-architecture.md) 📕
- [**Mastering FFmpeg: The Field Manual**](docs/ffmpeg-mastery.md) 🛠️
- [**Streaming Internals: HLS, ABR, & Buffering**](docs/streaming-internals.md) 🎬
- [**System Failure & Resilience Modeling**](docs/failure-modeling.md) 🐜
- [**Operations Runbook: Metrics, Scaling, & Cost**](docs/operations-runbook.md) 🔧

### 🧩 Phase 1: From Scratch (< 1K Users)
- **Project 1:** [Basic Video Streaming Server](projects/01-basic-streaming-server/README.md) - Mastery of `206 Partial Content` and Range Requests.
- **Project 2:** [DIY HLS & Adaptive Bitrate](projects/02-build-your-own-hls/README.md) - Implementing ABR with FFmpeg and HLS.js.

### ⚙️ Phase 2: The Monolith (1K → 10K Users)
- **Project 3:** [Scalable Monolith](projects/03-scalable-backend/README.md) - Automated FastAPI pipeline with background workers and real-time dashboard.
- **Project 4:** [Streaming Optimization](projects/04-streaming-optimization/README.md) - Nginx Edge Caching, Proxying, and HMAC-SHA256 Signed URLs.

### ☁️ Phase 3: Cloud-Native (10K → 100K Users)
- **Project 5:** [Cloud-Native Emulator](projects/05-cloud-native-emulator/README.md) - Simulating AWS S3 (Minio), SQS (Redis), and Lambda (Celery).
- **Project 6:** [Chaos & Resilience](projects/06-chaos-and-resilience/README.md) - Designing for failure with Chaos Monkey (Pumba) and retry logic.

### 🎥 Phase 4: Real-Time & Security (100K → 1M Users)
- **Project 7:** [Real-time Live Streaming](projects/07-live-streaming/README.md) - RTMP ingestion and Live HLS repackaging.
- **Project 8:** [DRM & Content Protection](projects/08-drm-protection/README.md) - AES-128 Encryption and ClearKey License Servers.
- **Project 9:** [Ultra-Low Latency (WebRTC)](projects/09-webrtc-low-latency/README.md) - Real-time communication with <500ms delay.

### 🧱 Phase 5: Service Mesh (1M+ Users)
- **Project 10:** [Microservices Migration](projects/10-microservices-migration/README.md) - Transitioning to a decoupled Service Mesh.

---

## 🏭 Production Readiness Checklist

| Category | Requirement | Status |
|---|---|---|
| **Resilience** | Retry with exponential backoff | ✅ Implemented (Project 6) |
| **Resilience** | Circuit breaker on storage calls | ✅ Implemented (Project 6) |
| **Resilience** | Idempotent transcoding workers | ✅ Implemented (Project 5) |
| **Security** | Rate limiting (per-IP + per-route) | ✅ Implemented (Project 10 Gateway) |
| **Security** | HMAC signed URLs with TTL | ✅ Implemented (Project 4) |
| **Security** | AES-128 segment encryption | ✅ Implemented (Project 8) |
| **Streaming** | HLS segmentation with ABR | ✅ Implemented (Project 2) |
| **Streaming** | Adaptive bitrate switching | ✅ Implemented (HLS.js client) |
| **Streaming** | Sub-second latency (WebRTC) | ✅ Implemented (Project 9) |
| **Ops** | Health check endpoints | ✅ Implemented (all services) |
| **Ops** | Structured logging | 📋 Documented (Runbook) |
| **Ops** | Distributed tracing | 📋 Documented (Runbook) |
| **Ops** | Autoscaling rules | 📋 Documented (Runbook) |
| **Cost** | CDN cache optimization (>95% hit) | 📋 Documented (Runbook) |
| **Cost** | Per-user cost model | 📋 Documented (Runbook) |

---

## 📂 Repository Structure

- `docs/` — Deep dives: streaming internals, failure modeling, operations, FFmpeg
- `projects/` — Hands-on implementations for each scaling phase
- `samples/` — Centralized raw media assets
- `assets/` — Architectural diagrams

---

## 🛠️ Global Tech Stack
- **Languages:** Node.js, Python (FastAPI)
- **Engine:** FFmpeg, HLS.js, Aiortc (WebRTC)
- **Storage:** Local FS, MinIO (S3-compatible)
- **Brokers:** Redis (Queue + Pub/Sub)
- **Infra:** Docker, Nginx (RTMP + Reverse Proxy), Pumba (Chaos)
