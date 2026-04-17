# Project 9: Ultra-Low Latency (WebRTC)

## 🚀 The Goal
Achieve near-instantaneous video delivery (<500ms delay), moving beyond the limitations of segment-based streaming (HLS/DASH).

## 😰 The Problem
Even with 3-second segments (Project 7), HLS has a significant delay because the browser has to download a full file before playing. For interactivity (Talk shows, Gambling, Gaming), 10 seconds of lag is unacceptable.

## 💡 The Solution: WebRTC (Real-Time Communication)
WebRTC doesn't use "files." It uses **UDP/SRTP** to send raw video frames directly to the player as soon as they are captured.
1. **Signaling:** The server and the browser exchange "Handshakes" (SDP) to find each other.
2. **Hole Punching:** They bypass firewalls (ICE) to establish a direct link.
3. **Continuous Flow:** Video is sent as a steady stream of packets, not chunks.

## 🛠️ Implementation Idea
- **Python Broadcaster (Aiortc):** A server-side peer that reads a video file and "calls" the browser to stream it.
- **Socket.io Signaling:** A central meeting point for the server and client to exchange their "Connection Cards."

## 🎓 Key Takeaway
**WebRTC is "Stateful" and "Real-Time."** Unlike HLS which is "Best Effort," WebRTC is "Instant Effort," sacrificing some quality to ensure zero delay.

---

## 🚀 How to Run
```bash
docker-compose up -d --build
```
👉 **Real-Time Studio: http://localhost:8089**

[Back to Roadmap](../../README.md) | [Read the Theory](../../docs/principles-and-architecture.md#project-9-ultra-low-latency-webrtc)
