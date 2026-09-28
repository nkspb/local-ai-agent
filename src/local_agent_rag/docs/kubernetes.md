# Kubernetes

## Pods

A Pod is the smallest deployable unit in Kubernetes. It wraps one or more containers that share the same network namespace, IP address, and storage volumes. Containers in the same Pod can talk to each other over `localhost`.

Pods are ephemeral. When a Pod dies, it is not restarted in place; a controller creates a new Pod with a new IP address. For this reason you should rarely create Pods directly. Use a higher-level controller such as a Deployment, StatefulSet, or DaemonSet instead.

## Deployments and ReplicaSets

A Deployment declares the desired state for a set of identical, stateless Pods. The Deployment controller creates a ReplicaSet, and the ReplicaSet keeps the requested number of Pod replicas running.

When you change the Pod template (for example, a new image tag), the Deployment creates a new ReplicaSet and gradually shifts Pods from the old one to the new one. This is called a rolling update. Two fields control its speed:

- `maxSurge`: how many extra Pods can be created above the desired count during the update.
- `maxUnavailable`: how many Pods can be unavailable during the update.

You can check rollout progress with `kubectl rollout status deployment/<name>` and roll back to the previous revision with `kubectl rollout undo deployment/<name>`.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27
          ports:
            - containerPort: 80
```

## Services

A Service gives a group of Pods a stable virtual IP address and DNS name. It selects Pods by label and load-balances traffic across them, so clients do not need to track individual Pod IPs.

Common Service types:

- `ClusterIP` (default): reachable only from inside the cluster.
- `NodePort`: exposes the Service on a static port (30000-32767) on every node.
- `LoadBalancer`: provisions an external load balancer from the cloud provider.
- `ExternalName`: maps the Service to an external DNS name via a CNAME record.

Inside the cluster, a Service is reachable at `<service>.<namespace>.svc.cluster.local`.

## Probes

Kubernetes uses probes to check container health:

- **Liveness probe**: if it fails, the kubelet restarts the container.
- **Readiness probe**: if it fails, the Pod is removed from Service endpoints but is not restarted.
- **Startup probe**: delays liveness and readiness checks until a slow-starting app has booted.

## ConfigMaps and Secrets

ConfigMaps store non-sensitive configuration as key-value pairs. Secrets store sensitive data such as passwords and tokens. Both can be injected into Pods as environment variables or mounted as files. By default, Secrets are only base64-encoded, not encrypted, so enable encryption at rest in etcd for production clusters.

## Troubleshooting

- `CrashLoopBackOff`: the container starts and exits repeatedly. Check `kubectl logs <pod> --previous` to see output from the crashed run.
- `ImagePullBackOff`: the image name or tag is wrong, or the registry needs credentials (`imagePullSecrets`).
- `Pending`: the scheduler cannot place the Pod, usually because of insufficient CPU or memory, or unsatisfied node selectors or taints. Run `kubectl describe pod <pod>` and read the Events section.

## Team conventions

These are the internal conventions for our clusters:

- Production workloads run in the `prod-apps` namespace; staging uses `stg-apps`.
- Every Deployment must set `maxUnavailable: 0` and have at least 3 replicas in production.
- All containers must define CPU and memory requests. The default memory limit is 512Mi unless the owning team files an exception.
- The on-call rotation for cluster incidents is owned by the Platform team, reachable in the `#platform-oncall` channel.
