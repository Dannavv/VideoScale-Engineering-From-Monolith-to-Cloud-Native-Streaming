# Project 10: Microservices Migration

## 🚀 The Goal
Transition from a "Distributed Monolith" to a truly decoupled **Microservices Ecosystem**.

## 😰 The Breaking Point
At **10M+ users**, the "Scalable Monolith" from Phase 2/3 begins to crack. While we have background workers, the **Deployment Velocity** slows down. Every time we want to update the "Auth" logic, we have to restart the "Transcoder" and "Catalog" logic because they are in the same code binary.

## 💡 The Solution: Service Isolation
We break the system into small, specialized apps (Auth, Catalog) that communicate over the network.

## ⚖️ Architecture Trade-offs
Moving to Microservices isn't "better"—it's a choice with heavy costs:
- **Pro:** Team A can update the Auth service without touching Team B's Catalog service.
- **Con (Network Latency):** A single user request now involves 3+ network hops (Gateway -> Auth -> DB).
- **Con (Observability):** Debugging a "500 Internal Server Error" now requires **Distributed Tracing** because the error could be in any of the 4 isolated containers.

```mermaid
graph TD
    User([User Browser]) -->|HTTP| GW[Nginx API Gateway]
    GW -->|/auth| AS[Auth Service]
    GW -->|/catalog| CS[Catalog Service]
    GW -->|/health| Monitor[Health Dashboard]
    
    AS --- Redis[(Redis Event Bus)]
    CS --- Redis
```

- **Gateway:** Route traffic based on URLs (e.g., `/auth` -> Auth Service).
- **Auth Service:** Responsible for only one thing: Identity.
- **Catalog Service:** Responsible for only one thing: Data.
- **Independence:** If the Auth service is undergoing maintenance, users can still browse the Catalog.

## 🛠️ Implementation Idea
- **Reverse Proxy (Nginx):** Acts as the single entry point.
- **Shared Event Bus (Redis):** Services talk to each other through messages, not direct calls (Async Decoupling).
- **Service Status Dashboard:** A central UI to monitor the "Pulse" of the entire cluster.

## 🎓 Key Takeaway
**Microservices is an organizational pattern as much as a technical one.** It allows teams to move fast, fail small, and scale independently.

---

## 🚀 How to Run
```bash
docker-compose up -d --build
```
👉 **System Dashboard: http://localhost:8010**

---

## 🧪 The Resilience Test (Chaos Simulation)
To truly understand the power of microservices, you must see the system survive a partial failure.

### 1. Kill the Catalog Service
Run this while the dashboard is open:
```bash
docker-compose stop catalog-service
```
**Observation:** The dashboard will show the Catalog Service turn **RED (UNREACHABLE)**, but the **Auth Service** stays **GREEN**. You can still log in! In a monolith, the whole site would be down.

### 2. Heal the System
Bring it back to life:
```bash
docker-compose start catalog-service
```
**Observation:** Within 3 seconds, the dashboard will detect the "Heartbeat" again and turn Green.

---

## 📊 Phase Constraints

| Metric | Monolith (Phase 2) | Microservices (This Phase) |
|---|---|---|
| Deployment frequency | 1× per week (shared binary) | 5× per day (per-service CI/CD) |
| Single-service failure | Entire system down | Only affected service down |
| Request latency (avg) | 5ms (in-process call) | 15-25ms (+network hop per service) |
| Debug time (root cause) | 10 min (single log file) | 30-60 min (distributed tracing required) |
| Team scalability | Merge conflicts at 5+ devs | Independent service ownership |
| Container count | 1 | 4+ (Gateway + Auth + Catalog + Workers) |

## 🎬 Role in the Streaming Pipeline

```
THIS PROJECT:  [10. SERVICE ISOLATION]
                    │
  ┌─────────────────────────────────────────────────────────────┐
  │            VIDEO STREAMING MICROSERVICE MESH                 │
  │                                                              │
  │  Upload ──► Gateway ──► Auth Service ──► Storage Service     │
  │                │                              │              │
  │                └──► Catalog Service   Worker Service (FFmpeg) │
  │                                        │                     │
  │                                   .ts + .m3u8 → CDN → Play  │
  └─────────────────────────────────────────────────────────────┘
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
       Each box is an independent container.
       Each can scale independently.
       Each can fail without killing the others.
```

## 📈 Production Dashboard (What You'd Monitor)

| Metric | Healthy | Degraded | Critical |
|---|---|---|---|
| Service health (per service) | ✅ All green | ⚠️ 1 service degraded | ❌ 2+ services down |
| Inter-service p99 latency | < 10ms | 10-50ms | > 100ms (network congestion) |
| Gateway error rate | < 0.1% | 0.1-1% | > 1% (routing failures) |
| Event bus (Redis) lag | < 100ms | 100-500ms | > 1s (services falling behind) |
| Distributed trace completion | > 99% | 95-99% | < 95% (missing spans) |
| Container restart count | 0 | 1-3/hour | > 5/hour (crash loop) |

## 💰 Cost Impact of Microservices

```
RESOURCE OVERHEAD:
  Each container: ~100MB RAM base overhead
  4 containers vs 1 monolith: +300MB RAM ($5/month)
  Network calls between services: +5-15ms latency per hop
  Observability stack (logging, tracing): +$50-200/month at scale

WHEN MICROSERVICES PAY OFF:
  At 3 engineers: Monolith is simpler and cheaper ← stay here
  At 10 engineers: Microservices let teams deploy independently
  At 50 engineers: Microservices are REQUIRED (merge conflicts become impossible)

TOTAL COST COMPARISON (at 100K users):
  Monolith:       $4,300/month (simple, but deployment velocity = slow)
  Microservices:  $4,800/month (+12% overhead, but 5× deployment frequency)
```

---

## 🚀 How to Run
```bash
docker-compose up -d --build
```
👉 **System Dashboard: http://localhost:8010**

**Read Next:** [Hyperscale Guide (100M users)](../../docs/hyperscale.md) — Multi-CDN, geo-routing, failover regions | [Cost Architecture](../../docs/cost-architecture.md) | [Back to Roadmap](../../README.md)
