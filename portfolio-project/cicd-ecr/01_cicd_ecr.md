# 01 — CI/CD with GitHub Actions & ECR

## Amazon ECR (Elastic Container Registry)
- Private Docker image registry on AWS
- Integrates with IAM for access control
- Push/pull via Docker CLI with `aws ecr get-login-password`

## GitHub Actions Pipeline
On push to `main`:
1. Build Docker images
2. Tag with git SHA
3. Push to ECR
4. Deploy to EKS

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE }}

      - name: Login to ECR
        run: |
          aws ecr get-login-password | docker login \
            --username AWS \
            --password-stdin ${{ secrets.AWS_ACCOUNT }}.dkr.ecr.us-east-1.amazonaws.com

      - name: Build and push
        run: |
          docker build -t backend ./app
          docker tag backend:latest ${{ secrets.AWS_ACCOUNT }}.dkr.ecr.us-east-1.amazonaws.com/backend:latest
          docker push ${{ secrets.AWS_ACCOUNT }}.dkr.ecr.us-east-1.amazonaws.com/backend:latest

      - name: Deploy to EKS
        run: |
          kubectl set image deployment/backend \
            backend=${{ secrets.AWS_ACCOUNT }}.dkr.ecr.us-east-1.amazonaws.com/backend:${{ github.sha }}
```

## ECR Commands
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t backend .
docker tag backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/backend:latest
```

## Key Takeaways
- GitHub Actions automates the build → push → deploy loop
- ECR is a private registry integrated with AWS IAM
- Tag images with git SHA for traceability
