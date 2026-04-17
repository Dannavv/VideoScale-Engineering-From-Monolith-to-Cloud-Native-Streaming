# Project 1: Basic Video Streaming Server

## 🚀 The Goal
Understand the "Magic" of the `206 Partial Content` status code and how browsers request specific byte ranges.

## 😰 The Problem
If you serve a 2GB video file via a standard `GET` request, the browser would have to download a significant portion before it could even seek to the middle. If a user only watches 30 seconds, you've wasted massive bandwidth.

## 💡 The Solution: HTTP Range Requests
The server detects a `Range` header and streams only the requested bytes.

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as Server
    B->>S: GET /video.mp4 (Range: bytes=0-1024)
    S-->>B: 206 Partial Content (Bytes 0-1024)
    B->>S: GET /video.mp4 (Range: bytes=1024-)
    S-->>B: 206 Partial Content (Next Chunks)
```

---

## 🚀 How to Run

### Why not just use a standard file download?
If you serve a 2GB video file via a standard `GET` request, the browser would have to download a significant portion before it could even seek to the middle. If a user only watches 30 seconds, you've wasted massive bandwidth.

### What we are building:
A Node.js server that can:
1. Detect `Range` headers from the browser.
2. Calculate the start and end bytes.
3. Stream only that chunk using `fs.createReadStream`.

---

## 🛠️ Architecture
- **Language:** JavaScript (Node.js)
- **Library:** Express (or built-in `http` module for "hard mode")
- **Storage:** Local `videos/` folder

---

## 🧪 Key Learnings
1. **Status Code 206:** What "Partial Content" means.
2. **Content-Range Header:** How to tell the browser "Here is bytes 500-1000 of 9000".
3. **Buffering:** How the browser decides how much to pre-fetch.

---

## 🚀 Getting Started

### 1. Preparation
Place an MP4 file named `sample1.mp4` in the root `samples/` directory of the repository.

### 2. Install & Start
```bash
npm install
npm start
```

### 3. Access on Desktop
Open `http://localhost:3000` in your browser.

### 4. Access on Mobile (Phone/Tablet)
To test the "Real World" experience on a mobile device:
1. Ensure your phone and computer are on the **same Wi-Fi**.
2. Find your computer's **Local IP address**.
3. Open the browser on your phone and go to: `http://<YOUR_LOCAL_IP>:3000`
   *(Example: http://192.168.1.5:3000)*
4. Experiment with seeking and notice how the browser handles buffering differently on mobile networks.

[Back to Roadmap](../../README.md)
