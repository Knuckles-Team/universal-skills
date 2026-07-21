---
name: k8s-node-rolling-update
skill_type: workflow
description: >-
  Roll operating-system updates across a Kubernetes cluster one node at a time:
  discover healthy targets, process workers before control-plane nodes, cordon,
  drain, patch through an AgentConfig-resolved remote connection, reboot only when
  required, verify readiness, and uncordon. Use for governed node OS or kernel
  maintenance where workload availability must be preserved. Do not use for
  application rollouts, initial cluster bootstrap, or uncoordinated fleet-wide
  patching.
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: rolling OS maintenance across a live Kubernetes cluster, one node at a time
  execution_mode: sequential
  specialist_ids:
    - systems-manager
    - devops-engineer
  tool_assignments:
    systems-manager: [tun_tm_remote]
    devops-engineer: [cnt_cm_k8s_cluster, graph_write]
tags: [infra, kubernetes, rolling-update, patching, drain, cordon, node-maintenance]
concept: CONCEPT:INFRA-001
metadata:
  version: '1.2.1'
---

# Kubernetes node rolling update

**CONCEPT:INFRA-001**

Run a fail-fast, one-node-at-a-time OS-maintenance sequence while Kubernetes
keeps workloads available on the remaining nodes. Discover node identity and
roles from the live cluster. Resolve Kubernetes and remote-execution connection
references through AgentConfig at runtime; never place hostnames, addresses,
usernames, credentials, kubeconfig locations, or cluster-specific exceptions in
this skill or its retained output.

## Runtime inputs

Require the deployment to supply these named AgentConfig references:

- a Kubernetes connection reference with permission to inspect, cordon, drain,
  wait for, and uncordon nodes;
- a remote-execution profile reference that maps each discovered node identity
  to an authorized transport and privilege policy;
- an approved patch command profile and service-health command profile;
- optional node-selection and exclusion policy references.

Reject unresolved references. Accept connection names only in workflow inputs;
endpoints and credentials remain inside the configured providers. Determine
worker and control-plane ordering from standard Kubernetes node labels, with all
control-plane nodes last. Apply deployment-owned exclusions before starting.

## Steps

### Step 0: list_nodes [mcp_tool: cnt_cm_k8s_cluster.list_nodes]

Read the target cluster through its configured connection reference. Produce an
ordered, deduplicated target list with workers first and control-plane nodes last.
Require every target to be `Ready` and schedulable before any mutation. Abort if
role discovery, health inspection, selection policy, or remote-profile mapping is
incomplete.

Expected: `ordered_targets, baseline_conditions, resolved_reference_status`

### Step 1: cordon_node [depends_on: list_nodes] [mcp_tool: cnt_cm_k8s_cluster.cordon_node]

Cordon only the current target. The per-node chain from Steps 1 through 8 is a
strict serial map over `ordered_targets`; never start a second target while the
current target is cordoned or unverified.

Expected: `cordoned`

### Step 2: drain_node [depends_on: cordon_node] [mcp_tool: cnt_cm_k8s_cluster.drain_node]

Drain the current target with DaemonSets ignored and deployment-configured grace
and timeout bounds. If eviction fails, stop the complete run and leave the node
cordoned for operator recovery.

Expected: `drained`

### Step 3: apply_patch [depends_on: drain_node] [mcp_tool: tun_tm_remote.execute]

Execute the approved patch command profile through the target's resolved remote
profile. Do not accept an endpoint, credential, username, or arbitrary shell
command from the workflow payload. A non-zero or indeterminate outcome stops the
run with the node still cordoned.

Expected: `patch_status, patch_profile_digest`

### Step 4: check_reboot [depends_on: apply_patch] [mcp_tool: tun_tm_remote.execute]

Run the approved reboot-required check from AgentConfig. Emit only a boolean
decision and bounded status metadata.

Expected: `reboot_required`

### Step 5: reboot_if_required [depends_on: check_reboot] [mcp_tool: tun_tm_remote.execute]

When `reboot_required` is true, execute the approved reboot action through the
same resolved remote profile. Otherwise record a governed skip. Never treat the
expected transport disconnect during reboot as proof of success.

Expected: `rebooted_or_skipped`

### Step 6: wait_ready [depends_on: reboot_if_required] [mcp_tool: cnt_cm_k8s_cluster.get_node_conditions]

Wait within the configured bound for the current node to report `Ready`. Stop the
run and leave it cordoned on timeout or an ambiguous condition.

Expected: `ready`

### Step 7: verify_node_service [depends_on: wait_ready] [mcp_tool: tun_tm_remote.execute]

Run the approved node-service health profile. Require an affirmative result
before returning the node to service.

Expected: `service_healthy, health_profile_digest`

### Step 8: uncordon_node [depends_on: verify_node_service] [mcp_tool: cnt_cm_k8s_cluster.uncordon_node]

Uncordon the current target and verify it remains `Ready`. Advance the serial map
to the next target only after this step succeeds.

Expected: `uncordoned, settled`

### Step 9: persist_outcome [depends_on: uncordon_node] [mcp_tool: graph_write]

After every selected node completes, persist privacy-safe aggregate outcomes,
profile digests, and timestamps. Do not retain connection values, endpoints,
credentials, local paths, command output, or operator identity.

Expected: `run_outcome_reference`

## Safety invariants

- Mutate exactly one node at a time; the node chain is never parallelized.
- Stop after any failed drain, patch, reboot recovery, readiness, service-health,
  or uncordon check.
- Derive role order from the cluster; process every control-plane node after all
  selected workers.
- Keep all environment topology and trust material behind AgentConfig references.
- Require an explicit approval before executing the first mutating step.
- Never acknowledge completion until every selected node is healthy and
  schedulable.

## Execution

Run Step 0 first. Map Steps 1 through 8 over `ordered_targets` strictly
sequentially, then run Step 9 once. A condition in Step 5 may skip the reboot
action but may not skip readiness and service verification.

**Execution:** If graph-os is reachable, offload the whole DAG via
`graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill)
for true parallel/swarm execution. Otherwise execute the steps natively in
dependency order: run steps with no unmet `depends_on` in parallel, then their
dependents. This workflow's per-node mutation chain is explicitly serial even
when the executor supports parallel work.
