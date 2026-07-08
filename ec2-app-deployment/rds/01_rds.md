# 01 — RDS (Relational Database Service)

## What is RDS?
- Managed database service for MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Aurora
- AWS handles: backups, patching, replication, failover
- No SSH access to the DB server — fully managed

## RDS vs Self-Hosted on EC2

| Aspect | RDS | PostgreSQL on EC2 |
|--------|-----|-------------------|
| Backups | Automated, point-in-time recovery | Manual (pg_dump) |
| Scaling | Vertical (instance size) + Read Replicas | Manual |
| High Availability | Multi-AZ (synchronous standby) | You build it |
| Maintenance | AWS handles patching | You handle it |
| Cost | Higher (managed premium) | Lower (just EC2 + EBS) |

## Creating an RDS Instance
```bash
aws rds create-db-instance \
  --db-instance-identifier mydb \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password <password> \
  --allocated-storage 20
```

## Connecting from EC2
- Launch RDS in a **private subnet** (not publicly accessible)
- EC2 in the same VPC connects via the RDS endpoint
- Security group: allow port 5432 from EC2's security group

## Key Takeaways
- RDS = managed DB, good for production
- For learning: self-hosted PostgreSQL in Docker is simpler and cheaper
