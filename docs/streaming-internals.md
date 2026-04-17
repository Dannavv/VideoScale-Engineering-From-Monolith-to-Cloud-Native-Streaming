# 🎬 Streaming Internals: HLS Pipeline, ABR, & Client Buffering

This document covers the **core streaming mechanics** that separate a "file server" from a "streaming platform." These are the internals that Netflix, YouTube, and Twitch operate at scale.

---

## 1. The HLS Segmentation Pipeline

### How a Single Upload Becomes a Streamable Asset

```
RAW UPLOAD (2GB MP4, H.264, 1080p, 60fps)
  │
  ├──► FFmpeg Pass 1: Transcode to 1080p @ 5000kbps  → /output/1080p/
  ├──► FFmpeg Pass 2: Transcode to 720p  @ 2800kbps  → /output/720p/
  ├──► FFmpeg Pass 3: Transcode to 480p  @ 1400kbps  → /output/480p/
  └──► FFmpeg Pass 4: Transcode to 360p  @ 800kbps   → /output/360p/
         │
         ▼
   Each Pass Segments into 6-second `.ts` Chunks
         │
         ├── segment_000.ts (6s of video)
         ├── segment_001.ts (6s of video)
         ├── segment_002.ts (6s of video)
         └── ...
         │
         ▼
   Media Playlist (.m3u8) Generated Per Quality
         │
         ▼
   Master Playlist (.m3u8) Links All Qualities
```

### The FFmpeg Command (Exact)

```bash
ffmpeg -i input.mp4 \
  -filter_complex "[0:v]split=4[v1][v2][v3][v4]; \
    [v1]scale=1920:1080[v1out]; \
    [v2]scale=1280:720[v2out]; \
    [v3]scale=854:480[v3out]; \
    [v4]scale=640:360[v4out]" \
  -map "[v1out]" -c:v:0 libx264 -b:v:0 5000k -maxrate:v:0 5350k -bufsize:v:0 7500k \
  -map "[v2out]" -c:v:1 libx264 -b:v:1 2800k -maxrate:v:1 2996k -bufsize:v:1 4200k \
  -map "[v3out]" -c:v:2 libx264 -b:v:2 1400k -maxrate:v:2 1498k -bufsize:v:2 2100k \
  -map "[v4out]" -c:v:3 libx264 -b:v:3 800k  -maxrate:v:3 856k  -bufsize:v:3 1200k \
  -map a:0 -c:a aac -b:a 128k -ac 2 \
  -f hls -hls_time 6 -hls_playlist_type vod \
  -hls_segment_filename "stream_%v/segment_%03d.ts" \
  -master_pl_name master.m3u8 \
  -var_stream_map "v:0,a:0 v:1,a:0 v:2,a:0 v:3,a:0" \
  stream_%v/playlist.m3u8
```

### What Each Parameter Does

| Parameter | Purpose | Impact If Wrong |
|---|---|---|
| `-hls_time 6` | Segment duration in seconds | Too short (1s) = CDN request storm. Too long (30s) = high seek latency |
| `-bufsize` | Rate control buffer | Too small = bitrate spikes. Too large = quality fluctuates |
| `-maxrate` | Ceiling bitrate | Prevents spikes that overwhelm mobile bandwidth |
| `-hls_playlist_type vod` | Signals player this is not live | Player pre-fetches aggressively |

---

## 2. Adaptive Bitrate (ABR) Switching Logic

### How the Client Decides Quality

The player (HLS.js) continuously measures **3 signals** to decide which quality to stream:

```
┌──────────────────────────────────────────────────┐
│           ABR Decision Engine (Client-Side)       │
│                                                   │
│  Signal 1: Estimated Bandwidth                    │
│    └─► Moving average of last 3 segment downloads │
│    └─► Example: Downloaded 480p segment (700KB)   │
│         in 200ms = 3.5 Mbps effective bandwidth   │
│                                                   │
│  Signal 2: Buffer Health                          │
│    └─► Current seconds of video buffered ahead    │
│    └─► If buffer < 5s  → Drop quality immediately │
│    └─► If buffer > 30s → Try upgrading quality    │
│                                                   │
│  Signal 3: Playback Stability                     │
│    └─► Number of quality switches in last 60s     │
│    └─► If switches > 3 → Lock current quality     │
│                                                   │
│  OUTPUT: Next segment quality level (0-3)         │
└──────────────────────────────────────────────────┘
```

### ABR Quality Map

| Level | Resolution | Bitrate | Min Required Bandwidth | Target Device |
|---|---|---|---|---|
| 0 | 360p | 800 kbps | 1.0 Mbps | 3G Mobile |
| 1 | 480p | 1400 kbps | 1.8 Mbps | 4G Mobile |
| 2 | 720p | 2800 kbps | 3.5 Mbps | Wi-Fi Tablet |
| 3 | 1080p | 5000 kbps | 6.5 Mbps | Desktop Fiber |

### The "Startup Penalty"

Players always start at the **lowest quality** and ramp up over 3-5 segments. This ensures:
- **Time-to-First-Frame (TTFF)** < 1.5 seconds
- No initial buffering on slow networks
- Gradual visual improvement ("Netflix warmup" effect)

### Actual .m3u8 Manifest (What the Player Parses)

**Master Playlist (`master.m3u8`):**
```
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080,CODECS="avc1.640028,mp4a.40.2"
1080p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720,CODECS="avc1.4d401f,mp4a.40.2"
720p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=854x480,CODECS="avc1.4d401e,mp4a.40.2"
480p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360,CODECS="avc1.42e00a,mp4a.40.2"
360p/playlist.m3u8
```

**Media Playlist (`720p/playlist.m3u8`):**
```
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:6
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-PLAYLIST-TYPE:VOD
#EXTINF:6.006,
segment_000.ts
#EXTINF:6.006,
segment_001.ts
#EXTINF:6.006,
segment_002.ts
#EXTINF:4.838,
segment_199.ts
#EXT-X-ENDLIST
```

**DRM-Encrypted Variant (adds `EXT-X-KEY`):**
```
#EXTM3U
#EXT-X-KEY:METHOD=AES-128,URI="https://api.example.com/key/video_abc123",IV=0x00000000000000000000000000000001
#EXTINF:6.006,
segment_000.ts
```

### ABR Hysteresis (Prevents Quality Flickering)

```
RULE 1: Upgrade requires 2× headroom
  Current: 720p (needs 3.5 Mbps)
  Measured bandwidth: 7.2 Mbps (> 2 × 3.5 = 7.0)
  → UPGRADE to 1080p ✅

RULE 2: Downgrade threshold is lower (1.5×)
  Current: 1080p (needs 6.5 Mbps)
  Measured bandwidth: 8.0 Mbps (> 1.5 × 6.5 = 9.75? NO)
  Measured bandwidth: 5.0 Mbps (< 6.5 Mbps)
  → DOWNGRADE to 720p ⚠️

RULE 3: Max 3 switches per 60 seconds
  If player has already switched 3 times in the last minute
  → LOCK current quality for remaining window

RULE 4: Emergency drop overrides all rules
  If buffer_seconds < 2.0
  → Immediately drop to level 0 (360p), ignore hysteresis
```

---

## 3. Client-Side Buffering Strategy

### Buffer State Machine

```
┌───────────┐    Buffer < 2s    ┌────────────┐
│  PLAYING  │──────────────────►│  BUFFERING │
│  (Normal) │                   │  (Spinner) │
└─────┬─────┘                   └──────┬─────┘
      │                                │
      │ Buffer > 30s                   │ Buffer > 5s
      ▼                                ▼
┌───────────┐                   ┌────────────┐
│  IDLE     │                   │  PLAYING   │
│(Pause DL) │                   │  (Resume)  │
└───────────┘                   └────────────┘
```

### Buffer Sizing Strategy

| Scenario | Buffer Target | Rationale |
|---|---|---|
| VOD (Desktop) | 30 seconds | Absorb Wi-Fi jitter without rebuffering |
| VOD (Mobile) | 15 seconds | Balance RAM usage vs. smoothness |
| Live (HLS) | 6 seconds (3 segments) | Minimize broadcast delay |
| Live (WebRTC) | 0 seconds (frame-by-frame) | True real-time, no buffer |

### The "Rebuffer Ratio" KPI

**Target: < 0.5% of total watch time** spent buffering.

```
Rebuffer Ratio = (Total Buffering Time / Total Watch Time) × 100

Example:
- User watches 60 minutes
- Experienced 15 seconds of spinner
- Rebuffer Ratio = (15 / 3600) × 100 = 0.42% ← ACCEPTABLE

If Rebuffer Ratio > 1.0% → User churn increases by 20%
```

---

## 4. Segment Delivery Economics

### Cost Per Viewer Per Hour

| Quality | Bitrate | Data/Hour | S3 Egress Cost ($0.09/GB) | CDN Cost ($0.02/GB) |
|---|---|---|---|---|
| 360p | 800 kbps | 0.36 GB | $0.032 | $0.007 |
| 720p | 2800 kbps | 1.26 GB | $0.113 | $0.025 |
| 1080p | 5000 kbps | 2.25 GB | $0.202 | $0.045 |

### The CDN Cache-Hit Math

```
Without CDN: 100K viewers × 2.25 GB/hr × $0.09 = $20,250/hour
With CDN (95% hit rate): Only 5K origin fetches → $1,012 + CDN fee $4,500 = $5,512/hour
Savings: 73% cost reduction
```

---

[Back to Roadmap](../README.md) | [FFmpeg Commands](ffmpeg-mastery.md) | [Failure Modeling](failure-modeling.md)
