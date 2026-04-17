# Project 4: Streaming Optimization (Cache & Security)

## 🎯 The Goal
Take your scalable backend and make it **Production Ready** by adding a caching layer and protecting your content with **Signed URLs**.

### Why Optimization matters:
1. **The Thundering Herd:** If 10,000 users request the same 2-second HLS segment, your FastAPI backend will die. We use Nginx (acting as a basic CDN) to cache that segment at the "edge."
2. **Piracy & Bandwidth Theft:** Without Signed URLs, anyone can copy your `.m3u8` link and embed it on their own site, stealing your bandwidth.

---

## 🛠️ Concepts
- **Reverse Proxy Caching:** Nginx intercepts requests for `.ts` files and serves them from its own memory/disk instead of hitting the backend.
- **Signed URLs (HMAC):** A URL that contains an expiration timestamp and a cryptographic signature. The server (Nginx or Backend) only fulfills the request if the signature is valid.
- **Cache Hit Ratio:** The percentage of requests served from cache vs reaching the origin.

---

## 🏗️ Architecture
- **Proxy/Cache:** Nginx
- **Backend:** Python (to generate signatures)
- **Token Logic:** HMAC-SHA256

---

## 🚀 How to Run

### 1. View the Nginx Config
Look at `nginx/nginx.conf` to see how we define the `proxy_cache` path and keys.

### 2. Run the Optimization Stack
```bash
docker-compose up -d --build
```

### 3. Open the Dashboard
Access the lab via **Nginx** (which handles the caching):
👉 **http://localhost:8084**

### 4. Test Security (Optional)
You can also run the logic script directly to see how tokens are calculated:
```bash
python3 app/main.py
```

---

[Back to Roadmap](../../README.md)
