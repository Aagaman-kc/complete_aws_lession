# 01 — EKS Architecture & Cluster Creation

## What is EKS?
- Amazon Elastic Kubernetes Service — managed Kubernetes
- AWS runs the **control plane** (API server, etcd, scheduler) — you pay for it
- **Worker nodes** run on EC2 in your account (managed or self-managed node groups)

## EKS Architecture
```
EKS Control Plane (AWS-managed)
       │
       ▼
Worker Nodes (EC2 in your account)
  ┌──────────┐
  │ kubelet  │
  │ kube-prox│
  │ coredns  │
  │ your Pods│
  └──────────┘
```

## Creating a Cluster with eksctl
```bash
eksctl create cluster \
  --name my-cluster \
  --region us-east-1 \
  --nodegroup-name standard-nodes \
  --node-type t3.medium \
  --nodes 2 \
  --managed
```

## Verify
```bash
kubectl get nodes
kubectl get pods -A
```

## kubectl Context Management
```bash
# List contexts
kubectl config get-contexts

# Switch context
kubectl config use-context <cluster-name>

# View current context
kubectl config current-context
```

## Key Takeaways
- EKS = managed K8s, control plane is AWS's responsibility
- Worker nodes are regular EC2 instances joined to the cluster
- `eksctl` is the fastest way to create an EKS cluster
