# 01 — Cloud Concepts & AWS Fundamentals

## What is Cloud Computing?
- On-demand delivery of compute, storage, and networking over the internet
- Pay only for what you use (no upfront hardware costs)
- Elastic — scale up/down as needed

## Service Models

| Model | You Manage | Provider Manages |
|-------|-----------|-----------------|
| **IaaS** | Apps, data, runtime, OS, networking | Virtualization, servers, storage, networking hardware |
| **PaaS** | Apps, data | Runtime, OS, middleware, infrastructure |
| **SaaS** | Nothing (just use the app) | Everything |

- **IaaS** — EC2, VPC, S3
- **PaaS** — Elastic Beanstalk, RDS, Lambda
- **SaaS** — WorkMail, Chime

## Deployment Models
- **Public Cloud** — AWS, Azure, GCP (shared infra, multi-tenant)
- **Private Cloud** — Dedicated to one organization
- **Hybrid Cloud** — Mix of public + private

## Key AWS Concepts
- **Region** — Geographic location (e.g. us-east-1)
- **AZ (Availability Zone)** — Isolated data center within a region
- **Edge Location** — CDN endpoint for CloudFront
- **Shared Responsibility Model** — AWS secures the cloud, you secure what's *in* the cloud
- **Well-Architected Framework** — 6 pillars: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability
