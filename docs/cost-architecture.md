# 💰 Cost Architecture: Where the Money Goes at Scale

Cost is the silent architect. At every scale inflection, **cost constraints drive architectural decisions** as much as performance does. This document maps the financial reality of operating a streaming platform.

---

## 1. Cost Breakdown by Component

### Monthly Cost Model

| Scale | Compute (API+Workers) | Storage (S3) | CDN Egress | Transcoding | Database | Total | Per-User |
|---|---|---|---|---|---|---|---|
| 1K users | $50 | $12 | $30 | $10 | $10 | **$112** | $0.112 |
| 10K users | $200 | $120 | $300 | $80 | $40 | **$740** | $0.074 |
| 100K users | $800 | $500 | $3,000 | $400 | $200 | **$4,900** | $0.049 |
| 1M users | $5,000 | $2,500 | $23,000 | $3,000 | $1,200 | **$34,700** | $0.035 |
| 10M users | $30,000 | $15,000 | $180,000 | $20,000 | $8,000 | **$253,000** | $0.025 |

### Cost Distribution (at 1M users)

```
CDN Egress:     66%  ← Every .ts segment served = bandwidth bill
Compute:        14%  ← API servers + Celery workers
Transcoding:     9%  ← FFmpeg CPU hours (grows linearly with uploads)
Storage:         7%  ← 4 quality levels × all videos × 3 tiers
Database:        4%  ← Auth + Catalog read replicas
```

---

## 2. CDN vs Origin: The Core Cost Tradeoff

### Without CDN (Direct Origin Delivery)

```
100K viewers × 720p (1.26 GB/hr) = 126 TB/hour from origin
  └─► S3 egress: 126,000 GB × $0.09/GB = $11,340/hour
  └─► Origin compute: 100K concurrent connections = 40+ API servers
  └─► Total: ~$12,000/hour ← UNSUSTAINABLE
```

### With CDN (95% Cache Hit)

```
100K viewers × 720p (1.26 GB/hr) = 126 TB/hour total delivery
  └─► CDN serves 95% from edge: 119,700 GB × $0.02/GB = $2,394
  └─► Origin serves 5% cache misses: 6,300 GB × $0.09/GB = $567
  └─► Total: ~$2,961/hour
  └─► SAVINGS: 75% ($9,039/hour saved)
```

### CDN Cost Optimization Tactics

| Tactic | Impact | Implementation |
|---|---|---|
| Increase cache TTL to 24h | +5% hit rate | `proxy_cache_valid 200 24h;` |
| Pre-warm trending content | -50% miss rate on new viral | Cron job pushes top 100 to CDN |
| Request collapsing | -99% origin load on miss storm | `proxy_cache_lock on;` |
| Negotiate CDN commits | -30% per-GB price | Annual commit (1 PB/month minimum) |
| Multi-CDN arbitrage | -15% avg cost | Route to cheapest healthy CDN per region |

---

## 3. Storage Tiering Strategy

### The Problem: Storage Grows Forever

```
1 video = 2GB raw + 5.2GB encoded (4 qualities) = 7.2GB total
1,000 videos/day × 365 days = 2,628 TB/year
At S3 Standard ($0.023/GB/month): $60,444/month after 1 year
```

### The Solution: Lifecycle Policies

| Tier | Storage Class | Age | Cost/GB/month | Access Latency | Use Case |
|---|---|---|---|---|---|
| **HOT** | S3 Standard (SSD) | 0-7 days | $0.023 | < 10ms | New uploads, trending content |
| **WARM** | S3 Infrequent Access | 8-90 days | $0.0125 | < 50ms | Regular catalog |
| **COLD** | S3 Glacier | 91-365 days | $0.004 | 5-12 hours | Long tail, compliance |
| **ARCHIVE** | S3 Glacier Deep | > 365 days | $0.00099 | 12-48 hours | Legal hold, never-watched |

### Tiering Cost Savings

```
WITHOUT tiering (52TB, all S3 Standard):
  52,000 GB × $0.023 = $1,196/month

WITH tiering (52TB distributed):
  HOT:     5,200 GB × $0.023  = $120  (10% of content, last 7 days)
  WARM:   20,800 GB × $0.0125 = $260  (40% of content)
  COLD:   20,800 GB × $0.004  = $83   (40% of content)
  ARCHIVE: 5,200 GB × $0.00099= $5    (10% of content, >1 year old)
  Total: $468/month
  SAVINGS: 61% ($728/month saved)
```

---

## 4. Transcoding Cost Explosion

Transcoding is the **only cost that scales with uploads, not viewers.**

### Cost Per Transcode Job

```
1 video (2GB, 1080p, 20 min):
  └─► 4 quality passes × ~8 min each = 32 CPU-minutes
  └─► On-demand (c5.2xlarge): $0.34/hour = $0.18/video
  └─► On spot instance:       $0.10/hour = $0.05/video (70% savings)
```

### Transcoding Cost at Scale

| Uploads/day | CPU-hours/day | On-demand/month | With Spot/month | Savings |
|---|---|---|---|---|
| 100 | 53 | $540 | $162 | $378 |
| 1,000 | 533 | $5,400 | $1,620 | $3,780 |
| 10,000 | 5,333 | $54,000 | $16,200 | $37,800 |
| 100,000 | 53,333 | $540,000 | $162,000 | $378,000 |

### Transcoding Optimization Strategies

| Strategy | Savings | Risk |
|---|---|---|
| **Spot instances** | 70% | Jobs interrupted (need checkpointing) |
| **Lazy transcoding** | 50% | Skip qualities nobody requests (only transcode 1080p if >100 views) |
| **Hardware encoding (NVENC)** | 4× faster | GPU instances cost more, quality slightly lower |
| **Codec upgrade (AV1)** | 30% smaller files | 10× slower encoding, limited hardware decode support |
| **Shared segments** | 20% | If same GOP structure, share audio track across qualities |

---

## 5. Bandwidth Cost at Scale

### Compression's Impact on Cost

| Codec | Equivalent Quality Bitrate | Data/User/Hour (720p) | Cost/User/Hour (CDN) | Savings vs H.264 |
|---|---|---|---|---|
| H.264 (current) | 2,800 kbps | 1.26 GB | $0.025 | — |
| H.265/HEVC | 1,680 kbps | 0.76 GB | $0.015 | 40% |
| AV1 | 1,400 kbps | 0.63 GB | $0.013 | 50% |

### Caching Impact on Bandwidth Cost

```
Popular content (top 10%):
  └─► Watched by 80% of users (Pareto distribution)
  └─► CDN cache hit rate: 99%+ (near-zero origin cost)
  └─► Cost: essentially just CDN edge delivery

Long-tail content (bottom 50%):
  └─► Watched by 5% of users, but represents 50% of storage
  └─► CDN cache hit rate: 10-30% (most requests are cold misses)
  └─► Cost: frequent origin fetches, high per-view cost
  └─► Strategy: keep in COLD storage, accept slower startup for rare content
```

---

## 6. Multi-Region Replication Cost

### Cross-Region Data Transfer

```
Replicating 10TB of trending content to 3 regions:
  S3 CRR cost: 10,000 GB × $0.02/GB × 3 regions = $600/month
  Additional storage: 30TB × $0.023/GB = $690/month
  Total replication cost: $1,290/month

BUT: Reduces P99 latency for 70% of global users from 400ms → 80ms
ROI: Each 100ms latency reduction → +1.5% user engagement
```

### When Multi-Region Becomes Worth It

| Scale | Single-Region Latency | Multi-Region Latency | Replication Cost | Worth It? |
|---|---|---|---|---|
| 10K users | 150ms avg | 80ms avg | $1,290/mo | ❌ Users not price-sensitive enough |
| 100K users | 200ms avg | 80ms avg | $1,290/mo | ⚠️ Marginal (depends on revenue) |
| 1M users | 400ms P99 | 80ms P99 | $1,290/mo | ✅ Engagement gain > replication cost |

---

## 7. Unit Economics: Can You Afford Users?

### Break-Even Analysis

```
AD-SUPPORTED MODEL:
  Revenue per user: ~$0.08-0.15/month (CPM-based)
  Infrastructure cost: $0.035/user/month (at 1M scale)
  Margin: $0.045-0.115/user/month
  Break-even: ~300K users (if total fixed costs = $15K/month)

SUBSCRIPTION MODEL:
  Revenue per user: ~$5-10/month
  Infrastructure cost: $0.035/user/month
  Margin: $4.96-9.96/user/month
  This is why Netflix, at $800M+ AWS bill/year, still profits.

FREE TIER + PREMIUM:
  90% free users × $0 revenue = subsidized by
  10% premium users × $10/month = $1/user avg revenue
  Must keep infra under $0.50/user/month (including free tier)
```

---

[Back to Roadmap](../README.md) | [Operations Runbook](operations-runbook.md) | [Hyperscale Guide](hyperscale.md)
