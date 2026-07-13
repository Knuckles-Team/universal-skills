---
name: k8s-node-rolling-update
skill_type: workflow
description: >-
  Roll OS package updates across the homelab's RKE2 Kubernetes cluster one node at a time —
  cordon, drain (tolerating DaemonSets), SSH apt upgrade, reboot only if required, wait for
  Ready, uncordon — so workloads stay available throughout. Workers roll first, the sole
  control-plane node (r820) rolls last, and the run aborts rather than cascades if any
  node fails to drain or come back Ready. Use when asked to patch/update OS packages or a
  kernel across cluster nodes (r510, r710, rw710, gb10, r820), or to roll a reboot across
  the cluster. Do NOT use for a blind fleet-wide `apt upgrade && reboot` (skips drain, takes
  every node down at once), for application/workload version rollouts (that's a Deployment
  rolling update, not a node OS patch), or for the initial RKE2 install/bootstrap.
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: rolling OS maintenance across a live Kubernetes cluster, one node at a time
  execution_mode: sequential
  specialist_ids:
    - discovery-agent
    - drain-agent
    - patch-agent
    - verify-agent
  tool_assignments:
    discovery-agent: [cnt_cm_k8s_cluster]
    drain-agent: [cnt_cm_k8s_cluster]
    patch-agent: [tun_tm_remote]
    verify-agent: [cnt_cm_k8s_cluster, tun_tm_remote, graph_write]
tags: [infra, kubernetes, rke2, rolling-update, patching, drain, cordon, homelab, node-maintenance]
concept: CONCEPT:INFRA-001
metadata:
  version: '1.2.1'
---

# K8s Node Rolling Update Workflow

**CONCEPT:INFRA-001**

Rolling OS-patch workflow for the homelab's **5-node RKE2 cluster** (Cilium CNI). This is a
**sequential, one-node-at-a-time** workflow, not a parallel fan-out: OS updates on a live k8s
cluster are never a blind `apt upgrade && reboot` across the fleet — that takes every node's
workloads down simultaneously and can wedge etcd. Instead, each node is drained so its pods
reschedule elsewhere, patched, rebooted only if required, and verified healthy **before the
next node starts**.

## The cluster
| Node | IP | Role | Notes |
|------|----|------|-------|
| r510 | 10.0.0.10 | worker | |
| r710 | 10.0.0.11 | worker | |
| rw710 | 10.0.0.12 | worker | |
| gb10 | 10.0.0.18 | worker | arm64 DGX-Spark GPU node. **Known intermittent hardware power-fault** — power-cycles on its own every 12-35 min. Excluded by default (see gb10 caveat below). |
| r820 | 10.0.0.13 | control-plane / etcd | The **only** control-plane node — always last. |

- SSH as `genius@<ip>` (passwordless sudo configured); `kubectl` uses `/home/genius/.kube/config`.
- RKE2 service is `rke2-server` on r820, `rke2-agent` on the four workers.
- DaemonSets present on every node that MUST be tolerated (not blocked) by drain:
  `fan-manager` (ns `fan-control`), `node-exporter` (ns `apps`), `cilium` and
  `nvidia-device-plugin` (ns `kube-system`), `rke2-ingress-nginx-controller` (ns
  `kube-system`) — always drain with `ignore_daemonsets`.

## Node order — workers first, control-plane LAST
```
r510 → r710 → rw710 → gb10 (optional/caution) → r820
```
- **r820 is always last.** It is the sole control-plane/etcd node — draining or rebooting
  it while a worker is still unready leaves no scheduler quorum spare and no fallback.
- **gb10 caveat**: gb10's unrelated hardware power-fault means a drain/reboot you initiate can
  race a fault-triggered power-cycle already in flight, and `Ready`-wait can time out or flap
  on an otherwise-successful patch. Default to **skipping gb10** in routine rolls and handle it
  manually — patch it, then watch it through at least one full 12-35 min window before trusting
  the result. Treat any gb10 failure as *possibly the known fault, not necessarily your patch* —
  but never assume that; verify.

## Steps

### Step 0: discover_baseline
**Agent**: `discovery-agent`
**Tools**: `cnt_cm_k8s_cluster`

Resolve the run's node list and confirm the starting state before touching anything: list
nodes (`cnt_cm_k8s_cluster` action `list_nodes`) and node conditions (action
`get_node_conditions`) to confirm every target is currently `Ready` and not already
`SchedulingDisabled`. Build the ordered target list — all workers (r510, r710, rw710) first
in that order, gb10 only if explicitly included, r820 always last. Abort before starting if
any target is not already healthy (don't roll updates onto a node that's already broken).
Expected: `node_order, baseline_conditions`

### Step 1: cordon_and_drain [depends_on: discover_baseline]
**Agent**: `drain-agent`
**Tools**: `cnt_cm_k8s_cluster`

For the **current** node in the order (one node only — never more than one concurrently):
`cnt_cm_k8s_cluster` action `cordon_node`, then action `drain_node` with
`ignore_daemonsets=true`, `grace_period_seconds` generous enough for clean pod shutdown
(≥120s), and delete-emptydir-data semantics so scratch-volume pods aren't refused eviction.
If drain fails or times out, **stop the run** — the node stays cordoned (safe) and no other
node is touched.
Expected: `cordoned, drained`

### Step 2: ssh_patch [depends_on: cordon_and_drain]
**Agent**: `patch-agent`
**Tools**: `tun_tm_remote`

Over SSH to the current node: `sudo apt-get update && sudo apt-get -y upgrade`. Prefer
`upgrade` over `dist-upgrade` for routine patching (never removes packages or pulls new
dependencies); only use `dist-upgrade` when a specific update requires it, after reviewing
`apt-get dist-upgrade -s` first. A non-zero exit here also stops the run — the node stays
cordoned and unpatched-or-partially-patched, not returned to service.
Expected: `patched, apt_exit_code`

### Step 3: conditional_reboot_and_wait [depends_on: ssh_patch]
**Agent**: `patch-agent`
**Tools**: `tun_tm_remote, cnt_cm_k8s_cluster`

Check `/var/run/reboot-required` over SSH. If present, `sudo reboot`; if absent, skip the
reboot entirely — don't reboot nodes that don't need it. If rebooted, poll
`cnt_cm_k8s_cluster` action `get_node_conditions` (or an equivalent Ready-wait, timeout
≈600s) until the node reports `Ready`, then confirm the RKE2 service is actually active over
SSH (`systemctl is-active rke2-agent` on workers, `rke2-agent || rke2-server` — condition
state can lag service state). A node that doesn't return `Ready` within the timeout **stops
the run** — leave it cordoned and escalate (see Rollback / abort below) rather than proceeding.
Expected: `rebooted, ready, rke2_active`

### Step 4: uncordon_and_verify [depends_on: conditional_reboot_and_wait]
**Agent**: `verify-agent`
**Tools**: `cnt_cm_k8s_cluster`

`cnt_cm_k8s_cluster` action `uncordon_node`, then re-check `get_node_conditions` and confirm
no pods on the node are stuck `Pending`/`Evicted`/`Error` a minute or two after uncordon (give
the scheduler time to settle before declaring the node done). Only once this node is clean
does the loop advance.
Expected: `uncordoned, settled`

### Step 5: advance_or_finish [depends_on: uncordon_and_verify]
**Agent**: `discovery-agent`
**Tools**: `cnt_cm_k8s_cluster`

**This is the loop control step.** If nodes remain in the ordered list from Step 0, return to
Step 1 for the **next** node — Steps 1-4 repeat once per remaining node, strictly in order,
never in parallel. If the just-completed node was the last one (r820), the run is done.
Expected: `remaining_nodes, loop_complete`

### Step 6: KG Persistence [depends_on: advance_or_finish]
**Agent**: `verify-agent`
**Tools**: `graph_write`

Persist the run (node order, per-node before/after kernel/package versions, reboots
performed, any node skipped or aborted-on) as nodes and edges in the Knowledge Graph, linked
to the existing `:HardwareNode`/cluster entities.

## Output
- K8s Node Rolling Update results persisted in KG (per-node outcome, reboot audit)
- Structured report: node order used, patched/rebooted/skipped per node, final `kubectl get
  nodes` state
- Audit trail with timestamps and the exact apt/reboot/drain commands run per node

## Safety invariants
- **Never** drain/reboot more than **one node at a time** — the other nodes must stay serving
  traffic throughout.
- **Never** advance to the next node (Step 5) if the current node failed to drain, failed to
  return `Ready`, or its RKE2 service isn't active — stop and investigate instead.
- **Never** run `apt-get upgrade`/reboot on a node that hasn't been cordoned+drained first
  (Steps 1 before 2/3, always).
- **Never** place r820 before any worker in the node order.
- Always drain with DaemonSets tolerated (`ignore_daemonsets=true`) — without it, drain hangs
  forever on fan-manager/node-exporter/cilium pods.

## Verify success (whole run)
- `cnt_cm_k8s_cluster` `list_nodes` — every target `Ready`, none left `SchedulingDisabled`.
- No pods stuck `Pending`/`Evicted` anywhere in the cluster after the run.
- Per rebooted node, `/var/run/reboot-required` no longer present and `rke2-agent`/
  `rke2-server` active.

## Rollback / abort guidance
There is no single "rollback" for an OS patch — the safe posture is **stop, don't cascade**:
- Failed drain: the node is still cordoned (safe, just not scheduling). Fix the stuck
  pod/PDB and re-run drain for that node only — do not start the next node.
- Failed to return `Ready` after reboot: leave it cordoned. Fall back to out-of-band recovery
  (BMC/IPMI serial-over-LAN) if SSH is also unreachable. Do not touch any other node until
  this one is healthy or a deliberate, informed decision is made to proceed without it.
- `rke2-agent`/`rke2-server` won't come active: check `journalctl -u rke2-agent -n 100` (or
  `rke2-server`) on the node before rebooting again.
- Cordoned but not yet patched and you decide to stop: `uncordon_node` puts it straight back
  into service — cordon alone is always reversible.
- `apt-get upgrade` has no built-in rollback; if a specific package regresses, downgrade it
  explicitly (`apt-get install <pkg>=<old-version>`) while the node is still cordoned, then
  re-verify before uncordoning.
- Abort the **whole run** the moment any safety invariant above is violated. A partially
  rolled cluster with N-1 healthy nodes is a fine place to pause and diagnose; racing ahead to
  "finish" the roll is not.

## Bundled resources
- `scripts/roll_update.sh` — a standalone, deterministic bash implementation of Steps 1-4
  (cordon → drain → SSH apt upgrade → conditional reboot → wait Ready → uncordon) for a
  human or agent to run directly against `kubectl`/`ssh` when MCP tool access isn't
  available. Encodes the same node order, gb10 exclusion, and fail-fast abort as the steps
  above. See its `--help` for flags (`--dry-run`, `--include-gb10`, explicit node list).

## Execution

Run this workflow as a dependency-ordered chain — it is sequential by nature (each step
depends on the one before it), and Step 5 loops Steps 1-4 back for the next node in the
order until the list from Step 0 is exhausted.

- **Run first:** Step 0 — discover_baseline
- **After Step 0 (repeats per node):** Step 1 — cordon_and_drain
- **After Step 1:** Step 2 — ssh_patch
- **After Step 2:** Step 3 — conditional_reboot_and_wait
- **After Step 3:** Step 4 — uncordon_and_verify
- **After Step 4:** Step 5 — advance_or_finish (loops to Step 1 for the next node, or falls through)
- **After the loop completes:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate
action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution.
Otherwise execute the steps natively in dependency order: run steps with no unmet
`depends_on` in parallel, then their dependents. Because this workflow is a per-node loop
rather than a fan-out, "native" execution here means running Steps 1-4 to completion for one
node before starting them for the next — or simply invoking `scripts/roll_update.sh`, which
already encodes that loop.
