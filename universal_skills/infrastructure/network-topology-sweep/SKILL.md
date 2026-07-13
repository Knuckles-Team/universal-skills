---
name: network-topology-sweep
skill_type: skill
description: >
  Network Topology Sweep atomic skill. Discovers active subnets, VLANs,
  network interfaces, and connectivity states across all registered hardware nodes
  using tunnel-manager-mcp.
domain: infrastructure
tags:
  - networking
  - discovery
  - topology
  - scan
requires:
  - tunnel-manager-mcp
  - systems-manager-mcp
metadata:
  version: '1.2.1'
---

# Network Topology Sweep Skill

Stateless atomic operation to discover network segments, interfaces, routing tables, and connectivity states across physical and virtual hardware nodes.

## Prerequisites

- `tunnel-manager-mcp` — for remote host command execution and SSH inventory access.
- `systems-manager-mcp` — for system-level network diagnostics on the local node.

## Steps

### Step 1: Query Host Inventory
Retrieve the full list of target hosts and IP addresses from the inventory.yaml configuration using `tunnel-manager-mcp`.

### Step 2: Probe Host Connectivity
Execute BatchMode SSH connections to every node concurrently to determine active reachability.

### Step 3: Scan Network Interfaces
Run interface and routing scanning commands (`ip addr show`, `ip route`, `ifconfig`) on each reachable host to extract:
- Active network interfaces (NICs)
- IP addresses, subnets, and CIDR blocks
- VLAN configurations and bridges
- VPN interfaces (e.g., WireGuard, Tailscale)

### Step 4: Export Discovered Topology Data
Compile and format the parsed network profile into structured JSON for Graph-OS/topology mapping:
- `NetworkSubnet` properties (CIDR, boundary IPs)
- `NetworkInterface` properties (macAddress, mtu, speed, ipAddress)
- `VPNTunnel` configurations
