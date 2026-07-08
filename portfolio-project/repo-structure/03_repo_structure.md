# 03 — Production Repository Structure & Documentation

## Recommended Layout
```
├── infrastructure/          # Terraform code
│   ├── providers.tf
│   ├── vpc.tf
│   ├── eks.tf
│   ├── ecr.tf
│   └── outputs.tf
├── app/                     # Kubernetes manifests
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── postgres-statefulset.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   └── ingress.yaml
├── .github/workflows/       # CI/CD
│   └── deploy.yml
└── README.md
```

## Why Separate infra/ and app/?
- **Separation of concerns** — infrastructure changes don't mix with app changes
- **Different lifecycles** — infra changes rarely, app changes frequently
- **Role clarity** — platform team owns infra, dev team owns app

## README Should Include
- Architecture diagram
- Prerequisites
- Deployment steps
- Cleanup instructions
- Screenshots of the running app

## Cost Warning
Always clean up after yourself:
```bash
terraform destroy
```
EKS clusters, Load Balancers, and NAT Gateways cost money even on Free Tier.

## Key Takeaways
- Keep infra and app code in separate directories
- Document everything for your future self and others
- Always destroy resources when done learning
