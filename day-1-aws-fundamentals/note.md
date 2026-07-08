# Day 1 – AWS Fundamentals (VPC, EC2, IAM, S3, Security Groups)

## Concepts Covered
- **Cloud Computing** – IaaS vs PaaS vs SaaS, Well-Architected Framework
- **IAM** – Users, groups, roles, policies, least-privilege
- **EC2** – Instance types, AMIs, key pairs, user data, metadata
- **VPC** – CIDR, subnets, route tables, Internet Gateway, NAT
- **EBS** – Volume types, attach/detach, snapshots
- **S3** – Object storage, bucket policies, versioning, lifecycle
- **Security Groups** vs NACLs
- **CloudWatch** – Metrics, logs, alarms, agent

## Hands-On: Secure Web Server

### 1. VPC Setup
Created a VPC with 1 public subnet and 1 private subnet manually (or via VPC wizard).

### 2. EC2 Instance
Launched an Amazon Linux 2 instance in the public subnet with a key pair for SSH access.

### 3. Security Group
Attached a security group allowing SSH (22) and HTTP (80) from my IP.

### 4. Docker & Nginx
SSH'd into the instance, installed Docker, and ran an nginx container:
```bash
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
docker run -d -p 80:80 nginx
```

### 5. S3 Bucket
Created an S3 bucket for backups/assets and tested with AWS CLI:
```bash
aws s3 mb s3://my-secure-web-server-bucket
aws s3 ls
```

### 6. CloudWatch Agent
Installed and configured the CloudWatch agent to view system metrics and logs.

### 7. IAM User
Created an IAM user with programmatic access and attached `AdministratorAccess` (temporary, for learning).

## Deliverable
- Running EC2 instance serving an nginx web page
- CloudWatch logs streaming
- S3 bucket listed via AWS CLI

## Key Commands
```bash
aws ec2 run-instances
aws s3 ls
ssh -i key.pem ec2-user@<public-ip>
docker run -d -p 80:80 nginx
```
