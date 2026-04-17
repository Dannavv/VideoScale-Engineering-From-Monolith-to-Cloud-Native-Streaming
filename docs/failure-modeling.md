# 🐜 System Failure Modeling & Mitigation

In a production streaming environment, **Failure is NOT an Option—it is a Certainty.** This document outlines how VideoScale handles common distributed system failures.

---

## 🏗️ 1. Transcoding Pipeline Failures
**Scenario:** The worker crashes mid-FFmpeg process (e.g., OOM or Node restart).
- **The Risk:** Zombie files in S3 and "Stalled" status in the UI.
- **Mitigation:** 
    - **Lease Pattern:** Workers "lock" a task with a TTL. If the worker dies, the lock expires and the task returns to the Redis/SQS queue for another worker to grab.
    - **Atomic Uploads:** Always upload to a `.tmp` file and perform an atomic `RENAME` (S3 Copy) only after FFmpeg exits with code 0.

## ❄️ 2. CDN & Edge Failures
**Scenario:** A massive "Thundering Herd" hits a fresh segment that isn't cached yet.
- **The Risk:** Origin backend meltdown (FastAPI crashes).
- **Mitigation:**
    - **Request Collapsing:** Ensuring that only 1 request goes to the origin for a specific segment, while others wait for the cache to populate.
    - **Stale-While-Revalidate:** Serving the previous quality segment if the origin is too slow to provide the new one.

## 🔐 3. Security & Auth Failures
**Scenario:** The Key License Server (DRM) is under Ddos or down.
- **The Risk:** Total blackout for all paying users.
- **Mitigation:**
    - **Key-Caching:** Using short-lived, encrypted local caches in the client or Edge.
    - **Graceful Degradation:** Temporarily allowing low-resolution (non-DRM) playback if the DRM vault is unreachable.

## 📊 4. Database & Consistency Failures
**Scenario:** The Auth service DB is in a Read-Only state during a failover.
- **The Risk:** Users can't log in or watch videos.
- **Mitigation:**
    - **Eventual Consistency:** Relying on signed JWT tokens that don't require a DB lookup for every single segment request.

---

[Back to Roadmap](../README.md)
