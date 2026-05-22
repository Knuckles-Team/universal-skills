---
name: hardware_sweep
description: OS and hardware information sweep across all inventory hosts. Collects CPU, memory, disk, GPU, and OS details for each machine and ingests them into the Knowledge Graph for troubleshooting and service designation decisions.
domain: infrastructure
tags: ['hardware', 'sweep', 'discovery', 'os', 'system-info']
requires: ['tunnel-manager-mcp', 'systems-manager-mcp']
---

# hardware_sweep Workflow

OS and hardware information sweep across all inventory hosts. Collects CPU, memory, disk, GPU, and OS details for each machine and ingests them into the Knowledge Graph for troubleshooting and service designation decisions.

### Step 0: tunnel-manager-mcp
List all hosts from inventory with their connectivity status
Expected: host, inventory

### Step 1: systems-manager-mcp
For each reachable host, collect CPU model and core count, total and available RAM, disk partitions and usage, OS distribution and kernel version
Expected: cpu, memory, disk, os
Depends On: Step 0

### Step 2: systems-manager-mcp
For each reachable host, detect GPU/accelerator hardware via lspci or nvidia-smi and collect driver versions
Expected: gpu, accelerator, driver
Depends On: Step 0

### Step 3: graph-os
Update HardwareNode entries in the KG with collected hardware metadata and create GPUAccelerator nodes with HAS_ACCELERATOR relationships
Expected: update, hardware, gpu
Depends On: Step 1, Step 2
