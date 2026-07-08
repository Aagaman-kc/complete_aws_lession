# Day 4 – Terraform Basics (Infrastructure as Code)

## Concepts Covered
- **Terraform Workflow** – init, plan, apply, destroy
- **Providers** – AWS provider configuration
- **Resources** – aws_vpc, aws_subnet, aws_eks_cluster, aws_eks_node_group, aws_iam_role
- **Variables and Outputs** – Reusable configurations
- **State** – Local and remote (S3 + DynamoDB for locking)
- **Modules** – terraform-aws-modules/vpc/aws, terraform-aws-modules/eks/aws
- **Graph** – Visualizing resource dependencies with terraform graph

## Hands-On: EKS Cluster with Terraform

### 1. Install Terraform
Installed the Terraform CLI.

### 2. Configuration Files
Created the following Terraform files:
- `providers.tf` – AWS provider configuration
- `vpc.tf` – VPC module from the Terraform registry
- `eks.tf` – EKS module from the Terraform registry
- `outputs.tf` – Cluster endpoint, kubeconfig

### 3. Apply
```bash
terraform init
terraform plan
terraform apply
```

### 4. Connect & Deploy
```bash
aws eks update-kubeconfig --region us-east-1 --name <cluster-name>
kubectl apply -f ../manifests/
```

### 5. Remote State
Configured remote state in an S3 bucket with DynamoDB for state locking (production-ready).

### 6. Cleanup
```bash
terraform destroy
```

## Deliverable
- Fully functional EKS cluster provisioned entirely with Terraform
- Application manifest files ready for deployment

## Key Commands
```bash
terraform init
terraform apply
terraform destroy
```
