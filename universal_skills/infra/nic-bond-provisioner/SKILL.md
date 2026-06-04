---
name: nic-bond-provisioner
description: >-
  Convert multi-NIC Linux hosts to a systemd-networkd active-backup bond on a static
  canonical IP, retiring NetworkManager, with a console-safe dead-man auto-revert. Use
  when a node's egress/data-path is non-deterministic across reboots (multiple DHCP NICs),
  when stabilizing a Docker Swarm VXLAN data-path before a swarm re-init, or when the user
  asks to bond NICs, set a static canonical IP via netplan, or fix cross-node overlay drift.
  Do NOT use for single-NIC hosts (already deterministic), for LACP/802.3ad throughput
  bonding (this is failover, not aggregation), or for non-netplan distros.
license: MIT
tags: [infra, networking, netplan, systemd-networkd, bond, docker-swarm, vxlan, failover, homelab]
metadata:
  author: Genius
  version: '0.1.21'
---

# NIC Bond Provisioner

Provision an **active-backup `bond0`** on a node's **canonical static IP** using
`systemd-networkd`, retiring NetworkManager so there is a single network authority and a
**deterministic egress** (the kernel egress src = the Docker Swarm VXLAN data-path, so a
drifting egress silently breaks cross-node overlay). Every step has a **dead-man
auto-revert** so a bad apply self-heals.

This skill is failover + determinism, NOT throughput aggregation. For LACP, upgrade the
bond mode later once the switch has port-channels.

## When to use / not use
- **Use**: multi-NIC node with several DHCP NICs and a non-deterministic egress; pinning a
  node to its canonical IP before a swarm re-init; recovering recurring cross-node overlay drift.
- **Skip**: single-NIC nodes (already deterministic — bonding adds nothing); LACP/throughput
  needs; hosts not managed by netplan.

## Bundled resources
- `scripts/apply-bond.sh` — applies a bond config **at the node's console** with a
  self-tearing dead-man revert. Encodes gotchas #1–#5 of `references/recovery.md`.
- `scripts/gen-bond-config.sh` — emit a site-agnostic bond netplan YAML from `--ip` + `--members`.
- `references/recovery.md` — gotchas, manual recovery, and the post-rollout swarm re-init.
  **Read it before bonding a swarm manager or when an apply misbehaves.**

## Procedure

### 1. Discover the node's NICs and confirm prerequisites
On each target node gather the cabled NICs and the DNS/egress state:
```bash
ip -br link | grep -vE '^(lo|docker|veth|br-|vx-|.*gwbridge)'   # carrier-up NICs
ip -br addr ; ip route get 1.1.1.1 | head -1                    # which IP/NIC is egress
ls -l /etc/resolv.conf ; resolvectl status | grep -i 'DNS Server'
```
Include only **carrier-up** NICs as bond members (NO-CARRIER ports stay backup forever).
Confirm `/etc/resolv.conf` → systemd-resolved stub (gotcha #6) — otherwise retiring NM
breaks DNS; fix that first.

### 2. Generate the per-node bond config
```bash
scripts/gen-bond-config.sh --ip <CANONICAL/8> --members "<nic1 nic2 ...>" \
    --primary <nic-holding-canonical> --node <NAME> --out /tmp/bond0-<NAME>.yaml
```
Default DNS is `10.0.0.199 1.1.1.1` and gateway `10.0.0.1` — override with `--dns` / `--gw`.

### 3. Pre-flight the recovery path (do this BEFORE applying)
- Be **at the node's console** (physical / KVM / iDRAC SoL) — the apply blips networking.
- Verify the BMC actually answers over LAN if you intend to lean on it (gotcha #7):
  `ipmitool -I lanplus -H <bmc-ip> -U <user> -P <pw> chassis power status`.
- On Dell PowerEdge, trim the EFI boot order so a recovery reboot can't stall on PXE/DVD:
  `sudo efibootmgr` then `sudo efibootmgr -o <ubuntu-id>,<fixeddisk-id>`.

### 4. Apply with the dead-man revert (AT THE CONSOLE)
```bash
sudo bash scripts/apply-bond.sh /tmp/bond0-<NAME>.yaml 180
```
The script: backs up `/etc/netplan`, arms a self-tearing revert (deletes bond0 + restores
netplan + re-enables NM + restarts networkd if not committed in N seconds), installs the
config at **0644** (gotcha #1), disables NM, restarts networkd, and reconfigures the slaves
(gotcha #2). It prints a verify summary.

### 5. Verify, then COMMIT IMMEDIATELY (gotcha #4)
Confirm in the printed summary (or re-check):
```bash
ip -br addr show bond0                 # expect the canonical IP
ip route show default                  # expect ONLY: default via <gw> dev bond0
cat /proc/net/bonding/bond0 | grep -E 'Active Slave|Slave Interface'   # all members enslaved
ping -c2 <a-peer-or-gateway>
```
If correct, commit at once (cancels the revert):
```bash
sudo touch /tmp/bond_ok && sudo rm -rf /root/netplan.bak.*
```
If anything is wrong, **do nothing** — it auto-reverts. If it wedges anyway, follow the
manual recovery in `references/recovery.md`.

### 6. Roll across the fleet — workers first, manager LAST
Apply one node at a time, verifying each before the next. Do swarm managers last, and do
the **control host you are running on** from its own console (an SSH-driven apply there
would cut your own link). After ALL targets are bonded, re-init the swarm to pin
`--data-path-addr` to the now-stable canonical IPs — see `references/recovery.md`.

## Failure modes (and where they're handled)
| Symptom | Cause | Fix |
|---------|-------|-----|
| `bond0` never appears; networkd logs `Permission denied` | source YAML `0600` (gotcha #1) | script forces `0644`; re-run |
| `networkctl` shows members `unmanaged`, no bond | NM still holds the NICs (gotcha #2) | script disables NM + restarts networkd |
| Node reachable then drops seconds after a good apply | revert collided with the new bond (gotcha #3) | script's revert tears down bond0 first; commit faster |
| DNS dead after NM retired | resolv.conf wasn't resolved-owned (gotcha #6) | restore NM or point resolv.conf at resolved |
| Can't recover a stranded node | BMC LAN never actually worked (gotcha #7) | physical console; pre-verify BMC next time |
