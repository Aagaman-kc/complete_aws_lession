# Day 3 – Amazon EKS (Kubernetes on AWS)

## Concepts Covered
- **EKS Architecture** – Managed control plane, worker nodes (EC2 or Fargate)
- **IAM Roles for Service Accounts** – Fine-grained pod permissions
- **AWS Load Balancer Controller** – ALB/NLB provisioning for Ingress
- **kubectl context** – Switching between clusters

## Hands-On: Your K8s App on EKS

### 1. Install Tools
Installed `eksctl` and the latest AWS CLI.

### 2. Create EKS Cluster
```bash
eksctl create cluster \
  --name my-cluster \
  --region us-east-1 \
  --nodegroup-name standard-nodes \
  --node-type t3.medium \
  --nodes 2 \
  --managed
```

### 3. Verify Cluster
```bash
kubectl get nodes
```

### 4. Deploy Application
Applied all Kubernetes manifests from Phase 10 (backend, frontend, PostgreSQL StatefulSet, ConfigMaps, Secrets, Ingress).  
PostgreSQL uses a StatefulSet with PVC (EBS-backed) — production would use RDS, but this works for the exercise.

### 5. Load Balancer
Installed the AWS Load Balancer Controller (Helm chart) so the Ingress creates an ALB.  
Alternative: Changed the frontend Service to `type: LoadBalancer` for a simpler Classic ELB.

### 6. Access
Accessed the app via the ELB DNS name.

### 7. Observations
- IAM roles attached to worker nodes
- LoadBalancer provisioned automatically
- CloudWatch logs for the EKS control plane

## Deliverable
- Same app from Phase 10, running on EKS
- External Load Balancer providing access

## Key Commands
```bash
eksctl create cluster
kubectl apply -f manifests/
aws eks update-kubeconfig --region us-east-1 --name my-cluster
```
