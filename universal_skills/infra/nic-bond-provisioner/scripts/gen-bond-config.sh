#!/usr/bin/env bash
# gen-bond-config.sh — emit a systemd-networkd active-backup bond netplan YAML.
# Site-agnostic: pass the canonical static IP and the NIC members. Writes to stdout
# (or --out FILE). Pair with apply-bond.sh, which applies it with a dead-man revert.
#
#   gen-bond-config.sh --ip 10.0.0.11/8 --members "eno1 eno2 eno3 eno4" \
#       [--primary eno1] [--gw 10.0.0.1] [--dns "10.0.0.199 1.1.1.1"] \
#       [--node R710] [--out /tmp/bond0-R710.yaml]
#
# Single-NIC nodes don't need a bond (already deterministic) — use --members with one
# NIC only if you specifically want a static pin; otherwise skip those nodes entirely.
set -euo pipefail

IP=""; MEMBERS=""; PRIMARY=""; GW="10.0.0.1"; DNS="10.0.0.199 1.1.1.1"; NODE=""; OUT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --ip) IP="$2"; shift 2;;
    --members) MEMBERS="$2"; shift 2;;
    --primary) PRIMARY="$2"; shift 2;;
    --gw) GW="$2"; shift 2;;
    --dns) DNS="$2"; shift 2;;
    --node) NODE="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 1;;
  esac
done
[ -n "$IP" ] || { echo "--ip required (e.g. 10.0.0.11/8)" >&2; exit 1; }
[ -n "$MEMBERS" ] || { echo "--members required (e.g. \"eno1 eno2\")" >&2; exit 1; }
case "$IP" in */*) ;; *) IP="$IP/8";; esac          # default /8 if no prefix
set -- $MEMBERS
[ -z "$PRIMARY" ] && PRIMARY="$1"                     # default primary = first member
DNS_YAML=$(for d in $DNS; do echo "        - $d"; done)
MEM_LIST=$(IFS=,; echo "$*" | sed 's/,/, /g')         # "eno1, eno2, ..."

emit() {
  echo "# ${NODE:+$NODE — }active-backup bond0 on canonical $IP. Members: $MEM_LIST"
  echo "network:"
  echo "  version: 2"
  echo "  renderer: networkd"
  echo "  bonds:"
  echo "    bond0:"
  echo "      interfaces: [$MEM_LIST]"
  echo "      addresses: [$IP]"
  echo "      nameservers:"
  echo "        addresses:"
  echo "$DNS_YAML"
  echo "      routes:"
  echo "        - to: default"
  echo "          via: $GW"
  echo "      parameters:"
  echo "        mode: active-backup"
  echo "        primary: $PRIMARY"
  echo "        mii-monitor-interval: 100"
  echo "  ethernets:"
  for m in "$@"; do echo "    $m: {}"; done
}

if [ -n "$OUT" ]; then emit "$@" > "$OUT"; echo "wrote $OUT" >&2; else emit "$@"; fi
