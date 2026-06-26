---
name: host-doctor
description: >-
  Onboard-diagnose a host (or a whole fleet) and remediate under gate. Validates the
  OS/kernel/arch, samples CPU/mem/disk/load utilization, and inspects processes for
  zombies, runaway/orphaned hogs, and swap exhaustion — then, only after presenting the
  findings and getting explicit per-host confirmation, remediates by delegating to the
  systems_issue_troubleshooter workflow (kill rogue PIDs, reclaim swap/temp), and
  re-verifies. Use when a machine is hot, sluggish, or newly onboarded and you want a
  single "how is this host doing, and make it run cool" pass. Composes hardware-profile-sweep,
  host-resource-sampler, and host-process-inspector over tunnel-manager SSH. Diagnosis is
  read-only; every change is gated on user approval.
domain: infra
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: host onboarding diagnostics and gated remediation
  execution_mode: parallel
  specialist_ids:
    - discovery-agent
    - inspector-agent
    - remediation-agent
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    inspector-agent: [tun_tm_remote, sm_process_operations]
    remediation-agent: [sm_process_operations, sm_system_operations]
tags: [infra, host, diagnostics, onboarding, process, zombie, swap, remediation]
concept: CONCEPT:INFRA-001
---

# Host Doctor Workflow

**CONCEPT:INFRA-001**

Onboard-diagnose a host (or fleet) — OS validation + resource utilization + process /
zombie / runaway / swap inspection — and remediate **only under explicit per-host
approval**. The three diagnostic steps are read-only and run in parallel; remediation
delegates to `systems_issue_troubleshooter` and is gated behind a user decision.

## Steps

### Step 0: hardware_profile_sweep
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Run the `hardware-profile-sweep` atomic skill to validate each target's OS/kernel/arch,
CPU, RAM, disks, and any GPU/accelerator. Establishes the baseline the load numbers are
judged against (load must be read relative to core count).
Expected: `os, cores, accelerator`

### Step 1: host_resource_sampler
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Run the `host-resource-sampler` atomic skill to sample CPU%, load average, memory %, and
disk % across the target host(s), flagging any node over the utilization thresholds.
Expected: `cpu, load, memory, disk`

### Step 2: host_process_inspector
**Agent**: `inspector-agent`
**Tools**: `tun_tm_remote, sm_process_operations`

Run the `host-process-inspector` atomic skill to rank CPU/RAM offenders by **full
cmdline**, flag orphaned-to-PID1 runaways, list zombie→parent pairs, detect swap
exhaustion + top swap holders and D-state blockers, and attribute culprit PIDs to their
tmux session where possible. Produces the prioritized **kill/reap/tune candidate** list.
Expected: `runaways, zombies, swap, candidates`

### Step 3: present_and_gate [depends_on: 0, 1, 2]
**Agent**: `inspector-agent`
**Tools**: `tun_tm_remote`

Present the consolidated dashboard (OS validation + utilization + the ranked hog/zombie/
swap findings + load-vs-cores verdict). Ask the user which candidates to act on. **No
change proceeds without an explicit, per-host choice.** Safest-first ordering: orphaned
runaways → reclaim swap → reap zombies (via parents) → wind down stale sessions.

### Step 4: remediate [depends_on: 3]
**Agent**: `remediation-agent`
**Tools**: `sm_process_operations, sm_system_operations`

Execute only the approved actions by delegating to the **`systems_issue_troubleshooter`**
workflow (`kill_process` for confirmed rogue/orphan PIDs, `clean_temp_files` /
`clean_package_cache`, swap reset). Verify each PID's identity (re-read cmdline) before
killing — PIDs recycle. Never kill a process still owned by a live interactive session
without naming the session and getting per-session confirmation.

### Step 5: verify_and_persist [depends_on: 4]
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, graph_write`

Re-run `host-resource-sampler` to confirm the load/swap recovered (load decays over
~1–15 min — re-sample, don't expect an instant drop). Persist the run (findings, actions
taken, before/after metrics) to the Knowledge Graph via `graph_write`.

## Output
- Host Doctor results persisted in KG (`:HardwareNode` health + remediation audit)
- Structured report (MD/PDF): OS validation, utilization, ranked hogs/zombies/swap, actions
- Audit trail with timestamps, the PIDs acted on, and per-host approvals

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in
parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — hardware_profile_sweep; Step 1 — host_resource_sampler; Step 2 — host_process_inspector
- **After level 0:** Step 3 — present_and_gate (user decision)
- **After Step 3:** Step 4 — remediate (only approved actions, via systems_issue_troubleshooter)
- **After Step 4:** Step 5 — verify_and_persist

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
