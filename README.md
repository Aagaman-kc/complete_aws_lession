<p align="center">
  <img src="roadmap.png" alt="AWS 5-Day Roadmap" width="800"/>
</p>

<h1 align="center">☁️ Complete AWS – 5-Day Bootcamp</h1>

<p align="center">
  <strong>From zero to production-ready microservices on AWS in 5 days.</strong><br>
  Hands-on labs covering VPC, EC2, EKS, Terraform, CI/CD, and monitoring.
</p>

<p align="center">
  <a href="#-roadmap"><img src="https://img.shields.io/badge/day--1-AWS%20Fundamentals-FF9900?style=flat&logo=amazonaws" /></a>
  <a href="#-roadmap"><img src="https://img.shields.io/badge/day--2-Real%20App%20on%20EC2-232F3E?style=flat&logo=fastapi" /></a>
  <a href="#-roadmap"><img src="https://img.shields.io/badge/day--3-Amazon%20EKS-326CE5?style=flat&logo=kubernetes" /></a>
  <a href="#-roadmap"><img src="https://img.shields.io/badge/day--4-Terraform-7B42BC?style=flat&logo=terraform" /></a>
  <a href="#-roadmap"><img src="https://img.shields.io/badge/day--5-Portfolio%20Project-181717?style=flat&logo=github" /></a>
</p>

---

## 🗺 Roadmap

> The roadmap is organized into interconnected modules, progressing from foundational knowledge through core infrastructure to advanced cloud components and a final capstone project.

| Day | Focus | Services Covered | Deliverable | Notes |
|:---:|-------|-----------------|-------------|:-----:|
| **1** | [AWS Fundamentals](day-1-aws-fundamentals/) | Cloud Concepts → EC2 → IAM → VPC → EBS → S3 → Security Groups → CloudWatch | Secure web server on EC2 with nginx, CloudWatch logs, S3 bucket | [📓](day-1-aws-fundamentals/01_cloud_concepts.md) · [📓](day-1-aws-fundamentals/02_ec2.md) |
| **2** | [Real App on EC2](day-2-ec2-app-deployment/note.md) | EC2, Docker, FastAPI, PostgreSQL, S3 (static assets/backups) | FastAPI + PostgreSQL running on EC2 via Docker Compose | [📓](day-2-ec2-app-deployment/note.md) |
| **3** | [Amazon EKS](day-3-eks-migration/note.md) | EKS, eksctl, kubectl, Load Balancer, IAM Roles | Existing K8s app migrated from kind to EKS with external LB | [📓](day-3-eks-migration/note.md) |
| **4** | [Terraform IaC](day-4-terraform-eks/note.md) | Terraform, VPC Module, EKS Module, IAM, Remote State | VPC + EKS cluster + IAM roles provisioned as code | [📓](day-4-terraform-eks/note.md) |
| **5** | [Portfolio Project](day-5-portfolio-project/note.md) | GitHub Actions, ECR, HPA, CloudWatch Insights, Terraform | Production-style microservices with CI/CD, monitoring, autoscaling | [📓](day-5-portfolio-project/note.md) |

---

## 🏗 Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        AWS Cloud                                │
│                                                                  │
│  ┌─────────────────────────────┐   ┌─────────────────────────┐  │
│  │           VPC               │   │     Amazon ECR           │  │
│  │  ┌───────────────────────┐  │   │  ┌───────────────────┐  │  │
│  │  │   Public Subnet       │  │   │  │ backend:latest   │  │  │
│  │  │   ┌─────────────────┐ │  │   │  │ frontend:latest  │  │  │
│  │  │   │ Bastion / NAT    │ │  │   │  └───────────────────┘  │  │
│  │  │   └─────────────────┘ │  │   └─────────────────────────┘  │
│  │  └───────────────────────┘  │                                │
│  │  ┌───────────────────────┐  │   ┌─────────────────────────┐  │
│  │  │   Private Subnet      │  │   │     EKS Cluster          │  │
│  │  │   ┌─────────────────┐ │  │   │  ┌───────────────────┐  │  │
│  │  │   │ EKS Worker Nodes│ │  │   │  │ Managed Node Grp  │  │  │
│  │  │   │ (t3.medium)     │ │  │   │  │  ┌─────────────┐ │  │  │
│  │  │   │ ┌─────────────┐ │ │  │   │  │  │ backend Pod │ │  │  │
│  │  │   │ │ FastAPI App │ │ │  │   │  │  ├─────────────┤ │  │  │
│  │  │   │ ├─────────────┤ │ │  │   │  │  │ frontend Pod│ │  │  │
│  │  │   │ │ PostgreSQL  │ │ │  │   │  │  ├─────────────┤ │  │  │
│  │  │   │ │(StatefulSet)│ │ │  │   │  │  │ PostgreSQL  │ │  │  │
│  │  │   │ └─────────────┘ │ │  │   │  │  └─────────────┘ │  │  │
│  │  │   └─────────────────┘ │  │   │  └───────────────────┘  │  │
│  │  └───────────────────────┘  │   └─────────────────────────┘  │
│  └─────────────────────────────┘                                │
│                                                                  │
│  ┌────────────────────┐   ┌──────────────────────────────────┐  │
│  │   S3 Buckets       │   │     CloudWatch                    │  │
│  │  ┌──────────────┐  │   │  ┌───────────────────────────┐  │  │
│  │  │ Static Assets│  │   │  │ Metrics · Logs · Alarms   │  │  │
│  │  │ Backups      │  │   │  │ Container Insights        │  │  │
│  │  └──────────────┘  │   │  └───────────────────────────┘  │  │
│  └────────────────────┘   └──────────────────────────────────┘  │
│                                                                  │
│  ┌────────────────────┐   ┌──────────────────────────────────┐  │
│  │   GitHub Actions   │   │     Terraform (IaC)              │  │
│  │  ┌──────────────┐  │   │  ┌───────────────────────────┐  │  │
│  │  │ Build → Push │  │   │  │ VPC · EKS · IAM · ECR    │  │  │
│  │  │ → Deploy EKS │  │   │  │ Remote State (S3 + DynDB) │  │  │
│  │  └──────────────┘  │   │  └───────────────────────────┘  │  │
│  └────────────────────┘   └──────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Concepts Progression

The roadmap follows a layered learning approach:

### Day 1 — Foundational Knowledge
Cloud Computing concepts, **IAM** (users, groups, roles, policies), **EC2** (instance types, AMIs, key pairs), **VPC** (subnets, route tables, IGW, NAT), **EBS** (block storage), **S3** (object storage, bucket policies), **Security Groups** (stateful firewalls), **CloudWatch** (logs, metrics, alarms).

### Day 2 — Core Infrastructure & Application Deployment
Launch a real **FastAPI + PostgreSQL** app on EC2 using **Docker Compose**. Use **S3** for static assets and backups. Attach **EBS** volumes for persistence.

### Day 3 — Container Orchestration with EKS
Migrate your existing Kubernetes project from **kind** to **Amazon EKS**. Deploy with `kubectl`, set up **IAM Roles for Service Accounts**, and expose via **AWS Load Balancer Controller**.

### Day 4 — Infrastructure as Code with Terraform
Rewrite all EKS infrastructure using **Terraform** — VPC, subnets, EKS cluster, node groups, IAM roles. Use community modules and manage state remotely with **S3 + DynamoDB**.

### Day 5 — Capstone: Production Microservices Platform
Combine everything into a single portfolio project:
- **CI/CD** with GitHub Actions → ECR → EKS
- **Horizontal Pod Autoscaler** for auto-scaling
- **CloudWatch Container Insights** for monitoring
- **Terraform** for full infrastructure automation

---

## ✅ Prerequisites

| Resource | Purpose |
|----------|---------|
| [AWS Account](https://aws.amazon.com/free/) | Free Tier — all labs designed to stay within it |
| [AWS CLI](https://aws.amazon.com/cli/) | Configured with `aws configure` |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | Kubernetes CLI |
| [eksctl](https://eksctl.io/) | EKS cluster management |
| [Terraform](https://developer.hashicorp.com/terraform/downloads) | Infrastructure as Code |
| [Docker](https://docs.docker.com/get-docker/) | Containerization |
| [GitHub Account](https://github.com) | CI/CD and portfolio hosting |
| [Existing K8s Project](https://kind.sigs.k8s.io/) | Your Phase 10 manifests (kind → EKS migration) |

---

## 📁 Repository Structure

```
complete-aws/
│
├── README.md                        # You are here
├── roadmap.png                      # Visual roadmap graphic
│
├── day-1-aws-fundamentals/          # Cloud Concepts → EC2 → IAM → VPC → EBS → S3 → Security Groups → CloudWatch
│   ├── 01_cloud_concepts.md
│   └── 02_ec2.md
│
├── day-2-ec2-app-deployment/        # FastAPI · PostgreSQL · Docker Compose · S3
│   └── note.md
│
├── day-3-eks-migration/             # EKS · eksctl · kubectl · Load Balancers · IRSA
│   └── note.md
│
├── day-4-terraform-eks/             # Terraform · VPC modules · EKS modules · Remote State
│   └── note.md
│
└── day-5-portfolio-project/         # GitHub Actions · ECR · HPA · Container Insights
    └── note.md
```

---

## 🛠 Tech Stack

| Category | Technologies |
|----------|-------------|
| **Compute** | EC2, EKS (managed Kubernetes), Docker, Amazon ECR |
| **Networking** | VPC, Public/Private Subnets, Internet Gateway, NAT Gateway, Security Groups, ALB/NLB |
| **Storage** | S3 (objects/backups), EBS (block), EFS (file — optional) |
| **Databases** | PostgreSQL (containerized via StatefulSet), RDS (managed — optional) |
| **CI/CD** | GitHub Actions |
| **IaC** | Terraform, eksctl |
| **Monitoring** | CloudWatch Logs, CloudWatch Metrics, CloudWatch Alarms, Container Insights |
| **Identity** | IAM Users, IAM Groups, IAM Roles, IAM Policies, IRSA |
| **Orchestration** | Docker Compose (Day 2), Kubernetes / EKS (Days 3–5) |

---

## 📚 Detailed Learnings by Day

<details>
<summary><strong>Day 1 — AWS Fundamentals</strong></summary>

- Cloud Computing concepts (IaaS vs PaaS vs SaaS) and the Well-Architected Framework
- **IAM** — Users, groups, roles, policies, and least-privilege principles
- **EC2** — Instance types, AMIs, key pairs, user data, instance metadata
- **VPC** — CIDR blocks, subnets, route tables, Internet Gateway, NAT Gateway/Instance
- **EBS** — Volume types, attaching volumes, snapshots
- **S3** — Bucket creation, bucket policies, versioning, lifecycle rules
- **Security Groups** vs NACLs — Stateful vs stateless firewall rules
- **CloudWatch** — Metrics, log groups, log streams, alarms, CloudWatch agent

**Project:** Secure web server — nginx on EC2 behind a security group, with CloudWatch logging and an S3 bucket for backups.

</details>

<details>
<summary><strong>Day 2 — Real App on EC2</strong></summary>

- **Docker Compose** — Multi-container orchestration on a single EC2 host
- **FastAPI** backend with **PostgreSQL** — Containerized with persistent EBS volumes
- **S3** for static asset hosting and automated database backups
- Environment variable management and secrets handling
- Security group configuration for app access (HTTP 80)

**Project:** FastAPI + PostgreSQL running on EC2 via Docker Compose, with S3 for static assets/backups.

</details>

<details>
<summary><strong>Day 3 — Amazon EKS</strong></summary>

- **EKS architecture** — Managed control plane vs self-managed worker nodes
- **eksctl** — Cluster and node group provisioning
- **kubectl context switching** — Managing multiple clusters
- **AWS Load Balancer Controller** — Automatic ALB/NLB provisioning for Ingress/Service
- **IAM Roles for Service Accounts (IRSA)** — Fine-grained pod permissions
- **Storage** — EBS-backed PVCs with StatefulSets
- **CloudWatch** — EKS control plane logs

**Project:** Migrate existing kind-based Kubernetes project to a production EKS cluster with external Load Balancer.

</details>

<details>
<summary><strong>Day 4 — Terraform IaC</strong></summary>

- **Terraform workflow** — `init`, `plan`, `apply`, `destroy`
- **Providers** — AWS provider configuration
- **Community modules** — `terraform-aws-modules/vpc/aws`, `terraform-aws-modules/eks/aws`
- **State management** — Local state → Remote state (S3 + DynamoDB locking)
- **Variables, outputs, and data sources**
- **Resource dependencies** and `terraform graph`

**Project:** Provision the entire Day 3 infrastructure (VPC, EKS cluster, IAM roles) as reusable Terraform code.

</details>

<details>
<summary><strong>Day 5 — Portfolio Project</strong></summary>

- **GitHub Actions** — CI/CD pipeline building Docker images → pushing to ECR → deploying to EKS
- **Amazon ECR** — Private container registry with IAM authentication
- **Horizontal Pod Autoscaler** — CPU/memory-based auto-scaling
- **CloudWatch Container Insights** — Cluster-level monitoring with performance dashboards
- **Production repository structure** — Clear separation of infra (`terraform/`) and app (`k8s/`) code
- **README documentation** — Architecture diagram, deployment instructions, screenshots

**Project:** A single GitHub repository combining all 5 days into a production-ready, CI/CD-automated, auto-scaled microservices platform on EKS.

</details>

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/yourusername/complete-aws.git
cd complete-aws

# Start with fundamentals
code day-1-aws-fundamentals/01_cloud_concepts.md
```

Each day folder contains a `note.md` with objectives, concept explanations, step-by-step instructions, and CLI commands.

> ⚠️ **Cost Warning**: EKS clusters, Load Balancers, and NAT Gateways incur costs even under Free Tier. Always run `terraform destroy` or manually delete resources after each session.

---

## 🤝 Connect

<p align="center">
  <a href="https://github.com/yourusername">
    <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github" />
  </a>
  <a href="https://linkedin.com/in/yourusername">
    <img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin" />
  </a>
  <a href="mailto:you@email.com">
    <img src="https://img.shields.io/badge/Email-EA4335?style=for-the-badge&logo=gmail" />
  </a>
</p>

---

<p align="center">
  <sub>Built as a 5-day AWS immersion program — from fundamentals to production microservices.</sub>
</p>
