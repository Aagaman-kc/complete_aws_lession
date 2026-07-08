# Day 5 – Portfolio Project: Production-Ready Microservices Platform

## Concepts Covered
- **GitHub Actions** – CI/CD pipeline (build → push to ECR → deploy to EKS)
- **Amazon ECR** – Private container registry
- **Horizontal Pod Autoscaler (HPA)** – CPU/memory-based auto-scaling
- **CloudWatch Container Insights** – EKS cluster monitoring with performance dashboards
- **Terraform + GitHub Actions** – Automated infrastructure provisioning
- **Production Repository Structure** – infra/ vs app/ separation
- **Documentation** – Architecture diagrams, deployment walkthrough

## Hands-On: Production Microservices Platform

### Repository Structure
```
├── infrastructure/          # Terraform code for EKS, VPC, ECR
│   ├── providers.tf
│   ├── vpc.tf
│   ├── eks.tf
│   ├── ecr.tf
│   └── outputs.tf
├── app/                     # FastAPI backend + frontend + PostgreSQL manifests
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── postgres-statefulset.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   └── ingress.yaml
├── .github/workflows/       # CI/CD pipeline
│   └── deploy.yml
└── README.md
```

### Terraform (infrastructure/)
- VPC with public/private subnets
- EKS cluster with managed node group
- IAM roles for service accounts
- ECR repositories for backend and frontend images

### CI/CD Pipeline (.github/workflows/deploy.yml)
On push to `main`:
1. Build Docker images, tag with git SHA
2. Push to Amazon ECR
3. Update Kubernetes deployments via `kubectl set image` (or kustomize/Helm)
4. Optional: Run `terraform plan` for full automation

### Application (app/)
- FastAPI backend and frontend
- PostgreSQL StatefulSet with persistent volumes
- Secrets, ConfigMaps, Ingress (AWS Load Balancer Controller)
- Horizontal Pod Autoscaler

### Monitoring
Enabled CloudWatch Container Insights via a ConfigMap.

### Documentation
Detailed README explaining architecture, deployment steps, architecture diagram, and screenshots.

### Deployment
- Deployed to personal AWS account
- Verified functionality
- Ran `terraform destroy` to avoid ongoing charges

## Deliverable
A GitHub repository demonstrating:
- **AWS** – VPC, EKS, ECR, IAM
- **Kubernetes** – All core resources (Deployments, StatefulSets, Services, Ingress, HPA)
- **CI/CD** – GitHub Actions automation
- **Infrastructure as Code** – Terraform
- **Monitoring** – CloudWatch Container Insights

## Key Commands
```bash
# Build & push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t backend .
docker tag backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/backend:latest

# Deploy to EKS
kubectl set image deployment/backend backend=<account>.dkr.ecr.us-east-1.amazonaws.com/backend:latest
```
