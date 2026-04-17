# 🛠️ Mastering FFmpeg: The Video Engineer's Field Manual

FFmpeg is the "Swiss Army Knife" of the streaming world. In this repository, we used it for everything from simple playback to complex cloud encryption.

---

## 🏗️ Core Concept: The Pipeline
FFmpeg works as a stream processor:
`Input (File/Stream) -> Demuxer -> Decoder -> Filter -> Encoder -> Muxer -> Output`

---

## 📂 Command Breakdown

### 1. HLS/ABR Generation (Project 2 & 3)
Used to chop video into adaptive segments.
```bash
ffmpeg -i input.mp4 \
  -vcodec libx264 -acodec aac \
  -s 1280x720 -b:v 2000k \
  -hls_time 10 -hls_list_size 0 \
  -f hls playlist.m3u8
```
- `-hls_time 10`: Cuts the video into 10-second segments.
- `-f hls`: Tells FFmpeg to output in HTTP Live Streaming format.

### 2. Signing & Encryption (Project 8)
Used for DRM (Digital Rights Management).
```bash
ffmpeg -i input.mp4 \
  -hls_key_info_file vault/key_info.txt \
  -f hls encrypted.m3u8
```
- `-hls_key_info_file`: Injects an AES-128 encryption key into every segment.

### 3. Real-Time Simulation (Project 7 & 9)
Used to simulate a live camera feed.
```bash
ffmpeg -re -i input.mp4 -f flv rtmp://server/live
```
- `-re`: (Real-time) Forces FFmpeg to read the file at its native frame rate. Without this, FFmpeg would finish a 1-hour video in 1 minute.
- `-f flv`: The format required for RTMP ingestion.

---

## 💡 Top 3 Pro Tips
1. **Copying instead of Re-encoding:** Using `-c copy` skips the heavy CPU work if the codecs are already correct.
2. **The `q` key:** While running FFmpeg in a terminal, press `q` to stop gracefully and save the file headers.
3. **Probe before you process:** Use `ffprobe -v error -show_format input.mp4` to see what's inside a file before you try to transcode it.

---

[Back to Roadmap](../README.md)
