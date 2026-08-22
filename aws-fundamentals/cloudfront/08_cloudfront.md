# 08 — CloudFront (Content Delivery Network)

## Architecture

```
                         USERS
                           │
                           ▼
                ┌─────────────────────┐
                │     CloudFront      │
                │   Edge / Cache      │
                │  (Global CDN)       │
                └─────────────────────┘
                           │
                     Cache Miss
                           │
                           ▼
         ┌─────────────────┴─────────────────┐
         │                                   │
         ▼                                   ▼
   ┌──────────┐                     ┌──────────────┐
   │    S3    │                     │     ALB      │
   │ (Static) │                     │              │
   └──────────┘                     └──────────────┘
                                            │
                                            ▼
                                   ┌──────────────┐
                                   │ EC2 / EKS    │
                                   │ (Application)│
                                   └──────────────┘
```

**Static content:** User → CloudFront → S3

**Dynamic applications:** User → CloudFront → ALB → EC2/EKS

CloudFront brings content closer to users through global edge locations, reducing latency and origin load.

---

## Theory

### 1. Edge Locations

An **Edge Location** is a location where CloudFront keeps cached copies of content close to users.

```
                 CloudFront
              Global Edge Network

        Nepal       Japan       Europe
          ↓           ↓            ↓
       Edge         Edge         Edge
          \           |            /
           \          |           /
                 Origin
              S3 / ALB / EC2
```

| Concept | Description |
|---------|-------------|
| **Edge Location** | CloudFront infrastructure that caches content near users |
| **Origin** | Where original content lives (S3, ALB, EC2, EKS) |
| **Cache HIT** | Content found at edge → served directly, no origin trip |
| **Cache MISS** | Content not at edge → fetched from origin, then cached |

**Why not create EC2 everywhere?**

A static image like `logo.png` doesn't need a full application server at every location. CloudFront caches it at edge locations instead.

| Service | Purpose |
|---------|---------|
| **EC2** | Runs your application logic |
| **CloudFront** | Brings frequently requested content closer to users |

---

### 2. POP — Point of Presence

A **POP** is a physical location where a network/CDN provider has infrastructure.

| Term | Definition |
|------|-----------|
| **POP** | Physical network location |
| **Edge Location** | CloudFront infrastructure at/associated with that location |

AWS manages these locations. You don't configure or manage them directly.

---

### 3. CloudFront Distribution

A **Distribution** is your CloudFront configuration — it tells CloudFront how your CDN should behave.

```
User
 ↓
CloudFront Distribution
 ↓
Origin
```

A Distribution defines:

| Setting | What It Controls |
|---------|-----------------|
| **Origin** | Where content comes from (S3, ALB, etc.) |
| **Cache behavior** | What requests should be cached |
| **TTL** | How long content stays cached |
| **Origin communication** | How CloudFront talks to your origin |
| **HTTPS/Security** | TLS certificates, security policies |
| **Routing** | How requests are directed to origins |

**Important distinction:**

| Term | Meaning |
|------|---------|
| **Edge Location** | Nearby CloudFront infrastructure/cache |
| **Origin** | Where your original content/application exists |

Edge Location ≠ Origin

---

### 4. Cache Behaviors

A Distribution can have different rules for different URL paths.

```
myapp.com/images/*  →  S3
myapp.com/api/*     →  ALB
```

Behaviors let CloudFront say: "For this type of request, handle it this way."

| Path Pattern | Origin | Use Case |
|--------------|--------|----------|
| `/images/*` | S3 | Static assets (logos, photos) |
| `/api/*` | ALB | Dynamic API responses |
| `/*` | S3 or ALB | Default catch-all |

---

### 5. Viewer Request vs Origin Request

| Request Type | Direction | Meaning |
|--------------|-----------|---------|
| **Viewer Request** | User → CloudFront | Request from the user to CloudFront |
| **Origin Request** | CloudFront → Origin | Request CloudFront makes to your backend when it needs to retrieve content |

```
Viewer Request                Origin Request
User ───────────→ CloudFront ───────────→ Origin
         (user → CF)              (CF → backend)
```

**Key idea:**

- **Viewer** = user → CloudFront
- **Origin** = CloudFront → your backend/source

---

### 6. CloudFront + S3 — Static Content Architecture

This is the classic static content pattern.

**S3 contains:**

```
index.html
style.css
logo.png
app.js
```

**Request flow:**

```
First Request:
User → Edge → Cache MISS → S3 → Edge caches object → User

Later Request:
User → Nearby Edge → Cache HIT → User (no S3 trip)
```

**Benefits:**

| Benefit | Description |
|---------|-------------|
| **Lower latency** | Content served from nearby edge |
| **Global distribution** | Users worldwide get fast access |
| **Caching** | Repeated requests served from cache |
| **Less S3 load** | Fewer direct hits to origin |
| **HTTPS/Security** | TLS termination at edge |

**Summary:** S3 stores original static files. CloudFront distributes them efficiently around the world.

---

### 7. CloudFront + ALB — Dynamic Application Architecture

For applications that need server-side processing:

```
User
 ↓
CloudFront
 ↓
ALB
 ↓
EC2 / EKS
```

| Component | Role |
|-----------|------|
| **CloudFront** | Global entry point + caching |
| **ALB** | Distributes traffic across instances |
| **EC2/EKS** | Runs the application |

**Cache behavior:**

```
Cache HIT  → CloudFront responds directly
Cache MISS → CloudFront → ALB → Healthy EC2
```

---

### 8. The Full Request Path (Production)

```
Browser
  ↓
myapp.com
  ↓
Route53
  ↓
CloudFront (HTTPS via ACM)
  ↓
ALB
  ↓
EKS
  ↓
Pods
```

| Step | Service | Purpose |
|------|---------|---------|
| 1 | **Route53** | DNS resolution |
| 2 | **CloudFront** | Edge caching + HTTPS termination |
| 3 | **ALB** | Load balancing across targets |
| 4 | **EKS** | Container orchestration |
| 5 | **Pods** | Application workloads |

---

### 9. Mental Model — Layered Architecture

```
                    USERS
                      ↓
             ┌────────────────┐
             │   CloudFront   │
             │  Edge / Cache  │
             └────────────────┘
                      ↓
                 Cache Miss
                      ↓
             ┌────────────────┐
             │      ALB       │
             └────────────────┘
                      ↓
             ┌────────────────┐
             │   EC2 / EKS    │
             │  Application   │
             └────────────────┘
```

| Content Type | Path |
|--------------|------|
| **Static** | User → CloudFront → S3 |
| **Dynamic** | User → CloudFront → ALB → EC2/EKS |

CloudFront's job is **not** to replace S3, ALB, or EC2 — it's to bring content closer to users and reduce origin load.

---

## Key Insights

| Concept | Insight |
|---------|---------|
| **Edge Location** | CloudFront cache node near users — content served from here when cached |
| **Origin** | Where original content lives (S3, ALB, EC2) — edge locations fetch from here |
| **Distribution** | Your CloudFront configuration — defines origins, behaviors, TTLs, security |
| **Behaviors** | Rules for different URL paths — route `/images/*` to S3, `/api/*` to ALB |
| **Viewer vs Origin Request** | Viewer = user→CloudFront, Origin = CloudFront→backend |
| **Cache HIT** | Content found at edge — fast response, no origin load |
| **Cache MISS** | Content not at edge — fetched from origin, then cached for next time |
| **POP vs Edge Location** | POP = physical network location, Edge Location = CloudFront infrastructure at that POP |
| **Static vs Dynamic** | Static (S3) = cache everything; Dynamic (ALB) = cache selectively or not at all |
| **Full stack** | Route53 → CloudFront → ALB → EKS → Pods |

---

## Key Commands

| Command | Purpose |
|---------|---------|
| `aws cloudfront create-distribution --origin-domain-name mybucket.s3.amazonaws.com` | Create a CloudFront distribution with S3 origin |
| `aws cloudfront list-distributions` | List all CloudFront distributions |
| `aws cloudfront get-distribution --id E1234ABCDEF` | Get details of a specific distribution |
| `aws cloudfront create-invalidation --distribution-id E1234ABCDEF --paths "/index.html"` | Invalidate cached objects (force refresh) |
| `aws cloudfront create-invalidation --distribution-id E1234ABCDEF --paths "/*"` | Invalidate all cached objects |
| `aws cloudfront wait distribution-deployed --id E1234ABCDEF` | Wait until distribution is fully deployed |
| `aws cloudfront delete-distribution --id E1234ABCDEF` | Delete a distribution (must disable first) |
| `aws cloudfront update-distribution --id E1234ABCDEF --distribution-config file://config.json` | Update distribution configuration |

---

## Mistakes & Fixes Log

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Forgetting to invalidate cache after S3 update | Old content served despite new files in S3 | Create invalidation for affected paths |
| Origin pointing to wrong endpoint | 502 Bad Gateway or 504 Timeout | Verify origin domain (S3 bucket name, ALB DNS) |
| Distribution still deploying | Changes not taking effect | Wait for `LastModifiedTime` to stabilize; use `wait distribution-deployed` |
| Trying to delete without disabling | `DistributionNotDisabled` error | Disable distribution first, then delete |
| Cache TTL too long | Stale content served for hours/days | Reduce default TTL or use cache behavior overrides |
| Missing HTTPS redirect | Users accessing via HTTP | Add redirect rule in cache behavior or use Origin Request Policy |
| Not using origin access control (OAC) | S3 bucket must be public | Configure OAC to allow CloudFront to access private S3 |

---

## Clean Up

Delete resources in this order to avoid charges:

1. **CloudFront Distribution** — disable first, then delete (takes ~15-20 min to fully delete)
2. **S3 Bucket** — empty first, then delete (if used as origin)
3. **ACM Certificate** — delete if created specifically for CloudFront (must be in `us-east-1`)
4. **Route53 Records** — remove any alias records pointing to the distribution

**Cost warning:** CloudFront charges for data transfer and requests. Always delete distributions you're not using.
