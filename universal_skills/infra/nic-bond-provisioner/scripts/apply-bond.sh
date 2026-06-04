#!/usr/bin/env bash
# apply-bond.sh — convert a node to a systemd-networkd active-backup bond on its
# canonical IP and RETIRE NetworkManager, with a dead-man auto-revert.
#
# RUN AT THE NODE'S CONSOLE (physical/KVM/iDRAC) — networking WILL blip during the
# cutover, so don't run it over the SSH link you'd lose. Needs root/sudo.
#
#   sudo bash apply-bond.sh <config.yaml> [revert_seconds=180]
#
# Then, in the SAME console, verify and COMMIT:
#   ip -br addr show bond0          # expect the canonical IP
#   ip route show default           # expect ONLY: default via 10.0.0.1 dev bond0
#   ping -c2 10.0.0.13
#   sudo touch /tmp/bond_ok         # COMMIT — cancels the revert. Only if all good.
# Do nothing -> auto-revert (deletes bond0, restores netplan, re-enables NM).
#
# Lessons baked in (2026-06-03 rollout):
#  - source YAML MUST be 0644 or networkd (user systemd-network) can't read the
#    generated /run files -> bond never forms (and fails the SAME way on reboot).
#  - multi-NIC nodes with persistent NM profiles need NM disabled + networkd
#    RESTART (not just `netplan apply`) before networkd will enslave the NICs.
#  - the revert must tear down bond0 + restart networkd, else it half-collides
#    with a freshly-built bond and wedges the node.
set -euo pipefail
[ "$(id -u)" = 0 ] || exec sudo "$0" "$@"

CFG="${1:?usage: apply-bond.sh <config.yaml> [revert_seconds]}"
REVERT="${2:-180}"
[ -f "$CFG" ] || { echo "config not found: $CFG" >&2; exit 1; }

TS=$(date +%Y%m%d-%H%M%S); BAK="/root/netplan.bak.$TS"
mkdir -p "$BAK"; cp -a /etc/netplan/. "$BAK/"
systemctl is-enabled NetworkManager >/dev/null 2>&1 && echo yes >"$BAK/nm" || echo no >"$BAK/nm"
rm -f /tmp/bond_ok

# Dead-man revert: tear down bond, restore netplan + NM, restart networkd.
nohup bash -c "
  sleep $REVERT; [ -f /tmp/bond_ok ] && exit 0
  ip link set bond0 down 2>/dev/null; ip link delete bond0 2>/dev/null
  rm -f /etc/netplan/*.yaml; cp -a $BAK/*.yaml /etc/netplan/ 2>/dev/null
  [ \"\$(cat $BAK/nm)\" = yes ] && systemctl enable --now NetworkManager
  systemctl restart systemd-networkd 2>/dev/null
  netplan apply
  logger -t apply-bond 'AUTO-REVERTED (no commit in ${REVERT}s)'
" >/dev/null 2>&1 &
REVPID=$!

# Install config as the sole authority (0644 = reboot-safe + networkd-readable).
rm -f /etc/netplan/*.yaml
cp "$CFG" /etc/netplan/01-bond0.yaml
chmod 0644 /etc/netplan/01-bond0.yaml

# Retire NM so it releases the slave NICs, then let networkd build the bond.
systemctl disable --now NetworkManager 2>/dev/null || true
netplan generate
chmod 0644 /run/systemd/network/* 2>/dev/null || true
systemctl restart systemd-networkd
sleep 3
MEMBERS=$(grep -oP '^\s+(eno[0-9]+|enp\w+)(?=:)' /etc/netplan/01-bond0.yaml | tr -d ' ' | sort -u | tr '\n' ' ')
networkctl reconfigure $MEMBERS bond0 2>/dev/null || true
sleep 2

echo
echo "=== APPLIED $CFG  (backup: $BAK) ==="
echo "bond0:"; ip -br addr show bond0 2>&1 | sed 's/^/  /'
echo "default routes (want ONLY bond0):"; ip route show default | sed 's/^/  /'
echo "egress: $(ip route get 10.0.0.50 2>/dev/null | grep -oP 'src \K[0-9.]+')"
echo
echo ">>> If bond0 holds the canonical IP and the only default route is via bond0:"
echo ">>>     sudo touch /tmp/bond_ok && sudo rm -rf /root/netplan.bak.*"
echo ">>> Else do nothing — auto-revert fires in ${REVERT}s (revert pid $REVPID)."
