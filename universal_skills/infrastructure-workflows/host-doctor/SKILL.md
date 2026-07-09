---
name: host-doctor
description: >-
  Onboard-diagnose a host (or a whole fleet) and remediate under gate. Validates the
  OS/kernel/arch, samples CPU/mem/disk/load utilization, inspects processes for
  zombies, runaway/orphaned hogs, and swap exhaustion, and checks PHYSICAL storage +
  BMC health (SMART incl. RAID megaraid passthrough, drive-slot/IPMI faults, predicted
  failures) that the filesystem checks miss — then, only after presenting the findings
  and getting explicit per-host confirmation, remediates by delegating to the
  systems-issue-troubleshooter workflow (kill rogue PIDs, reclaim swap/temp), and
  re-verifies. Use when a machine is hot, sluggish, throwing a drive fault, or newly
  onboarded and you want a single "how is this host doing, and make it run cool" pass.
  Composes hardware-profile-sweep, host-resource-sampler, and host-process-inspector
  over tunnel-manager SSH, plus sm_storage_health (systems-manager) and the fan-manager
  IPMI/BMC tools. Diagnosis is read-only; every change is gated on user approval.
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
    inspector-agent: [tun_tm_remote, sm_process_operations, sm_storage_health, fan_manager_sel, fan_manager_sensors]
    remediation-agent: [sm_process_operations, sm_system_operations]
tags: [infra, host, diagnostics, onboarding, process, zombie, swap, storage, smart, bmc, ipmi, drive-fault, remediation]
concept: CONCEPT:INFRA-001
---

# Host Doctor Workflow

**CONCEPT:INFRA-001**

Onboard-diagnose a host (or fleet) — OS validation + resource utilization + process /
zombie / runaway / swap inspection + physical-storage/BMC health — and remediate **only
under explicit per-host approval**. The four diagnostic steps are read-only and run in
parallel; remediation delegates to `systems-issue-troubleshooter` and is gated behind a
user decision (drive faults are surfaced as hardware replace candidates, never
auto-remediated).

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

### Step 2b: storage_bmc_health
**Agent**: `inspector-agent`
**Tools**: `sm_storage_health, fan_manager_sel, fan_manager_sensors`

Run `sm_storage_health` (action `report`) to check **physical** disk health that the
filesystem/process steps miss: SMART for every drive incl. RAID `megaraid` passthrough,
in-band PERC/LSI PD state, and BMC/IPMI **drive-slot faults** — correlated, so a
BMC-flagged disk with clean SMART media is classified as a **link/aging fault**
(reseat/replace), not media wear. For a remote host pass `host=<inventory-key>`; for
out-of-band BMC pass `params_json={"oob":true}` (the iDRAC credential is read from
OpenBao `apps/idrac` at runtime). For deeper BMC detail use the fan-manager IPMI tools
(`fan_manager_sel` for the System Event Log history, `fan_manager_sensors` action `type`
sensor_type `Drive Slot`). Flags failed/predicted-fail/faulted drives as **replace
candidates** (hardware action — never auto-remediated).
Expected: `disks, bmc_drive_faults, faults`

### Step 3: present_and_gate [depends_on: 0, 1, 2, 2b]
**Agent**: `inspector-agent`
**Tools**: `tun_tm_remote`

Present the consolidated dashboard (OS validation + utilization + the ranked hog/zombie/
swap findings + drive/BMC faults + load-vs-cores verdict). Ask the user which candidates
to act on. Drive faults are surfaced as **hardware replace candidates** (physical action,
not auto-remediated). **No
change proceeds without an explicit, per-host choice.** Safest-first ordering: orphaned
runaways → reclaim swap → reap zombies (via parents) → wind down stale sessions.

### Step 4: remediate [depends_on: 3]
**Agent**: `remediation-agent`
**Tools**: `sm_process_operations, sm_system_operations`

Execute only the approved actions by delegating to the **`systems-issue-troubleshooter`**
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

- **Run first (in parallel):** Step 0 — hardware_profile_sweep; Step 1 — host_resource_sampler; Step 2 — host_process_inspector; Step 2b — storage_bmc_health
- **After level 0:** Step 3 — present_and_gate (user decision)
- **After Step 3:** Step 4 — remediate (only approved actions, via systems-issue-troubleshooter)
- **After Step 4:** Step 5 — verify_and_persist

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
