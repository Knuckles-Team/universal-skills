---
name: hardware-profile-sweep
skill_type: skill
description: >
  Hardware Profile Sweep atomic skill. Collects CPU, memory, disk, OS info,
  and GPU/accelerator details across reachable hardware nodes using systems-manager-mcp.
domain: infrastructure
tags:
  - hardware
  - systems
  - gpu
  - probe
requires:
  - systems-manager-mcp
  - tunnel-manager-mcp
metadata:
  version: '1.6.2'
---

# Hardware Profile Sweep Skill

Stateless atomic operation to query system resources, operating systems, and accelerator devices across all reachable nodes.

## Prerequisites

- `systems-manager-mcp` — for collecting low-level OS, CPU, RAM, storage, and GPU parameters.
- `tunnel-manager-mcp` — for coordinating execution across multiple hosts.

## Steps

1. Query core system resources on each host with `systems_manager`. Verify that every host returns OS, CPU, memory and disk data, and that `sm_storage_health` with action `report` lists drive health.
2. Detect accelerators by running `nvidia-smi` or `lspci | grep -i vga` on each host. Verify that each GPU reports a model, VRAM and driver version, or that no accelerator is recorded.
3. Format the profile data against `ontology_infrastructure.ttl` classes `HardwareNode` and `GPUAccelerator`. Verify that every host object has CPU cores, RAM size and OS fields populated.

### Step 1: Query System Info
Query core system resources on each host via `systems_manager`:
- OS details (kernel version, distribution, architecture)
- CPU specs (model, cores, threads, clock speed)
- Physical Memory (total RAM, active/free space)
- Disk Storage (disk devices, partitions, mounting locations, free capacity)
- Physical disk health via `sm_storage_health` (action `report`): SMART per drive incl.
  RAID `megaraid` passthrough (model/serial/power-on-hours/reallocated/predicted-fail),
  PERC/LSI physical-disk state, and BMC/IPMI drive-slot faults — correlated so a
  BMC-flagged disk with clean SMART media reads as a link/aging fault. Surfaces failing
  or fault-asserted drives the free-capacity check alone never sees.

### Step 2: Detect Accelerator Hardware
Identify and probe any connected GPU or AI accelerator devices (e.g., using `nvidia-smi`, `lspci | grep -i vga`):
- GPU models (e.g., GTX 1080, RTX 3090, A100)
- VRAM capacity and bus interface type
- Driver version and execution status

### Step 3: Format HW Profile Data
Export the structured metadata representing compute hardware. Data fields strictly align with `ontology_infrastructure.ttl` classes:
- `HardwareNode` properties (CPU cores, RAM size, OS info)
- `GPUAccelerator` properties (VRAM size, bus ID, model name)

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| A host returns no data | Host unreachable via `tunnel-manager-mcp` | Check inventory connectivity and re-query that host once it is reachable. |
| `nvidia-smi` not found | No NVIDIA driver on the host | Fall back to `lspci | grep -i vga` and record the device as having no managed accelerator. |
| Profile fields missing | Command output not parsed | Inspect the raw output and fix the field mapping before exporting. |
