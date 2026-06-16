---
name: kubernetes-mesh-provisioner
description: >
  Kubernetes Mesh Provisioner atomic skill. Stands up an RKE2 cluster
  (server + agents) with Cilium CNI and the NVIDIA GPU device plugin, the
  Kubernetes parallel of swarm-mesh-provisioner. Idempotent — re-runnable.
domain: infrastructure
tags:
  - kubernetes
  - rke2
  - cilium
  - cluster
  - gpu
requires:
  - container-manager-mcp
  - tunnel-manager-mcp
---

# Kubernetes Mesh Provisioner Skill

Stateless atomic operation to establish a multi-node RKE2 Kubernetes cluster
with an eBPF dataplane — the Kubernetes counterpart of `swarm-mesh-provisioner`.
RKE2 is the CIS-hardened, real-etcd sibling of k3s in the SUSE/Rancher
ecosystem, so the same cluster scales from homelab to production without
re-platforming.

## Prerequisites

- `container-manager-mcp` — with `CONTAINER_MANAGER_TYPE=kubernetes` for node
  introspection (`list_nodes`, `update_node` labels/cordon) once the cluster is up.
- `tunnel-manager-mcp` — for remote command execution (RKE2 install + config) on
  each host over SSH.
- **NIC bonds applied first.** Cilium's tunnel data-path hits the same multi-NIC
  egress instability as Swarm's VXLAN unless each node has a deterministic
  canonical IP (run `nic-bond-provisioner` and validate cross-node reachability
  before this skill).

Every step is **idempotent**: check the desired state, act only on drift.

## Steps

### Step 1: Install RKE2 Server (control plane)
On the manager node **R820 (10.0.0.13)**:
- If `systemctl is-active rke2-server` is already active, skip to token retrieval.
- Otherwise install RKE2 server, write `/etc/rancher/rke2/config.yaml` with
  `cni: cilium`, `node-label` entries (`name=R820`), and the cluster CIDR; then
  `systemctl enable --now rke2-server`.
- Retrieve the node-join token from `/var/lib/rancher/rke2/server/node-token` and
  the kubeconfig from `/etc/rancher/rke2/rke2.yaml` (rewrite the server URL to
  `https://10.0.0.13:6443`).
- Trust the internal CA: add `registry.arpa` to `/etc/rancher/rke2/registries.yaml`
  so containerd pulls from the private registry.

### Step 2: Join RKE2 Agents (workers)
For each worker — **R710, R510, RW710, GR1080** (and **GB10** if its
throttled-vLLM soak passed):
- If `systemctl is-active rke2-agent` is active, skip.
- Otherwise install the RKE2 agent, write `/etc/rancher/rke2/config.yaml` with
  `server: https://10.0.0.13:9345`, the join token, and node labels; then
  `systemctl enable --now rke2-agent`.
- Distribute `registries.yaml` (registry.arpa + internal CA) to every agent.
- **GB10** is ARM64 (Grace-Blackwell); it joins as a tainted GPU agent
  (`gpu=true:NoSchedule`) so only GPU workloads with matching tolerations land
  there. Only arm64 images may schedule on it.

### Step 3: Verify Cilium CNI
RKE2 with `cni: cilium` self-installs Cilium. Verify the dataplane:
- `cilium status` reports OK on every node; `kube-proxy` is **not** running
  (Cilium runs in kube-proxy-replacement mode — this is what removes the IPVS
  kernel path that hard-reset GB10 under Swarm).
- For the ingress VIP, configure a `CiliumLoadBalancerIPPool` + `L2Announcement`
  (e.g. reuse `10.0.0.13` so Technitium's `*.arpa → VIP` needs no change).

### Step 4: GPU Device Plugin
On GPU nodes **GR1080 (10.0.0.16)** and **GB10 (10.0.0.18, if joined)**:
- Ensure the NVIDIA driver + `nvidia-container-toolkit` are present (RKE2
  auto-creates `RuntimeClass nvidia` when it detects the runtime).
- Deploy the NVIDIA k8s device-plugin DaemonSet with a nodeSelector to the GPU
  nodes; verify `nvidia.com/gpu` appears under the node's allocatable resources
  (`kubectl describe node GR1080`).
- GPU workloads then request `nvidia.com/gpu` with `runtimeClassName: nvidia` —
  no more `swarm-launcher` device-passthrough wrapper.

### Step 5: Verify Cluster State
Confirm every node reads `Ready` (`kubectl get nodes`), the expected labels and
taints are present, Cilium is healthy, and the GPU nodes advertise
`nvidia.com/gpu`. Re-running this skill against a healthy cluster is a no-op.
