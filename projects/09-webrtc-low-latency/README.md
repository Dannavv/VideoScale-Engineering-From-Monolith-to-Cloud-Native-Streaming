# Project 9: Ultra-Low Latency (WebRTC)

## 🚀 The Goal
Achieve near-instantaneous video delivery (<500ms delay), moving beyond the limitations of segment-based streaming (HLS/DASH).

## 😰 The Problem
Even with 3-second segments (Project 7), HLS has a significant delay because the browser has to download a full file before playing. For interactivity (Talk shows, Gambling, Gaming), 10 seconds of lag is unacceptable.

## 💡 The Solution: WebRTC (Real-Time Communication)
WebRTC doesn't use "files." It uses **UDP/SRTP** to send raw video frames directly to the player as soon as they are captured.

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as Signaling Server
    participant M as Media Server (Aiortc)
    B->>S: Send Offer (SDP)
    S->>M: Forward Offer
    M->>M: Attach Video Track
    M->>S: Send Answer (SDP)
    S-->>B: Forward Answer
    B<->>M: Direct UDP Media Stream
```

### 🧠 Systems Thinking: The Challenge of Stateful Scaling
- **The Problem:** Unlike HLS, where any server can serve any chunk, WebRTC creates a **Long-Lived Stateful Connection**.
- **The Scalability Wall:** If you have 10,000 users, you need 10,000 open UDP ports and constant CPU usage to encrypt the stream for each individual user. This is why WebRTC is far more expensive to scale than traditional HLS.

## 😰 The Breaking Point
At **1,000 concurrent viewers**, a single WebRTC Media Server (like this Aiortc instance) will hit 100% CPU. In HLS, the server just hands out files. In WebRTC, the server has to **constantly encrypt and package** every single frame for every single user in real-time.

## ⚖️ Architecture Trade-offs
- **Pro:** Ultra-Low Latency (<500ms). Perfect for auctions, gambling, or interactive gaming.
- **Con (The Cost):** WebRTC is 10x-50x more expensive to scale than HLS. You cannot cache WebRTC on a CDN; every stream is a "Direct Phone Call" to your server.
- **Con (Network Stability):** Because it uses UDP, packets are lost. At high scale, if the network jitters, the video will "tear" or artifact, whereas HLS would simply buffer.

## 🎓 Key Takeaway
**WebRTC is "Stateful" and "Real-Time."** Unlike HLS which is "Best Effort," WebRTC is "Instant Effort," sacrificing some quality to ensure zero delay.

---

## 📊 Phase Constraints

| Metric | HLS (Project 7) | WebRTC (This Project) |
|---|---|---|
| Glass-to-glass latency | 6-18 seconds | < 500ms |
| Max viewers/server | 100,000+ (cached .ts) | ~500 (stateful UDP) |
| CDN cacheable | ✅ (static .ts files) | ❌ (unique per-user stream) |
| Network protocol | TCP (reliable, ordered) | UDP (fast, lossy) |
| Cost per 1K viewers/hour | $0.50 (CDN cached) | $25 (server CPU per user) |
| Seek support | ✅ Full timeline | ❌ Live only |

## 🎬 Role in the Streaming Pipeline

```
THIS PROJECT:  [9. REAL-TIME DELIVERY]
                    │
  Standard path: Upload → Transcode → .ts → CDN → HLS.js (6-18s delay)
                                                        │
  WebRTC path:   Camera → ──► MEDIA SERVER (aiortc) → UDP/SRTP → Browser (<500ms)
                              ^^^^^^^^^^^^^^^^^^^^^^
                              You are here.

This project REPLACES the HLS pipeline for real-time use cases:
  Auctions, gambling, interactive gaming, video calls
  Where 6 seconds of delay = unacceptable

BUT: it cannot replace HLS for VOD. Different tool, different job.
```

## 📈 Production Dashboard (What You'd Monitor)

| Metric | Healthy | Degraded | Critical |
|---|---|---|---|
| Active WebRTC sessions | < 500/server | 500-800 | > 800 (CPU saturated) |
| CPU per session | < 0.2% | 0.2-0.5% | > 0.5% (needs scaling) |
| Packet loss rate | < 1% | 1-5% | > 5% (video artifacts visible) |
| ICE connection time | < 2s | 2-5s | > 5s (NAT traversal issues) |
| Jitter buffer delay | < 50ms | 50-200ms | > 200ms (defeats purpose) |

## 💰 Cost Impact (WebRTC is EXPENSIVE)

```
HLS at 10K viewers:
  CDN serves cached .ts files
  Server load: ~0 (CDN handles everything)
  Cost: $5/hour

WebRTC at 10K viewers:
  Server must encrypt + packetize + send to EACH user
  Server load: 10,000 active UDP sessions × 0.2% CPU each = 20 full cores
  Cost: $250/hour (50× more expensive than HLS)

WHEN TO USE WEBRTC:
  ✅ Latency < 1 second is REQUIRED (auctions, gambling)
  ✅ Audience < 10,000 concurrent (cost-manageable)
  ❌ Large audience + few seconds delay acceptable → use HLS instead
```

---

## 🚀 How to Run
```bash
docker-compose up -d --build
```
👉 **Real-Time Studio: http://localhost:8089**

**Read Next:** [Project 10: Microservices](../10-microservices-migration/README.md) — Service isolation at scale | [Hyperscale Guide](../../docs/hyperscale.md) | [Back to Roadmap](../../README.md)
