# 🧠 Phase 0: The Mental Model

Video streaming isn't just "sending a file." It's a high-performance orchestration of data transformation and delivery. To build for a billion users, you must first understand the life of a video packet.

## 🔄 The Video Pipeline

Every major platform (YouTube, Netflix, Twitch) follows this fundamental flow:

### 1. Capture
Raw data from a camera or screen. This is uncompressed and massive (Gbps range). It cannot be sent over the internet in this state.

### 2. Encode (Compression)
The raw data is compressed using **Codecs** (like H.264, H.265/HEVC, AV1). 
- **Goal:** Throw away data the human eye won't notice to save bandwidth.

### 3. Store (Ingest)
The encoded file is uploaded to a storage layer (Object Storage, like S3 or MinIO).

### 4. Process (Transcoding)
One video isn't enough. You need **Transcoding**:
- **Multiplexing:** Creating different resolutions (360p, 720p, 1080p, 4K).
- **Packaging:** Chopping videos into small segments (.ts or .m4s) for HLS/DASH.

### 5. Deliver (CDN)
The video segments are cached globally on **Content Delivery Networks**.
- Servers should be as close to the user as possible to reduce latency.

### 6. Play (Client)
The user's player (ExoPlayer, Video.js, AVPlayer) requests chunks as needed.
- **Adaptive Bitrate (ABR):** If the internet slows down, the player automatically switches to a lower quality 360p chunk instead of buffering.

---

## 🛑 The Core Bottlenecks

1. **Latency:** The time from "Video starts" to "Pixel on screen."
2. **Throughput:** How much data can we push?
3. **Buffering:** What happens when the network stalls?
4. **Compute Cost:** Transcoding 4K video is expensive and slow.

## 🛠️ The Engineer's Toolkit
- **FFmpeg:** The "Swiss Army Knife" of video.
- **Protocols:** HTTP, RTMP, WebRTC, HLS, DASH.
- **Transcoding:** H.264 (AVC), H.265 (HEVC), AV1.
- **Storage:** S3, Pre-signed URLs.

---

[Next Step: Phase 1 - Basic Video Streaming Server](../projects/01-basic-streaming-server/README.md)
