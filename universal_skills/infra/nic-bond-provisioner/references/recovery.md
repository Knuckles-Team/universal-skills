# NIC bond — gotchas, recovery, and post-rollout

Read this when a bond apply misbehaves, before touching a swarm manager, or when
wiring the bond rollout into a Docker Swarm data-path fix.

## Hard-won gotchas (each one cost a wedged node or hours)
1. **Source YAML must be `0644`.** `netplan` copies the source file's mode to the
   generated `/run/systemd/network/*` files. At `0600`, the `systemd-network` user
   cannot read them → `systemd-networkd` logs `Failed to open ... Permission denied`
   → the bond netdev is never created, and it fails the SAME way on every reboot.
   netplan prints a benign `permissions ... too open` WARNING at 0644 — ignore it.
2. **Multi-NIC nodes that run NetworkManager need NM disabled + a networkd RESTART.**
   Persistent NM connection profiles hold the NICs, so `networkctl` reports them
   `unmanaged` and `netplan apply` alone won't enslave them. Sequence: disable NM →
   `systemctl restart systemd-networkd` → `networkctl reconfigure <members> bond0`.
3. **The auto-revert MUST tear down bond0 + restart networkd**, not just restore the
   netplan files. A naive revert collides with a freshly-built bond (NM trying to DHCP
   the slaves while networkd holds them) and wedges the node. `apply-bond.sh` does this.
4. **Commit the instant the bond verifies.** The revert is a safety net, not the normal
   path. The classic failure: verify succeeds, operator hesitates, the 180s timer fires
   mid-celebration and reverts (or collides). `sudo touch /tmp/bond_ok` immediately.
5. **Run at the node's console** (physical / KVM / iDRAC SoL), never over the SSH link
   you would lose — networking blips during the cutover. If you must drive over SSH,
   wrap the apply in `setsid nohup` so it survives the disconnect, and rely on the revert.
6. **DNS:** retiring NM is safe only when `systemd-resolved` owns `/etc/resolv.conf`
   (symlink → `…/stub-resolv.conf`, nameserver `127.0.0.53`). Confirm first:
   `ls -l /etc/resolv.conf; resolvectl status`. The bond YAML's `nameservers` feed resolved.
7. **iDRAC/BMC is the real backstop** — but verify it actually answers over LAN BEFORE
   relying on it (`ipmitool -I lanplus -H <bmc> -U <u> -P <p> chassis power status`).
   In-band password-set does NOT guarantee the LAN channel/cipher is up. If the BMC's
   dedicated NIC is uncabled, the physical console is your only recovery.

## Manual recovery (node wedged, revert didn't save it)
At the console:
```bash
sudo ip link delete bond0 2>/dev/null
sudo systemctl restart systemd-networkd
sudo systemctl restart NetworkManager      # if NM was the baseline
sleep 3; ip a show <primary-nic>; ping -c2 <gateway-or-peer>
# last resort — boots clean on the on-disk (restored) netplan:
sudo reboot
```
Before risky reboots on Dell PowerEdge, trim the EFI boot order so it can't stall on
PXE/DVD fallback: `sudo efibootmgr -o <ubuntu>,<fixeddisk>` (e.g. `000B,0009`). Entries
are reordered, not deleted.

## Why this exists: Docker Swarm VXLAN data-path stability
Multi-NIC nodes pulling DHCP on every NIC pick a non-deterministic egress src; the
kernel egress = the swarm VXLAN data-path, so it shifts on reboot and silently breaks
cross-node overlay. One active-backup bond on the canonical static IP gives ONE
deterministic egress (+ NIC/cable redundancy, no switch config).

After ALL target nodes are bonded, re-init the swarm so the data-path pins to canonical:
```
# leave --force all → init manager (--data-path-addr <canonical>) → workers join
#   (--advertise-addr <canonical> --data-path-addr <canonical>)
# → re-add node labels → recreate overlay networks ON THE MANAGER → validate cross-node
# → redeploy stacks
```
Pin `--data-path-addr` to each node's canonical IP (now stable thanks to the bond).
