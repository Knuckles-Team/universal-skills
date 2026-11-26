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
  version: '1.6.2'
---

# Network Topology Sweep Skill

Stateless atomic operation to discover network segments, interfaces, routing tables, and connectivity states across physical and virtual hardware nodes.

## Prerequisites

- `tunnel-manager-mcp` — for remote host command execution and SSH inventory access.
- `systems-manager-mcp` — for system-level network diagnostics on the local node.

## Steps

1. Read the host inventory with `tunnel-manager-mcp` from `inventory.yaml`. Verify that the host list is non-empty.
2. Probe reachability with BatchMode SSH, for example `ssh -o BatchMode=yes <host> true`. Verify that each host is marked reachable or unreachable.
3. Scan interfaces with `ip addr show` and `ip route` on each reachable host. Verify that each host has at least one interface with an address.
4. Export the topology as JSON with `NetworkSubnet`, `NetworkInterface` and `VPNTunnel` entries. Verify that `python3 -m json.tool` parses the file.

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
Compile and format the parsed network profile into structured JSON for Arbora/topology mapping:
- `NetworkSubnet` properties (CIDR, boundary IPs)
- `NetworkInterface` properties (macAddress, mtu, speed, ipAddress)
- `VPNTunnel` configurations


## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Host unreachable | SSH key or network issue | Check the key in `inventory.yaml` and test with `ssh -v` |
| ifconfig not found | Not installed | Use `ip addr show` instead |
| JSON invalid | Unescaped output | Re-parse with `python3 -m json.tool` and fix the offending host |
