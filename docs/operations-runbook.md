# 🔧 Operations Runbook: Observability, Autoscaling, & Cost Control

Production systems aren't "deployed." They are **operated.** This document defines how VideoScale is monitored, scaled, and kept within budget.

---

## 1. Observability Stack

### The Three Pillars

```
┌─────────────────────────────────────────────────────────┐
│                   OBSERVABILITY LAYER                    │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌───────────────────┐  │
│  │  METRICS  │    │   LOGS   │    │  DISTRIBUTED      │  │
│  │ (Numbers) │    │  (Text)  │    │  TRACES (Flows)   │  │
│  └────┬─────┘    └────┬─────┘    └────────┬──────────┘  │
│       │               │                   │              │
│  Prometheus       Fluentd/Loki        Jaeger/Zipkin     │
│  + Grafana        + Kibana            + OpenTelemetry   │
└───────┼───────────────┼───────────────────┼─────────────┘
        │               │                   │
        ▼               ▼                   ▼
   "What broke?"    "Why broke?"      "Where broke?"
```

### Critical Metrics Dashboard

| Metric | Source | Alert Threshold | Action |
|---|---|---|---|
| API p99 Latency | Nginx access logs | > 500ms | Scale API pods |
| Transcode Queue Depth | Redis `LLEN` | > 50 jobs | Scale workers |
| CDN Cache Hit Ratio | Nginx `$upstream_cache_status` | < 90% | Investigate miss patterns |
| S3 Error Rate (5xx) | MinIO health endpoint | > 0.1% | Trigger circuit breaker |
| Rebuffer Ratio | Client-side beacon | > 1.0% | Lower default quality |
| Active WebRTC Sessions | Aiortc connection count | > 800/server | Reject new connections |
| CPU Usage (Transcoder) | Docker stats | > 85% sustained 5min | Add worker container |
| Memory Usage (API) | Docker stats | > 75% | Investigate leaks |
| Disk I/O Wait | `iostat` | > 20% | Move hot files to SSD/cache |
| Upload Error Rate | API 4xx/5xx ratio | > 2% | Check storage connectivity |

### Log Levels Strategy

```
ERROR  → Immediate PagerDuty alert. System cannot serve a user.
         Example: "S3 PUT failed after 3 retries"

WARN   → Investigate within 1 hour. System is degraded but functional.
         Example: "Transcode took 45s (threshold: 30s)"

INFO   → Operational audit trail. Never alert on these.
         Example: "Video abc123 transcoded to 4 qualities in 22s"

DEBUG  → Disabled in production. Only enable for targeted investigation.
         Example: "HLS segment 047 generated, size=1.2MB, duration=6.003s"
```

---

## 2. Autoscaling Triggers

### Scaling Rules

| Component | Scale-Up Trigger | Scale-Down Trigger | Min Instances | Max Instances |
|---|---|---|---|---|
| API Gateway (Nginx) | RPS > 2,000/instance | RPS < 500/instance for 10min | 2 | 10 |
| Transcoder Workers | Queue depth > 20 | Queue depth = 0 for 5min | 1 | 20 |
| Auth Service | p99 latency > 100ms | p99 < 30ms for 15min | 2 | 6 |
| Catalog Service | p99 latency > 200ms | p99 < 50ms for 15min | 2 | 6 |
| WebRTC Media Servers | Active sessions > 500/server | Sessions < 100/server for 10min | 1 | 8 |

### Scaling Strategy Per Phase

```
Phase 1-2 (< 1K users):
  └─► Vertical scaling only. Bigger VM.
  └─► Cost: ~$50/month

Phase 3 (1K-100K users):
  └─► Horizontal scaling. Multiple API + Worker containers.
  └─► Auto-scale workers based on queue depth.
  └─► Cost: ~$500-2,000/month

Phase 4-5 (100K-1M+ users):
  └─► Multi-region deployment with geo-routing.
  └─► CDN at the edge, origin behind load balancer.
  └─► Cost: ~$5,000-50,000/month (dominated by CDN egress)
```

---

## 3. Rate Limiting Strategy

### Multi-Layer Defense

```
Layer 1: Nginx (Connection Level)
  └─► limit_conn: 100 concurrent connections per IP
  └─► limit_req: 50 requests/second per IP (burst 20)

Layer 2: API Gateway (Route Level)
  └─► /upload: 5 req/min per authenticated user
  └─► /stream: 100 req/sec per session (segment fetches)
  └─► /auth: 10 req/min per IP (brute-force protection)

Layer 3: Application (Business Logic)
  └─► Max 3 concurrent transcodes per user
  └─► Max 50GB storage per free-tier account
  └─► Max 5 active WebRTC sessions per user
```

### Rate Limit Response Codes

| Code | Meaning | Client Behavior |
|---|---|---|
| `429 Too Many Requests` | Rate limit exceeded | Retry after `Retry-After` header |
| `503 Service Unavailable` | Load shedding active | Client shows "high traffic" message |

---

## 4. Cost Model & Budgeting

### Per-User Monthly Cost Breakdown

| Component | Cost/User/Month | At 10K Users | At 1M Users |
|---|---|---|---|
| Compute (API + Workers) | $0.002 | $20 | $2,000 |
| Storage (S3, 5 qualities) | $0.005 | $50 | $5,000 |
| CDN Egress | $0.015 | $150 | $15,000 |
| Database (Auth/Catalog) | $0.001 | $10 | $1,000 |
| **Total** | **$0.023** | **$230** | **$23,000** |

### The "Unit Economics" Rule

```
Revenue per user (ad-supported): ~$0.10/month
Revenue per user (subscription):  ~$5.00/month

Break-even requires:
  Ad-supported → CDN costs must stay below $0.05/user/month
  Subscription → Total infra must stay below $1.00/user/month

This is why Netflix spends $1B/year on AWS and still profits.
```

### Cost Optimization Levers

1. **CDN Cache Hit Ratio > 95%** → Reduces S3 egress by 19x
2. **ABR Defaults to 480p** → Halves average bandwidth per user
3. **Transcode Only Popular Content** → Skip 4K for videos with < 100 views
4. **Spot Instances for Workers** → 70% compute cost reduction
5. **S3 Intelligent Tiering** → Auto-moves cold segments to Glacier

---

## 5. Incident Response Playbook

| Severity | Definition | Response Time | Example |
|---|---|---|---|
| **SEV-1** | Total service outage | < 15 minutes | API Gateway down, all users affected |
| **SEV-2** | Major degradation | < 1 hour | Transcoding queue stalled, no new videos |
| **SEV-3** | Minor degradation | < 4 hours | WebRTC latency spike > 2s |
| **SEV-4** | Cosmetic/non-blocking | Next business day | Dashboard shows stale metrics |

---

[Back to Roadmap](../README.md) | [Failure Modeling](failure-modeling.md) | [Streaming Internals](streaming-internals.md)
