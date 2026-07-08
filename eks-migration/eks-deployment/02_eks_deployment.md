# 02 — Deploying Apps on EKS

## Deploying Manifests
Same Kubernetes manifests work on EKS — apply directly:
```bash
kubectl apply -f manifests/
```

PostgreSQL typically uses a **StatefulSet with PVC** (EBS-backed):
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  template:
    spec:
      containers:
      - image: postgres:15
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

## AWS Load Balancer Controller
- Automatically provisions ALB/NLB when you create an Ingress or LoadBalancer Service
- Install via Helm:
```bash
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller
```

- After install, an Ingress creates an ALB automatically:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: alb
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
```

## IAM Roles for Service Accounts (IRSA)
- Fine-grained permissions for pods (e.g., pod reads from S3)
- Associate an IAM role with a Kubernetes service account
- Pods inherit the role via the service account

## Accessing the App
```bash
# Get the ALB DNS name
kubectl get ingress
```

## Key Takeaways
- Existing K8s manifests work on EKS with minimal changes
- AWS Load Balancer Controller automates ALB/NLB provisioning
- Use IRSA for pod-level IAM permissions
