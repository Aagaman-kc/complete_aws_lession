<p align="center">
  <img src="roadmap.png" alt="AWS 5-Day Roadmap" width="800"/>
</p>

<h1 align="center">☁️ Complete AWS</h1>

<p align="center">
  <strong>From zero to production-ready microservices on AWS.</strong><br>
  Hands-on modules covering EC2, RDS, EKS, Terraform, CI/CD, and monitoring — organized by topic, not by day.
</p>

---

## 🗺 Roadmap

> Modules are organized progressively — from foundational knowledge through core infrastructure to advanced cloud components and a final capstone project.

| # | Topic | What's Covered | Deliverable |
|:-:|-------|---------------|-------------|
| 1 | [Cloud Concepts](aws-fundamentals/cloud-concepts/01_cloud_concepts.md) | IaaS vs PaaS vs SaaS, deployment models, regions/AZs, shared responsibility, Well-Architected Framework | — |
| 2 | [EC2](aws-fundamentals/ec2/02_ec2.md) | Instance types, AMIs, key pairs (SSH/RSA), security groups, user data, metadata, Elastic IP | Deploy K8s app on EC2 via kind |
| 3 | [RDS](ec2-app-deployment/rds/01_rds.md) | Managed PostgreSQL, RDS vs self-hosted, Multi-AZ, read replicas | — |
| 4 | [Docker Compose](ec2-app-deployment/docker-compose/02_docker_compose_deploy.md) | Multi-container orchestration, EBS volumes, env vars, secrets, S3 backups | FastAPI + PostgreSQL on EC2 |
| 5 | [EKS Basics](eks-migration/eks-basics/01_eks_basics.md) | EKS architecture, eksctl, managed node groups, kubectl context | — |
| 6 | [EKS Deployment](eks-migration/eks-deployment/02_eks_deployment.md) | Deploying manifests, ALB/NLB via Load Balancer Controller, IRSA | K8s app on EKS with LB |
| 7 | [Terraform Fundamentals](terraform-eks/terraform-fundamentals/01_terraform_fundamentals.md) | Workflow (init/plan/apply), providers, resources, variables, outputs | — |
| 8 | [Terraform State & Modules](terraform-eks/terraform-state-modules/02_terraform_state_modules.md) | Remote state (S3 + DynamoDB), community modules, dependency graph | EKS cluster via Terraform |
| 9 | [CI/CD & ECR](portfolio-project/cicd-ecr/01_cicd_ecr.md) | GitHub Actions pipeline, ECR push/pull, automated deploy to EKS | — |
| 10 | [HPA & Monitoring](portfolio-project/hpa-monitoring/02_hpa_monitoring.md) | Horizontal Pod Autoscaler, CloudWatch Container Insights | — |
| 11 | [Repo Structure](portfolio-project/repo-structure/03_repo_structure.md) | infra/ vs app/ layout, README docs, cost hygiene | Production microservices platform |

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

### Foundations (1–2)
Cloud concepts, IaaS/PaaS/SaaS, shared responsibility, then **EC2** (instance types, AMIs, key pairs, security groups, Elastic IP). **Project:** Deploy K8s app on EC2 via kind.

### Application Deployment (3–4)
**RDS** managed PostgreSQL vs self-hosted, **Docker Compose** multi-container orchestration with EBS volumes and env vars. **Project:** FastAPI + PostgreSQL on EC2.

### Container Orchestration (5–6)
**EKS** architecture, eksctl cluster creation, deploy manifests, **AWS Load Balancer Controller** for ALB/NLB, **IRSA** for pod permissions. **Project:** Migrate K8s app to EKS.

### Infrastructure as Code (7–8)
**Terraform** workflow, resources, variables, outputs, remote state with S3 + DynamoDB locking, community modules. **Project:** EKS cluster via Terraform.

### Capstone Platform (9–11)
**GitHub Actions** CI/CD pipeline → **ECR** → EKS, **HPA** auto-scaling, **CloudWatch Container Insights**, production repo structure. **Project:** Full microservices platform.

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
├── aws-fundamentals/               # Cloud concepts → EC2 (more topics added as we go)
│   ├── cloud-concepts/
│   │   └── 01_cloud_concepts.md
│   └── ec2/
│       ├── 02_ec2.md
│       └── (future code)
│
├── ec2-app-deployment/             # RDS → Docker Compose → S3 backups
│   ├── rds/
│   │   └── 01_rds.md
│   └── docker-compose/
│       ├── 02_docker_compose_deploy.md
│       └── (future code)
│
├── eks-migration/                  # EKS architecture → deployment → IRSA
│   ├── eks-basics/
│   │   └── 01_eks_basics.md
│   └── eks-deployment/
│       ├── 02_eks_deployment.md
│       └── (future code)
│
├── terraform-eks/                  # Terraform workflow → state → modules
│   ├── terraform-fundamentals/
│   │   └── 01_terraform_fundamentals.md
│   └── terraform-state-modules/
│       ├── 02_terraform_state_modules.md
│       └── (future code)
│
└── portfolio-project/              # CI/CD → HPA → monitoring → documentation
    ├── cicd-ecr/
    │   └── 01_cicd_ecr.md
    ├── hpa-monitoring/
    │   └── 02_hpa_monitoring.md
    └── repo-structure/
        ├── 03_repo_structure.md
        └── (future code)
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
| **Orchestration** | Docker Compose, Kubernetes / EKS |

---

## 📚 Detailed Learnings

<details>
<summary><strong>1–2: Cloud Concepts → EC2</strong></summary>

- Cloud Computing concepts (IaaS vs PaaS vs SaaS) and the Well-Architected Framework
- **IAM** — Users, groups, roles, policies, and least-privilege principles
- **EC2** — Instance types, AMIs, key pairs (SSH/RSA), user data, instance metadata, security groups, Elastic IP
- **VPC** — CIDR blocks, subnets, route tables, Internet Gateway, NAT Gateway/Instance
- **EBS** — Volume types, attaching volumes, snapshots
- **S3** — Bucket creation, bucket policies, versioning, lifecycle rules
- **Security Groups** vs NACLs — Stateful vs stateless firewall rules
- **CloudWatch** — Metrics, log groups, log streams, alarms, CloudWatch agent

**Project:** Deploy K8s app (frontend + backend + PostgreSQL) on EC2 via kind.

</details>

<details>
<summary><strong>3–4: RDS → Docker Compose</strong></summary>

- **RDS** — Managed PostgreSQL, Multi-AZ, read replicas, RDS vs self-hosted comparison
- **Docker Compose** — Multi-container orchestration on a single EC2 host
- **FastAPI** backend with **PostgreSQL** — Containerized with persistent EBS volumes
- **S3** for static asset hosting and automated database backups
- Environment variable management and secrets handling
- Security group configuration for app access (HTTP 80)

**Project:** FastAPI + PostgreSQL running on EC2 via Docker Compose, with S3 for static assets/backups.

</details>

<details>
<summary><strong>5–6: EKS Basics → EKS Deployment</strong></summary>

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
<summary><strong>7–8: Terraform Fundamentals → State & Modules</strong></summary>

- **Terraform workflow** — `init`, `plan`, `apply`, `destroy`
- **Providers** — AWS provider configuration
- **Community modules** — `terraform-aws-modules/vpc/aws`, `terraform-aws-modules/eks/aws`
- **State management** — Local state → Remote state (S3 + DynamoDB locking)
- **Variables, outputs, and data sources**
- **Resource dependencies** and `terraform graph`

**Project:** Provision a full EKS infrastructure (VPC, cluster, node groups, IAM roles) as reusable Terraform code.

</details>

<details>
<summary><strong>9–11: CI/CD → HPA → Repo Structure</strong></summary>

- **GitHub Actions** — CI/CD pipeline building Docker images → pushing to ECR → deploying to EKS
- **Amazon ECR** — Private container registry with IAM authentication
- **Horizontal Pod Autoscaler** — CPU/memory-based auto-scaling
- **CloudWatch Container Insights** — Cluster-level monitoring with performance dashboards
- **Production repository structure** — Clear separation of infra and app code
- **README documentation** — Architecture diagram, deployment instructions, screenshots

**Project:** A single GitHub repository combining everything into a production-ready, CI/CD-automated, auto-scaled microservices platform on EKS.

</details>

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/yourusername/complete-aws.git
cd complete-aws

# Start with fundamentals
code aws-fundamentals/cloud-concepts/01_cloud_concepts.md
```

Each topic is a self-contained `.md` file with concepts explained, CLI commands, and a project to build.

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
  <sub>From fundamentals to production microservices — one topic at a time.</sub>
</p>
