# 02 — Docker Compose Deployment on EC2

## EBS (Elastic Block Store)
- Block storage volumes attached to EC2
- Persist data even if container restarts
- Common types: gp3 (general purpose), io2 (high performance)
- Attach via `aws ec2 attach-volume` or specify in launch template

## Docker Compose on EC2
Run multi-container apps using a single `docker-compose.yml`:

```yaml
services:
  backend:
    build: .
    ports:
      - "80:80"
    environment:
      - DB_HOST=postgres
      - DB_NAME=myapp
      - DB_USER=postgres
      - DB_PASSWORD=secret
  postgres:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

## Environment Variables & Secrets
- Pass via `environment:` key in docker-compose.yml
- For secrets: use `.env` file or AWS Secrets Manager
- Never hardcode secrets in source code

## Deployment Steps
```bash
# SSH into EC2, then:
docker compose up -d
```

## S3 Backup (Optional)
```bash
pg_dump -h localhost -U postgres mydb > dump.sql
aws s3 cp dump.sql s3://my-backup-bucket/db-$(date +%F).sql
```

## Security Group
Open port 80 to `0.0.0.0/0` for HTTP access:
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
```

## Key Takeaways
- Docker Compose simplifies multi-container management on a single host
- EBS volumes provide persistence for container data
- Use environment variables for configuration, never hardcode secrets
