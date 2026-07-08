# Day 2 – Deploy a Real App on EC2 (Docker Compose + RDS)

## Concepts Covered
- **RDS** – Managed PostgreSQL (alternative to self-hosted)
- **EBS** – Block storage volumes for data persistence
- **Docker Compose** – Multi-container orchestration on a single host
- **Environment Variables & Secrets** – Managing configuration

## Hands-On: FastAPI + PostgreSQL on EC2

### 1. EC2 Instance Setup
Launched a t2.micro instance in the public subnet, installed Docker & Docker Compose.

### 2. Database Option
Chose **Option A**: PostgreSQL in a Docker container with a mounted volume for persistence.  
(Option B: Amazon RDS for PostgreSQL in the private subnet — noted the endpoint.)

### 3. Application Deployment
- Cloned the FastAPI backend code onto the instance
- Built the Docker image
- Created a `docker-compose.yml` with:
  - `backend` service (port 80)
  - `postgres` service (or RDS endpoint)
  - Environment variables for DB connection

### 4. Run
```bash
docker compose up -d
```

### 5. Security Group
Opened HTTP (80) to `0.0.0.0/0` and verified the app returns JSON at the public IP.

### 6. S3 Backup (Optional)
Wrote a small script to upload daily database dumps to S3.

## Deliverable
- Publicly accessible FastAPI backend connected to PostgreSQL
- Running on EC2 via Docker Compose

## Key Commands
```bash
docker compose up -d
aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 80 --cidr 0.0.0.0/0
aws rds create-db-instance --db-instance-identifier mydb --db-instance-class db.t3.micro --engine postgres
```
