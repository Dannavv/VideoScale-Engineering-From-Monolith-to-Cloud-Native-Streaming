# Project 2: Build Your Own HLS (HTTP Live Streaming)

## 🎯 The Goal
Understand how modern streaming (YouTube, Netflix) works at scale. Instead of serving one large MP4, we break it into hundreds of small `.ts` chunks and a `.m3u8` playlist.

### Why HLS over progressive download?
1. **Adaptive Bitrate (ABR):** The player can switch between 480p and 1080p chunks mid-stream based on network speed.
2. **CDN Friendly:** Chunks are small, static files easily cached by edge servers.
3. **Live Streaming:** You can keep appending new chunks to a playlist for live broadcasts.

---

## 🛠️ The Workflow
1. **Centralized Source:** Uses the shared `samples/sample1.mp4` file.
2. **Processing:** The `encode.sh` script uses **FFmpeg** to generate 3 different quality variants (360p, 720p, 1080p).
3. **Packaging:** High-performance chunking into 2-second segments.
4. **ABR Manifest:** Generates a Master Playlist that links to all quality levels.

---

## 🧪 Key Learnings
1. **The Master Playlist (`.m3u8`):** How it describes bandwidth and resolution to the player.
2. **Segmenting:** Why we use `.ts` files and how they enable mid-stream quality switching.
3. **Player Logic:** How `hls.js` monitors network speed and picks the best chunk.

---

## 🚀 How to Run

### 1. Encode the Video
This will create the `output/` folder and generate the fragments.
```bash
cd scripts
./encode.sh
```

### 2. Install & Start Server
```bash
cd ..
npm install
npm start
```

### 3. Play & Observe
*   Open `http://localhost:3001` on your desktop.
*   Open `http://<YOUR_LOCAL_IP>:3001` on your phone.
*   **Watch the "Real-time Metrics"** at the bottom. Try throttling your network in Chrome DevTools (Network tab -> Throttling) to watch the ABR engine switch quality levels live.

---

[Back to Roadmap](../../README.md)
