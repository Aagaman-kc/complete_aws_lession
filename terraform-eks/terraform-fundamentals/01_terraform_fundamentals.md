# 01 — Terraform Fundamentals

## What is Terraform?
- Infrastructure as Code (IaC) tool by HashiCorp
- Declarative — you describe the desired state, Terraform makes it happen
- Providers: AWS, Azure, GCP, Kubernetes, etc.

## Workflow
```bash
terraform init      # Initialize providers and modules
terraform plan      # Preview changes
terraform apply     # Apply changes
terraform destroy   # Tear down everything
```

## Provider Configuration
```hcl
provider "aws" {
  region = "us-east-1"
}
```

## Resources
```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}
```

## Variables
```hcl
variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "my-cluster"
}
```

## Outputs
```hcl
output "cluster_endpoint" {
  value = aws_eks_cluster.main.endpoint
}
```

## Key Takeaways
- `init` → `plan` → `apply` is the core workflow
- Resources are declared, dependencies are automatic
- Variables and outputs make configs reusable
