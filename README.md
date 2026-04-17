# 🎬 VideoScale: Engineering a Global Streaming Platform

![VideoScale Architecture Banner](assets/cover.png)

**This is not a backend project that happens to serve video.** This is a **streaming-first system** where every architectural decision — from storage partitioning to circuit breaker thresholds — exists to deliver `.ts` segments to a player buffer within 200ms, at any scale, anywhere in the world.

The system evolves through 5 phases, each triggered by a specific failure at a specific scale. Every phase documents what broke, what we built to fix it, and what new problems we introduced.

---

## 🗺️ The Engineering Roadmap

The repository is structured as a progressive journey from a simple prototype to a globally distributed, resilient architecture.

### 🧠 Phase 0: The Mental Model
Before code, understand the pipeline: `Capture → Encode → Store → Process → Deliver → Play → Scale`.
- [**Master Principles & Architecture Guide**](docs/principles-and-architecture.md) 📕
- [**Mastering FFmpeg: The Field Manual**](docs/ffmpeg-mastery.md) 🛠️
- [**Streaming Internals: HLS, ABR, & Buffering**](docs/streaming-internals.md) 🎬
- [**System Failure & Resilience Modeling**](docs/failure-modeling.md) 🐜
- [**Operations Runbook: Metrics, Scaling, & Cost**](docs/operations-runbook.md) 🔧
- [**Cost Architecture: Where the Money Goes**](docs/cost-architecture.md) 💰
- [**Hyperscale: The 100M User Architecture**](docs/hyperscale.md) 🌍

### 🧩 Phase 1: From Scratch (< 1K Users)
- **Project 1:** [Basic Video Streaming Server](projects/01-basic-streaming-server/README.md) — `206 Partial Content`, Range Requests, byte-level streaming.
- **Project 2:** [DIY HLS & Adaptive Bitrate](projects/02-build-your-own-hls/README.md) — `.ts` segmentation, `.m3u8` manifests, ABR with HLS.js.

### ⚙️ Phase 2: The Monolith (1K → 10K Users)
- **Project 3:** [Scalable Monolith](projects/03-scalable-backend/README.md) — Async transcoding pipeline, background workers, real-time status dashboard.
- **Project 4:** [Streaming Optimization](projects/04-streaming-optimization/README.md) — Nginx edge caching, `proxy_cache_lock`, HMAC signed URLs.

### ☁️ Phase 3: Cloud-Native (10K → 100K Users)
- **Project 5:** [Cloud-Native Emulator](projects/05-cloud-native-emulator/README.md) — S3 (MinIO), task queues (Redis/Celery), storage tiering.
- **Project 6:** [Chaos & Resilience](projects/06-chaos-and-resilience/README.md) — Circuit breakers, retry storms, idempotent workers, Pumba chaos testing.

### 🎥 Phase 4: Real-Time & Security (100K → 1M Users)
- **Project 7:** [Real-time Live Streaming](projects/07-live-streaming/README.md) — RTMP ingestion, live `.ts` generation, glass-to-glass latency.
- **Project 8:** [DRM & Content Protection](projects/08-drm-protection/README.md) — AES-128 segment encryption, key rotation, ClearKey license server.
- **Project 9:** [Ultra-Low Latency (WebRTC)](projects/09-webrtc-low-latency/README.md) — Sub-500ms P2P streaming, SDP negotiation, stateful scaling wall.

### 🧱 Phase 5: Service Mesh (1M+ Users)
- **Project 10:** [Microservices Migration](projects/10-microservices-migration/README.md) — Service isolation, API gateway, rate limiting, distributed tracing challenges.

---

## 🎬 The Streaming Pipeline (System Spine)

Everything in this repository serves **one goal**: get video segments from storage to the user's screen as fast and reliably as possible. HLS is the backbone.

### How HLS Works (End-to-End)

```mermaid
graph LR
    Upload["1. Upload (MP4)"] --> Transcode["2. Transcode (FFmpeg)"]
    Transcode --> Segment["3. Segment (.ts chunks)"]
    Segment --> Manifest["4. Manifest (.m3u8)"]
    Manifest --> CDN["5. CDN Edge Cache"]
    CDN --> ABR["6. ABR Switch (HLS.js)"]
    ABR --> Buffer["7. Buffer → Decode → Render"]
    
    style Segment fill:#4CAF50,stroke:#333,color:#fff
    style Manifest fill:#4CAF50,stroke:#333,color:#fff
    style ABR fill:#2196F3,stroke:#333,color:#fff
```

### Step-by-Step: The Life of a Video

```
1. RAW UPLOAD
   └─► User uploads sample.mp4 (H.264, 1080p, 2GB)
   └─► API returns 202 Accepted immediately (async processing)

2. TRANSCODE (FFmpeg, server-side)
   └─► 4 quality passes: 1080p@5Mbps / 720p@2.8Mbps / 480p@1.4Mbps / 360p@800kbps
   └─► Each pass uses -maxrate and -bufsize for constrained VBR
   └─► Output: 4 streams × ~200 segments each = ~800 .ts files
   └─► Duration: ~8 min on 4-core VM (bottleneck at scale)

3. SEGMENT (.ts chunk lifecycle)
   └─► Each .ts = exactly 6 seconds of muxed H.264 video + AAC audio
   └─► Segment sizes: 360p=0.7MB, 480p=1.1MB, 720p=2.2MB, 1080p=3.8MB
   └─► Naming: /ab/c4/{video_id}/720p/seg_047.ts (hash-prefix for S3 IOPS)
   └─► Lifecycle: HOT (7 days, SSD) → WARM (90 days, IA) → COLD (Glacier)

4. MANIFEST (.m3u8 playlist generation)
   └─► master.m3u8 (Master Playlist):
       │  #EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
       │  1080p/playlist.m3u8
       │  #EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720
       │  720p/playlist.m3u8
   └─► 720p/playlist.m3u8 (Media Playlist):
       │  #EXT-X-TARGETDURATION:6
       │  #EXTINF:6.0,
       │  seg_000.ts
       │  #EXTINF:6.0,
       │  seg_001.ts
   └─► For DRM: #EXT-X-KEY:METHOD=AES-128,URI="/api/key/{video_id}"

5. ABR SWITCHING (client-side, HLS.js decision engine)
   └─► Startup: always loads lowest quality first (TTFF < 1.5s)
   └─► Bandwidth estimation: moving average of last 3 segment download speeds
   └─► Upgrade: if measured_bw > 2× next_level.bandwidth → switch up
   └─► Emergency drop: if buffer_seconds < 5 → immediately switch to lowest
   └─► Stability: max 3 quality switches per 60s (prevents flickering)
   └─► Hysteresis: won't downgrade unless bandwidth drops below 1.5× current level

6. PLAYER BUFFER STRATEGY
   └─► VOD: target 30s buffer (absorbs Wi-Fi jitter)
   └─► Live HLS: target 6s buffer (3 segments, minimizes broadcast delay)
   └─► WebRTC: 0s buffer (frame-by-frame, true real-time)
   └─► Rebuffer trigger: buffer < 2s → spinner shown
   └─► Idle pause: buffer > 30s → stop downloading (save bandwidth)

7. DECODE → RENDER
   └─► .ts demuxed → H.264 NALUs + AAC frames
   └─► Hardware decode (GPU) or software decode (CPU fallback)
   └─► Rendered to <video> element at display refresh rate
```

---

## 🔄 System Architecture & Data Flow

### Upload Flow (Ingest)

```mermaid
graph LR
    Client[Client App] -->|"POST /upload (SYNC)"| GW[API Gateway]
    GW -->|"Auth Check (SYNC)"| Auth[Auth Service]
    GW -->|"Store Raw (SYNC)"| S3[(Object Storage)]
    S3 -.->|"Event (ASYNC)"| Queue[Redis Task Queue]
    Queue -.->|"Dequeue (ASYNC)"| Worker["Transcoder ⚠️ BOTTLENECK"]
    Worker -->|"FFmpeg → .ts + .m3u8"| Worker
    Worker -->|"PUT segments"| S3cdn[(CDN Storage)]
    Worker -->|"Update status"| DB[(Catalog DB)]
    
    style Worker fill:#ff6b6b,stroke:#333,color:#fff
```

### Playback Flow (Egress)

```mermaid
graph LR
    Player[HLS.js Player] -->|"GET master.m3u8 (SYNC)"| CDN[CDN Edge]
    CDN -->|"Cache HIT → 0ms"| Player
    CDN -->|"Cache MISS"| Origin["Origin ⚠️ PROTECT THIS"]
    Origin -->|"Signed URL Check"| Auth[Auth Service]
    Origin -->|"Fetch .ts"| S3[(Object Storage)]
    S3 -->|"seg_047.ts"| Origin
    Origin -->|"Cache + Respond"| CDN
    CDN -->|"seg_047.ts → buffer"| Player
    Player -->|"ABR: measure bw → pick quality"| Player
    
    style Origin fill:#ff6b6b,stroke:#333,color:#fff
```

> **Solid lines** = synchronous (user waits). **Dashed lines** = asynchronous (background).

---

## 📊 Scale, Reliability & Performance

### Quantitative Pressure Model

| Scale | Users | Upload RPS | Playback RPS | DB CPU | Transcode Queue | Breaking Symptom |
|---|---|---|---|---|---|---|
| **Prototype** | 10 | 1/s | 10/s | 5% | 0 | Nothing breaks |
| **Launch** | 1,000 | 10/s | 500/s | 25% | 2-3 jobs | TTFB > 800ms on cold starts |
| **Growth** | 10,000 | 50/s | 5,000/s | 65% | 15-20 jobs | Upload latency > 2.8s |
| **Viral** | 100,000 | 200/s | 50,000/s | 85% | 200+ jobs | DB lock contention. 502s at 3% |
| **Scale** | 1,000,000 | 500/s | 200,000/s | Sharded | Distributed | Single-region CDN saturates |
| **Global** | 10,000,000+ | 2,000/s | 1,000,000/s | Multi-region | Multi-region | Requires geo-routing |

### Operational Baseline (SLIs / SLOs)

| SLI | SLO Target | P95 | P99 | Alert (PagerDuty) | Measurement |
|---|---|---|---|---|---|
| **Availability** | **99.9%** (8.7h downtime/year) | — | — | < 99.5% over 1h window | Synthetic uptime probe |
| Stream startup | < 2.0s | 1.4s | 2.8s | p95 > 3.0s | Client beacon |
| Rebuffer ratio | < 0.5% | 0.3% | 0.8% | > 1.0% | Client beacon |
| API latency | < 200ms | 120ms | 280ms | p99 > 500ms | Nginx access log |
| Segment fetch (CDN) | < 100ms | 60ms | 150ms | p99 > 300ms | CDN edge log |
| Upload success | > 99.5% | — | — | < 98% | API 2xx ratio |
| CDN cache hit | > 95% | — | — | < 90% | `$upstream_cache_status` |

### Reliability & Resilience Patterns

| Pattern | Where | Behavior |
|---|---|---|
| Exponential backoff | Worker → S3 | 0s → 2s → 4s → 8s → Dead Letter Queue |
| Circuit breaker | Worker → MinIO | Open after 5 failures/60s. Probe every 30s |
| Idempotent workers | Celery tasks | `IF EXISTS output → skip` (no duplicate .ts files) |
| Rate limiting | Nginx gateway | 50 req/s per IP, 5 uploads/min per user |
| Request collapsing | Nginx proxy_cache | `proxy_cache_lock on` (1 origin fetch per segment) |
| Graceful degradation | DRM key server | If key vault down → serve 480p unencrypted |

---

## 💰 Economics & Cost at Scale

### Monthly Infrastructure Cost

| Scale | Compute | Storage | CDN Egress | Transcode | Total/month | Per-User |
|---|---|---|---|---|---|---|
| 1K | $50 | $12 | $30 | $10 | **$102** | $0.102 |
| 10K | $200 | $120 | $300 | $80 | **$700** | $0.070 |
| 100K | $800 | $500 | $3,000 | $400 | **$4,700** | $0.047 |
| 1M | $5,000 | $2,500 | $23,000 | $3,000 | **$33,500** | $0.034 |
| 10M | $30,000 | $15,000 | $180,000 | $20,000 | **$245,000** | $0.025 |

### Cost Breakdown & Optimization

```
WHERE THE MONEY GOES (at 100K users):
  CDN Egress:     64%  ← #1 COST DRIVER (every .ts served = bandwidth bill)
  Compute:        17%  (API servers + transcoder workers)
  Storage:        11%  (4 quality levels × all videos × 3 tiers)
  Transcoding:     8%  (FFmpeg CPU hours — grows linearly with uploads)

STORAGE TIERING (applied in Project 5):
  HOT  (S3 Standard, SSD):   last 7 days     → $0.023/GB/month
  WARM (S3 IA, HDD):         8-90 days       → $0.0125/GB/month
  COLD (S3 Glacier):         >90 days        → $0.004/GB/month
  At 52TB total: all-hot = $1,196/mo → tiered = $484/mo (60% savings)
```

---

## 🌍 Hyperscale: 100M+ Users (The Netflix Problem)

At **100 million monthly active users** with **10 million concurrent streams**, the system faces challenges that no single architecture can solve:

| Problem | Solution | Implementation |
|---|---|---|
| CDN single point of failure | **Multi-CDN strategy** | Route via Cloudflare primary, Akamai failover. DNS-level health checks switch in <30s |
| Regional S3 outage | **Cross-region replication** | S3 CRR to 3 regions. Read replica promotion in <60s |
| Geographic latency | **Geo-routing** | Route53/Cloudflare geo-DNS sends users to nearest edge. Latency-based routing |
| Viral traffic spike | **Edge transcoding** | Pre-position popular content at edge. Transcode at edge for <1s startup |
| Regional outage | **Failover regions** | Active-active in 3 regions. If us-east-1 fails, eu-west-1 absorbs traffic in <60s |

---

## ⚖️ Trade-offs & Deep Dives

### Architecture Trade-off Comparisons

| Dimension | Monolith (Phase 2) | Microservices (Phase 5) |
|---|---|---|
| Deployment speed | 1 binary, 1 deploy | 4+ services, independent deploys |
| Debug complexity | Stack trace → root cause | Distributed trace across 4 services |
| Latency | In-process function call (0ms) | Network hop per service (2-10ms each) |
| **When to use** | **< 10 engineers, < 100K users** | **> 10 engineers, > 1M users** |

### FAQ & Common Mistakes

**Q: Why 6-second segments instead of 2?**
A: 6s segments reduce CDN request volume by 3× (83% fewer requests). For VOD, the startup penalty is acceptable. Live uses 2s when latency matters.

**Q: Why HLS and not DASH?**
A: HLS has universal browser support (including iOS Safari). DASH requires dash.js and has no Safari support without MSE workarounds.

| Mistake | Why It Fails | Fix |
|---|---|---|
| Transcoding in the handler | Request times out at 30s | Use async queue (Redis + Celery) |
| No CDN, serving from origin | Origin crashes at 1,000 viewers | Add Nginx cache or CDN edge |
| Single quality level | 3G users buffer forever | Implement ABR with 4 quality levels |

### 🎯 System Design Interview Questions (This Repo Answers)

1. **Design a video streaming platform like Netflix** → Full repo walkthrough
2. **How does adaptive bitrate streaming work?** → [Streaming Internals](docs/streaming-internals.md#2-adaptive-bitrate-abr-switching-logic)
3. **How would you handle a thundering herd at CDN?** → [Failure Modeling](docs/failure-modeling.md#f3-cdn-cache-miss--request-collapsing)
4. **Design for 100M users** → [Hyperscale Guide](docs/hyperscale.md)

---

## 🛠️ Repository & Tech Stack

### Repository Structure

```
videostreaming/
├── docs/                              # Engineering deep-dives
├── projects/
│   ├── 01-basic-streaming-server/     # Range Requests, 206 Partial Content
│   ├── 02-build-your-own-hls/         # .ts segmentation, .m3u8, ABR
│   ├── ...                            # (See Roadmap for details)
│   └── 10-microservices-migration/    # Service mesh, API gateway
└── samples/                           # Raw media assets
```

### Tech Stack
- **Streaming:** FFmpeg, HLS.js, Nginx-RTMP, Aiortc (WebRTC)
- **Backend:** Node.js, Python (FastAPI), Celery
- **Storage:** Local FS, MinIO (S3-compatible), Redis
- **Infra:** Docker, Nginx (reverse proxy + edge cache), Pumba (chaos)

### Production Readiness Checklist

| Category | Requirement | Status |
|---|---|---|
| **Streaming** | HLS segmentation (.ts + .m3u8) with 4-level ABR | ✅ Implemented |
| **Resilience** | Exponential backoff + DLQ | ✅ Implemented |
| **Security** | Rate limiting (per-IP + per-route) | ✅ Implemented |
| **Ops** | SLO targets defined (99.9%) | 📋 Documented |
| **Cost** | Storage tiering (hot/warm/cold) | 📋 Documented |
