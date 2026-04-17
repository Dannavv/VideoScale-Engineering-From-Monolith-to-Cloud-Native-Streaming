# Project 7: Real-Time Live Streaming

## 🚀 The Goal
Build a professional-grade "Live Studio" that can ingest a camera feed and broadcast it globally.

## 😰 The Problem
VOD (Video on Demand) is easy because the files already exist. In **Live**, every millisecond matters. We can't wait for a whole file to be encoded; we have to "stream" the stream.

## 💡 The Solution: RTMP to HLS Repackaging
We use **RTMP** (Real-Time Messaging Protocol) because it is incredibly fast for sending video from a camera to a server.
- The server (Nginx) receives the RTMP feed.
- It instantly converts the segments into HLS chunks.
- The browser "pulls" these chunks every 3 seconds.

## 🛠️ Implementation Idea
**Low-Latency HLS Tuning:**
We configure Nginx to use 3-second segments instead of the standard 10-second ones. This reduces the "Broadcast Delay" from 30 seconds down to under 10 seconds.

## 🎓 Key Takeaway
**Ingest with RTMP, Distribute with HLS.** RTMP is the industry standard for "pushing" the news; HLS is the standard for "viewing" it.

---

## 🚀 How to Run
```bash
docker-compose up -d --build
```
👉 **Live Studio: http://localhost:8087**

### To Start the Stream:
```bash
ffmpeg -re -i /home/thearp/projects/videostreaming/samples/sample1.mp4 -vcodec libx264 -acodec aac -f flv rtmp://localhost:1935/live/stream1
```

[Back to Roadmap](../../README.md) | [Read the Theory](../../docs/principles-and-architecture.md#7-rtmp-ingestion-project-7)
