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

## 🚀 How to Run
```bash
docker-compose up -d --build
```
👉 **Real-Time Studio: http://localhost:8089**

[Back to Roadmap](../../README.md) | [Read the Theory](../../docs/principles-and-architecture.md#project-9-ultra-low-latency-webrtc)
