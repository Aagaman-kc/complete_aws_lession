# 02 — State Management & Modules

## Terraform State
- Terraform tracks resources in a **state file** (`terraform.tfstate`)
- State maps config to real-world resources
- By default: **local state** (stored on disk)

## Remote State (Production)
Store state remotely for team collaboration:
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "eks/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}
```

- S3 stores the state file (durable, shared)
- DynamoDB provides **state locking** (prevents concurrent modifications)

## Modules
Reusable configs from the Terraform Registry:
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"
  azs  = ["us-east-1a", "us-east-1b"]
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.0.0"

  cluster_name    = "my-cluster"
  cluster_version = "1.27"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets
}
```

## Dependency Graph
```bash
terraform graph | dot -Tpng > graph.png
```
Visualize resource dependencies and creation order.

## Key Takeaways
- Local state is fine for learning; remote state (S3 + DynamoDB) is production-ready
- Modules from the registry save months of boilerplate
- Always run `terraform destroy` to avoid ongoing charges
