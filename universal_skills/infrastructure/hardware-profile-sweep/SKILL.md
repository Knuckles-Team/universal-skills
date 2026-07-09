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
  version: '1.2.0'
---

# Hardware Profile Sweep Skill

Stateless atomic operation to query system resources, operating systems, and accelerator devices across all reachable nodes.

## Prerequisites

- `systems-manager-mcp` — for collecting low-level OS, CPU, RAM, storage, and GPU parameters.
- `tunnel-manager-mcp` — for coordinating execution across multiple hosts.

## Steps

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
