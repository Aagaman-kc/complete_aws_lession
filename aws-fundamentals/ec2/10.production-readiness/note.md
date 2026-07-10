# 10: Production Readiness & Observability — Full Walkthrough

**Goal:** Transform the existing Ingress-based stack into a production-grade system with RBAC security, resource governance, health probes, Prometheus/Grafana monitoring via Helm, and HPA autoscaling.

**Stack:** Frontend (FastAPI + httpx) → Backend (FastAPI + psycopg2) → PostgreSQL (StatefulSet + PVC) + Ingress (NGINX) + Prometheus/Grafana (Helm) + HPA

---

## Architecture

```
         User (port 30080)
                │
                ▼
        ┌───────────────┐
        │ NGINX Ingress  │  path-based routing
        │ (NodePort 30080)│  /  → frontend-service:80
        └───────┬───────┘  /api → backend-service:80
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
 frontend-service   backend-service
    (ClusterIP)       (ClusterIP)
        │               │
        ▼               ▼
   Frontend Pod      Backend Pods ×2
                         │ (RBAC: ServiceAccount + Role)
                         │
                    ┌────┘
                    ▼
              postgres (headless)
                    │
                    ▼
              PostgreSQL StatefulSet
                    │
                    ▼
              PVC (1Gi)

 Monitoring Stack (Helm-installed):
 ┌─────────────────────────────────────┐
 │  Prometheus ← Grafana ← Alertmanager│
 │  (scrapes metrics)  (dashboards)    │
 └─────────────────────────────────────┘
```

**What Phase 10 adds beyond Phase 9:**
| Enhancement | Why It Matters |
|-------------|---------------|
| **Liveness/Readiness probes** | K8s knows when a container is alive vs ready to serve traffic |
| **Resource requests/limits** | Guarantees minimum resources, prevents noisy neighbors |
| **RBAC** | Backend gets a dedicated ServiceAccount with least-privilege permissions |
| **Prometheus + Grafana** | Cluster-wide metrics collection and visualization |
| **Helm** | Package manager for K8s — installs complex stacks (Prometheus stack) in one command |
| **HPA** | Auto-scales backend under CPU load |
| **Production namespace isolation** | `production` and `monitoring` namespaces keep concerns separated |

---

## Step 1 — Directory Setup & Cluster

### Directory Structure

```powershell
cd C:\projects\kubernetes_lab
mkdir 10.production-readiness
cd .\10.production-readiness
mkdir k8s, backend, frontend -Force
```

### Kind Cluster with Port Mappings (NodePort 30080)

`kind-config.yaml`:
```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30080
    hostPort: 30080
    protocol: TCP
  - containerPort: 30443
    hostPort: 30443
    protocol: TCP
```

Port 30080 is the HTTP entry point. Port 30443 is reserved for HTTPS. The `extraPortMappings` map host ports directly to the container so the Ingress controller is reachable without `kubectl port-forward`.

```powershell
kind delete cluster --name k8-lab
kind create cluster --name k8-lab --config kind-config.yaml
```

### Namespaces

```powershell
kubectl create namespace production
kubectl create namespace monitoring
kubectl config set-context --current --namespace=production
```

We keep `production` for the application and `monitoring` for Prometheus/Grafana. This is a real-world pattern — monitoring infra in its own namespace.

---

## Step 2 — ConfigMap & Secret

`k8s/config-and-secret.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
  namespace: production
data:
  POSTGRES_DB: mydb
  POSTGRES_USER: admin
  POSTGRES_HOST: postgres
  POSTGRES_PORT: "5432"
---
apiVersion: v1
kind: Secret
metadata:
  name: backend-secret
  namespace: production
type: Opaque
data:
  POSTGRES_PASSWORD: YWRtaW4xMjM=   # admin123
```

**ConfigMap** holds non-sensitive data (DB name, user, host, port). **Secret** holds sensitive data (password) base64-encoded (not encrypted — just obfuscated; real encryption requires KMS or external secrets store).

Both are injected into Pods via `configMapKeyRef` and `secretKeyRef` in the Deployment spec. This keeps credentials out of the container image.

---

## Step 3 — PostgreSQL StatefulSet with Health Checks & Resources

`k8s/postgres.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: production
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
  clusterIP: None            # Headless — enables StatefulSet DNS
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: production
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          valueFrom:
            configMapKeyRef:
              name: backend-config
              key: POSTGRES_DB
        - name: POSTGRES_USER
          valueFrom:
            configMapKeyRef:
              name: backend-config
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: backend-secret
              key: POSTGRES_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 256Mi
        livenessProbe:
          exec:
            command: ["pg_isready", "-U", "admin", "-d", "mydb"]
          initialDelaySeconds: 10
          periodSeconds: 5
        readinessProbe:
          exec:
            command: ["pg_isready", "-U", "admin", "-d", "mydb"]
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
```

### Why Resource Requests/Limits Are Needed

- **requests** — Kubernetes uses this to schedule the Pod on a node that has at least this much capacity available. It's a guarantee, not a hard cap.
- **limits** — The container cannot exceed this amount. If it tries, it gets throttled (CPU) or OOM-killed (memory).
- Without them, a single Pod can starve others on the same node — the "noisy neighbor" problem.

### Why Liveness and Readiness Probes Matter

| Probe | Purpose | What Happens on Failure |
|-------|---------|------------------------|
| **livenessProbe** | "Is the container alive?" | Kubelet restarts the container (CrashLoop prevention) |
| **readinessProbe** | "Is the container ready to serve traffic?" | Pod is removed from Service endpoints (no traffic until ready) |

For Postgres, we use `exec` probes with the `pg_isready` utility — it exits 0 if the database is accepting connections. This is more accurate than a TCP socket check because Postgres can accept TCP connections but still be recovering.

- `initialDelaySeconds: 10` — Wait 10s before first probe (Postgres needs time to start).
- `periodSeconds: 5` — Check every 5 seconds.

### Headless Service

`clusterIP: None` creates a headless service. For StatefulSets, this enables stable DNS names like `postgres-0.postgres.production.svc.cluster.local` — each Pod gets its own A record instead of the Service getting one VIP. The backend connects to `postgres` (the headless service name), which resolves to the set of Pod IPs.

---

## Step 4 — Backend with RBAC, Health Checks & Resources

`k8s/backend.yaml` combines four resources:

### ServiceAccount, Role, RoleBinding

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: backend-sa
  namespace: production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: backend-role
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets", "pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: backend-rb
  namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: backend-role
subjects:
- kind: ServiceAccount
  name: backend-sa
  namespace: production
```

**RBAC Concepts:**

| Resource | Purpose |
|----------|---------|
| **ServiceAccount** | Identity for the backend Pod (not a human user) |
| **Role** | Set of permissions (rules) — what actions on which resources |
| **RoleBinding** | Grants the Role to a ServiceAccount (binds identity to permissions) |

This Role grants `get`, `list`, `watch` on `configmaps`, `secrets`, and `pods` in the `production` namespace only. This follows the **principle of least privilege** — the backend can read config and inspect pods, but cannot create, update, or delete anything. If the backend is compromised, the blast radius is limited to read-only access within one namespace.

**Why use `Role` + `RoleBinding` instead of `ClusterRole` + `ClusterRoleBinding`?**
- `Role` is namespace-scoped. It only grants access within `production`.
- `ClusterRole` is cluster-wide. We don't need that here.
- If you had a cross-cutting concern (e.g., reading nodes), you'd use a ClusterRole.

### Deployment with Probes, Resources, and Env Injection

```yaml
spec:
  replicas: 2
  template:
    spec:
      serviceAccountName: backend-sa
      containers:
      - name: api
        image: fastapi-backend:2.0
        ports:
        - containerPort: 80
        env:
        - name: POSTGRES_HOST
          valueFrom:
            configMapKeyRef:
              name: backend-config
              key: POSTGRES_HOST
        # ... (POSTGRES_DB, POSTGRES_USER, POSTGRES_PORT from ConfigMap)
        # ... (POSTGRES_PASSWORD from Secret)
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
          limits:
            cpu: 200m
            memory: 128Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 3
          periodSeconds: 5
```

**Key details:**
- `serviceAccountName: backend-sa` — Pod runs under this identity (default would be `default` SA with no permissions).
- **HTTP probes** — Unlike Postgres (exec), here we use `httpGet` on the root path `/`. FastAPI returns 200 at `/`, so this works perfectly.
- **2 replicas** — High availability. If one fails, traffic routes to the other.
- **Env injection** — Values from ConfigMap (`POSTGRES_HOST`, `POSTGRES_DB`, etc.) and Secret (`POSTGRES_PASSWORD`) are injected as environment variables. The app reads them with `os.getenv()`.

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: production
spec:
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

Stable ClusterIP. The frontend (and Ingress) call `backend-service:80`.

---

## Step 5 — Frontend with Health Checks & Resources

`k8s/frontend.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: production
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: web
        image: frontend:1.0
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
          limits:
            cpu: 200m
            memory: 128Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 3
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: production
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

Same pattern — 1 replica (single frontend is sufficient for this demo), probes, and resource limits.

---

## Step 6 — Ingress

`k8s/ingress.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: main-ingress
  namespace: production
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

Same Ingress from Phase 9 — path-based routing. The Ingress controller (NGINX) runs in the `ingress-nginx` namespace and is exposed via NodePort 30080, which maps to the kind port mapping.

---

## Step 7 — Application Code

### `backend/main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import psycopg2
import os

def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        database=os.getenv("POSTGRES_DB", "mydb"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "admin123"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create table and seed data
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        content TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    )""")
    cur.execute("SELECT COUNT(*) FROM messages")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO messages (content) VALUES ('Hello from PostgreSQL!')")
    conn.commit()
    cur.close()
    conn.close()
    yield
    # Shutdown
    print("Application is shutting down.")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT content, created_at FROM messages ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"message": row[0], "time": row[1].isoformat()}
    return {"message": "no data", "time": ""}
```

**Changes from Phase 9:**
- Uses the modern `lifespan` pattern (FastAPI `@asynccontextmanager`) instead of the deprecated `@app.on_event("startup")`.
- On startup, connects to PostgreSQL via environment variables, creates the `messages` table if it doesn't exist, and seeds "Hello from PostgreSQL!" if empty.
- The `/` endpoint reads the latest message and returns it as JSON.
- This endpoint is used by both the frontend (via proxy) and the liveness/readiness probes (`httpGet: path: /`).

### `frontend/main.py`

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx

app = FastAPI()
BACKEND_URL = "http://backend-service:80"

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>K8s Production App</title></head>
    <body>
        <h1>Production&#8209;grade Kubernetes App</h1>
        <div id="output">Loading...</div>
        <script>
            fetch('/api')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('output').innerHTML =
                        `<p><strong>Message:</strong> ${data.message}</p>
                         <p><strong>Time:</strong> ${data.time}</p>`;
                })
                .catch(err => {
                    document.getElementById('output').innerText = 'Error: ' + err;
                });
        </script>
    </body>
    </html>
    """

@app.get("/api")
async def proxy_api():
    async with httpx.AsyncClient() as client:
        resp = await client.get(BACKEND_URL)
        return resp.json()
```

The frontend serves a simple HTML page at `/`. The page's JavaScript fetches `/api` (relative path, which goes through the Ingress to `backend-service`), and displays the backend response. The frontend also exposes `/api` as a pass-through proxy to the backend using `httpx.AsyncClient`.

### Dockerfiles

Both backend and frontend use the same Dockerfile pattern:
```dockerfile
FROM python:3.11-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

- `python:3.11-alpine` — Minimal base image (~50MB), reducing attack surface and build time.
- `COPY requirements.txt` before `COPY main.py` — Docker layer caching. If `requirements.txt` hasn't changed, the `RUN pip install` step uses the cached layer, making rebuilds faster.

---

## Step 8 — Build, Load, and Deploy

### Build Docker Images

```powershell
cd backend
docker build -t fastapi-backend:2.0 .
kind load docker-image fastapi-backend:2.0 --name k8-lab
cd ..

cd frontend
docker build -t frontend:1.0 .
kind load docker-image frontend:1.0 --name k8-lab
cd ..
```

`kind load docker-image` makes locally built images available to the kind cluster nodes. Without this, kind would try to pull from Docker Hub and fail with `ErrImagePull`.

### Apply Manifests

```powershell
kubectl apply -f k8s/config-and-secret.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
```

### Wait for Postgres

```powershell
kubectl wait --for=condition=ready pod postgres-0 --timeout=60s
```

### Install Ingress Controller

```powershell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx wait --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s
```

### Patch Ingress Service to NodePort 30080

```powershell
kubectl -n ingress-nginx patch svc ingress-nginx-controller -p '{"spec":{"type":"NodePort","ports":[{"name":"http","port":80,"targetPort":80,"nodePort":30080},{"name":"https","port":443,"targetPort":443,"nodePort":30443}]}}'
```

This explicitly sets nodePort 30080 for HTTP and 30443 for HTTPS. Kind's `extraPortMappings` in `kind-config.yaml` maps host port 30080 to container port 30080, and the Ingress controller's NodePort service routes container port 80 to nodePort 30080.

### Apply Ingress

```powershell
kubectl apply -f k8s/ingress.yaml
```

### Test

```
http://localhost:30080/
```

You should see "Hello from PostgreSQL!" with a timestamp. This confirms the full path:
```
Browser → Host:30080 → Kind NodePort → Ingress Controller → path-based routing
  ├── / → frontend-service → Frontend Pod (HTML + JS)
  └── /api → backend-service → Backend Pod → PostgreSQL
```

---

## Step 9 — Helm, Prometheus & Grafana

### Why Helm?

Helm is the package manager for Kubernetes. Instead of writing dozens of YAML files for Prometheus, Grafana, Alertmanager, ServiceMonitors, RBAC rules, etc., we use a single command:

```powershell
helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring
```

This installs the entire **kube-prometheus-stack** which includes:
- **Prometheus** — Metrics collection and storage
- **Grafana** — Visualization (dashboards)
- **Alertmanager** — Alert routing and notification
- **kube-state-metrics** — Cluster state metrics (deployments, pods, etc.)
- **node-exporter** — Node-level metrics (CPU, memory, disk)
- **Prometheus Operator** — Manages Prometheus instances via custom resources

### Install Helm

On Windows, use winget:
```powershell
winget install helm.helm
```

After installation, **restart your terminal** (the PATH environment variable needs refreshing).

Verify:
```powershell
helm version
# version.BuildInfo{Version:"v4.x.x", ...}
```

### Add Prometheus Repository & Install

```powershell
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring
```

Wait for pods:
```powershell
kubectl get pods -n monitoring -w
# (Ctrl+C once all are Running)
```

Expected pods:
```
alertmanager-monitoring-kube-prometheus-alertmanager-0    2/2  Running
monitoring-grafana-xxxxxxxxx-xxxxx                       3/3  Running
monitoring-kube-prometheus-operator-xxxxxxxxx-xxxxx      1/1  Running
monitoring-kube-state-metrics-xxxxxxxxx-xxxxx            1/1  Running
monitoring-prometheus-node-exporter-xxxxx                1/1  Running
prometheus-monitoring-kube-prometheus-prometheus-0       2/2  Running
```

### Access Grafana

```powershell
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```

Open http://localhost:3000

**Login:** `admin`

**Password:** retrieve with:
```powershell
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl get secret -n monitoring monitoring-grafana -o jsonpath="{.data.admin-password}")))
```

(On Linux/Mac: `kubectl get secret -n monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 --decode`)

### Explore Dashboards

Go to **Dashboards → Browse** and select a pre-built dashboard:

| Dashboard | What It Shows |
|-----------|---------------|
| **Kubernetes / Compute Resources / Pod** | CPU, memory, network per pod |
| **Kubernetes / Compute Resources / Namespace** | Resource usage grouped by namespace (production vs monitoring) |
| **Kubernetes / Networking / Pod** | Network I/O per pod |
| **Node Exporter / Nodes** | Node-level CPU, memory, disk |

Select the `production` namespace in the namespace dropdown to see your backend, frontend, and postgres pods.

### Understanding the Monitoring Stack

```
                          ┌──────────────┐
                          │   Grafana     │  UI for dashboards & alerts
                          │ port 3000     │
                          └──────┬───────┘
                                 │ queries PromQL
                                 ▼
                    ┌──────────────────────┐
                    │     Prometheus        │  Time-series DB + query engine
                    │  port 9090            │  Stores all metrics
                    └──────┬───────────┬───┘
                           │           │
                    scrape │           │ scrape
                           ▼           ▼
              ┌─────────────────┐  ┌─────────────────┐
              │ kube-state-metrics│  │ node-exporter    │
              │ (cluster state)  │  │ (node metrics)   │
              └─────────────────┘  └─────────────────┘
                           │
                    scrape │
                           ▼
              ┌─────────────────────┐
              │ Your App Pods        │
              │ (CPU, memory, etc.)  │  Collected via kubelet / cAdvisor
              └─────────────────────┘
```

- **cAdvisor** (built into kubelet) — Exposes container-level CPU, memory, filesystem, network metrics. Prometheus scrapes these from each node's kubelet.
- **kube-state-metrics** — Generates metrics about the state of Kubernetes objects (e.g., `kube_deployment_status_replicas`, `kube_pod_status_phase`).
- **node-exporter** — Hardware and OS metrics for each node (disk I/O, network stats, load average).

---

## Step 10 — Horizontal Pod Autoscaler (HPA)

### Install Metrics Server

HPA needs per-pod CPU/memory metrics. The Metrics Server collects these from kubelets and exposes them through the Kubernetes Metrics API.

```powershell
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Kind workaround:** Kind uses self-signed TLS certificates for kubelets. Metrics Server needs `--kubelet-insecure-tls` to accept them:
```powershell
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

Wait for it:
```powershell
kubectl -n kube-system wait --for=condition=ready pod -l k8s-app=metrics-server --timeout=60s
```

Verify:
```powershell
kubectl top pods -n production
# NAME                       CPU(cores)   MEMORY(bytes)
# backend-xxxxx-xxxxx        1m           32Mi
# backend-xxxxx-xxxxx        2m           34Mi
# frontend-xxxxx-xxxxx       1m           30Mi
# postgres-0                 3m           45Mi
```

### Create HPA

```powershell
kubectl autoscale deployment backend --cpu-percent=50 --min=2 --max=5 -n production
```

This creates an HPA that:
- Targets 50% average CPU utilization across all backend pods
- Scales between 2 and 5 replicas
- Uses the formula: `desiredReplicas = ceil[currentReplicas × (currentMetric / targetMetric)]`

Check it:
```powershell
kubectl get hpa -n production
# NAME      REFERENCE            TARGETS   MINPODS   MAXPODS   REPLICAS
# backend   Deployment/backend   0%/50%    2         5         2
```

### Test HPA with Load Generator

```powershell
kubectl run load-generator --image=busybox -it --rm --restart=Never -n production -- sh -c "while true; do wget -q -O- http://backend-service; done"
```

In another terminal:
```powershell
kubectl get hpa -n production -w
# NAME      TARGETS   REPLICAS
# backend   85%/50%   2
# backend   85%/50%   4    ← scaled up!
# backend   92%/50%   4
# backend   55%/50%   4
```

Stop the load generator (Ctrl+C or `kubectl delete pod load-generator -n production`). After the 5-minute cooldown, replicas will scale back down to 2.

---

## Production Best Practices — Summary

| Practice | Implemented In | Why |
|----------|---------------|-----|
| **Resource requests** | Backend, Frontend, Postgres | Guarantees minimum resources for scheduling |
| **Resource limits** | Backend, Frontend, Postgres | Prevents resource starvation (noisy neighbor) |
| **Liveness probe** | Backend, Frontend, Postgres | Kubelet restarts unhealthy containers |
| **Readiness probe** | Backend, Frontend, Postgres | Service stops sending traffic to unready pods |
| **RBAC** | Backend | Least-privilege ServiceAccount — read-only access to configmaps/secrets/pods |
| **Namespace isolation** | production, monitoring | Logical separation of app and monitoring |
| **Helm** | Prometheus/Grafana install | Reproducible, parameterized deployments |
| **Monitoring** | Prometheus + Grafana | Metrics collection and visualization |
| **HPA** | Backend | Auto-scales under CPU load |
| **Rolling updates** | Default strategy (25% max surge/unavailable) | Zero-downtime deployments |
| **Persistent storage** | Postgres PVC (1Gi) | Data survives pod restarts and rescheduling |

---

## Complete File Tree

```
10.production-readiness/
├── note.md                              ← You are here
├── kind-config.yaml                     ← Kind cluster with port mappings (30080, 30443)
├── k8s/
│   ├── config-and-secret.yaml           ← ConfigMap (DB config) + Secret (password)
│   ├── postgres.yaml                    ← Headless Service + StatefulSet (postgres:15-alpine, 1Gi PVC, probes, limits)
│   ├── backend.yaml                     ← ServiceAccount + Role + RoleBinding + Deployment ×2 + ClusterIP Service
│   ├── frontend.yaml                    ← Deployment ×1 + ClusterIP Service (probes, limits)
│   └── ingress.yaml                     ← NGINX Ingress (/ → frontend, /api → backend)
├── backend/
│   ├── main.py                          ← FastAPI with psycopg2 + PostgreSQL (lifespan pattern)
│   ├── requirements.txt                 ← fastapi, uvicorn, psycopg2-binary
│   └── Dockerfile                       ← python:3.11-alpine, exposes 80
└── frontend/
    ├── main.py                          ← FastAPI with httpx, serves HTML + proxies /api
    ├── requirements.txt                 ← fastapi, uvicorn, httpx
    └── Dockerfile                       ← python:3.11-alpine, exposes 80
```

---

## Mistakes & Fixes Log

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Helm `get-helm-3` script is bash, not PowerShell | Parse errors in `get_helm.ps1` | Use `winget install helm.helm` on Windows |
| `helm` not recognized after installation | `helm : The term 'helm' is not recognized` | Restart terminal — PATH wasn't refreshed |
| `base64` is a Linux command, not PowerShell | `base64 : The term 'base64' is not recognized` | Use `[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(...))` |
| Metrics Server not installed | HPA shows `cpu: <unknown>/50%` | `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml` |
| Metrics Server can't connect (kind self-signed certs) | Still `<unknown>` after install | Patch with `--kubelet-insecure-tls` |
| Grafana shows "No data" on dashboards | Empty graphs | Check namespace dropdown is `production` not `default`; generate traffic to see CPU usage |
| Prometheus data source missing in Grafana | Dashboards show error | Verify URL is `http://monitoring-kube-prometheus-prometheus.monitoring.svc:9090` and click "Save & test" |
| Images not loaded into kind | `ErrImagePull` / `ImagePullBackOff` | `kind load docker-image <tag> --name k8-lab` |
| Wrong namespace on Ingress resource | 404 on `localhost:30080` | Ensure Ingress is in `production` namespace |
| Frontend calls wrong backend URL | JS shows error | Frontend uses `http://backend-service:80` (Service DNS name) |
| `kubectl` context wrong | Pods not found in `production` | `kubectl config use-context kind-k8-lab` |

---

## Key Commands

| Command | Purpose |
|---------|---------|
| `kind delete cluster --name k8-lab && kind create cluster --name k8-lab --config kind-config.yaml` | Recreate cluster with port mappings |
| `kubectl apply -f k8s/` | Apply all manifests (order: config → postgres → backend → frontend → ingress) |
| `kubectl wait --for=condition=ready pod postgres-0 --timeout=60s` | Wait for PostgreSQL to be ready |
| `kubectl -n ingress-nginx wait --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s` | Wait for Ingress controller |
| `kubectl -n ingress-nginx patch svc ingress-nginx-controller -p '...'` | Set NodePort to 30080 |
| `docker build -t fastapi-backend:2.0 .` | Build backend image |
| `docker build -t frontend:1.0 .` | Build frontend image |
| `kind load docker-image fastapi-backend:2.0 --name k8-lab` | Load backend into kind |
| `kind load docker-image frontend:1.0 --name k8-lab` | Load frontend into kind |
| `winget install helm.helm` | Install Helm on Windows |
| `helm repo add prometheus-community https://prometheus-community.github.io/helm-charts` | Add Prometheus Helm repo |
| `helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring` | Install monitoring stack |
| `kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80` | Access Grafana locally |
| `[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String((kubectl get secret -n monitoring monitoring-grafana -o jsonpath="{.data.admin-password}")))` | Decode Grafana admin password (PowerShell) |
| `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml` | Install Metrics Server |
| `kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'` | Fix Metrics Server for kind |
| `kubectl autoscale deployment backend --cpu-percent=50 --min=2 --max=5 -n production` | Create HPA for backend |
| `kubectl get hpa -n production -w` | Watch HPA scaling live |
| `kubectl top pods -n production` | Real-time CPU/memory per pod |
| `kubectl run load-generator --image=busybox -it --rm --restart=Never -n production -- sh -c "while true; do wget -q -O- http://backend-service; done"` | Generate load to trigger HPA |

---

## Key Concepts

| Concept | Key Insight |
|---------|-------------|
| **Liveness Probe** | Tells K8s when to restart a container. Without it, a deadlocked process runs forever. |
| **Readiness Probe** | Tells K8s when a pod can serve traffic. Without it, a pod still starting gets requests and returns errors. |
| **Resource Requests** | Minimum resources guaranteed to a container. Required for HPA and QoS class assignment. |
| **Resource Limits** | Hard cap — container is throttled (CPU) or killed (memory) if it exceeds them. |
| **RBAC ServiceAccount** | Identity for a pod (not a person). Every pod runs under a SA. |
| **RBAC Role** | Namespace-scoped permissions. Grants only what's needed (least privilege). |
| **RBAC RoleBinding** | Binds a Role to subjects (ServiceAccounts, users, groups). |
| **Helm** | Package manager for K8s. One command installs a complex stack (Prometheus + Grafana + Alertmanager + ...). |
| **Prometheus** | Pull-based time-series metrics system. Scrapes targets, stores data, runs queries via PromQL. |
| **Grafana** | Visualization layer. Queries Prometheus and renders dashboards. Pre-built dashboards for K8s. |
| **kube-prometheus-stack** | Helm chart that bundles Prometheus Operator, Prometheus, Grafana, Alertmanager, node-exporter, kube-state-metrics. |
| **Metrics Server** | Required for HPA. Aggregates per-pod CPU/memory from kubelets. Needs `--kubelet-insecure-tls` in kind. |
| **HPA (HorizontalPodAutoscaler)** | Reads metrics from Metrics Server, computes desired replicas, updates Deployment. Scale-up is instant; scale-down has a 5-min cooldown. |
| **Headless Service** | `clusterIP: None`. For StatefulSets — each pod gets a stable DNS name. |
| **StatefulSet** | Stable identity, ordered creation, per-pod PVC via `volumeClaimTemplates`. |
| **ConfigMap + Secret** | External configuration injected as env vars. Keeps config out of the image. |
| **Ingress + NodePort** | Single entry point (host port 30080 → node port 30080 → container port 80). No port-forward needed. |
| **Namespace isolation** | `production` for app, `monitoring` for observability — prevents configuration conflicts and improves security. |

---

## Next Up — 🏆 Final Capstone

The Final Capstone ties everything together:
- Deploy the full stack on **AWS EKS** (managed Kubernetes)
- Implement a **CI/CD pipeline** with GitHub Actions (build → push → deploy on push)
- Add **canary deployments** with traffic splitting
- Document the entire system architecture

Let me know when you're ready for the capstone!
