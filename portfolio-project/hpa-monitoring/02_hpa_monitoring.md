# 02 — Auto-Scaling & Monitoring

## Horizontal Pod Autoscaler (HPA)
- Automatically scales pod replicas based on CPU/memory metrics
- Requires **Metrics Server** installed in the cluster

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## CloudWatch Container Insights
- Collects metrics and logs from EKS clusters
- Enables performance dashboards in CloudWatch
- Enable via a ConfigMap:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-config
  namespace: amazon-cloudwatch
data:
  cluster.name: my-cluster
  logs.region: us-east-1
```

## Key Takeaways
- HPA enables automatic scaling based on demand
- Container Insights gives visibility into cluster performance
- Always verify HPA works with `kubectl get hpa`
