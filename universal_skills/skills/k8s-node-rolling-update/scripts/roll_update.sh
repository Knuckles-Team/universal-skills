#!/usr/bin/env bash
# roll_update.sh — roll OS package updates across the homelab's RKE2 cluster one node at a
# time: cordon -> drain -> SSH apt upgrade -> conditional reboot -> wait Ready -> uncordon.
# Aborts the whole run rather than cascading if any node fails a step.
#
#   ./roll_update.sh [--dry-run] [--include-gb10] [--yes] [node ...]
#
# With no node arguments, rolls the default order: workers first, control-plane last,
# gb10 excluded unless --include-gb10 is given:
#   r510 r710 rw710 [gb10] r820
#
# Passing explicit node names overrides the default list (still validated against the
# known fixed node/IP table below — no arbitrary hostnames are accepted).
#
# Requires: kubectl (pointed at the cluster kubeconfig), ssh access to each node as
# `genius` with passwordless sudo.
set -euo pipefail

# --- fixed, known-good node -> IP table (no unsanitized input reaches ssh/kubectl) ---
declare -A NODE_IP=(
  [r510]="10.0.0.10"
  [r710]="10.0.0.11"
  [rw710]="10.0.0.12"
  [gb10]="10.0.0.18"
  [r820]="10.0.0.13"
)
DEFAULT_WORKERS=(r510 r710 rw710)
GB10=(gb10)
CONTROL_PLANE=(r820)

SSH_USER="genius"
DRAIN_TIMEOUT="300s"
READY_TIMEOUT="600s"
DRY_RUN=0
INCLUDE_GB10=0
ASSUME_YES=0
EXPLICIT_NODES=()

usage() {
  sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
}

# --- args ---
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --include-gb10) INCLUDE_GB10=1; shift ;;
    --yes|-y) ASSUME_YES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) echo "unknown flag: $1" >&2; usage; exit 1 ;;
    *) EXPLICIT_NODES+=("$1"); shift ;;
  esac
done
EXPLICIT_NODES+=("$@")

log()  { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }
run()  { # run <description> <cmd...>  -- honors --dry-run
  local desc="$1"; shift
  if [ "$DRY_RUN" = 1 ]; then
    log "DRY-RUN would run: $*"
    return 0
  fi
  log "$desc"
  "$@"
}
ssh_node() { # ssh_node <node> <remote-command-string>
  local node="$1" cmd="$2"
  ssh -o BatchMode=yes -o ConnectTimeout=10 "${SSH_USER}@${NODE_IP[$node]}" "$cmd"
}

# --- resolve node order ---
NODES=()
if [ "${#EXPLICIT_NODES[@]}" -gt 0 ]; then
  for n in "${EXPLICIT_NODES[@]}"; do
    if [ -z "${NODE_IP[$n]+x}" ]; then
      echo "unknown node: $n (known: ${!NODE_IP[*]})" >&2
      exit 1
    fi
    NODES+=("$n")
  done
else
  NODES+=("${DEFAULT_WORKERS[@]}")
  [ "$INCLUDE_GB10" = 1 ] && NODES+=("${GB10[@]}")
  NODES+=("${CONTROL_PLANE[@]}")
fi

log "Node order for this run: ${NODES[*]}"
if [ "$ASSUME_YES" != 1 ] && [ "$DRY_RUN" != 1 ]; then
  read -r -p "Proceed rolling these ${#NODES[@]} node(s), one at a time? [y/N] " reply
  case "$reply" in [yY]|[yY][eE][sS]) ;; *) echo "aborted."; exit 1 ;; esac
fi

# --- per-node rolling sequence ---
# NOTE: this function is invoked as `if ! roll_one_node ...; then` below, which — per bash
# semantics — suspends `set -e` for the whole call. Every fallible step therefore checks its
# own exit status explicitly and returns 1 on failure; nothing here relies on inherited -e.
roll_one_node() {
  local node="$1"
  log "=== ${node} (${NODE_IP[$node]}) : starting ==="

  run "cordon ${node}" kubectl cordon "$node" || { log "FAILED: cordon ${node}"; return 1; }

  run "drain ${node} (ignoring DaemonSets, timeout ${DRAIN_TIMEOUT})" \
    kubectl drain "$node" --ignore-daemonsets --delete-emptydir-data --force \
    --timeout="$DRAIN_TIMEOUT" || { log "FAILED: drain ${node} (left cordoned)"; return 1; }

  if [ "$DRY_RUN" = 1 ]; then
    log "DRY-RUN would ssh ${node}: apt-get update && apt-get -y upgrade"
  else
    log "patching ${node} over ssh (apt-get update && upgrade)"
    ssh_node "$node" 'sudo apt-get update && sudo apt-get -y upgrade' \
      || { log "FAILED: apt upgrade on ${node} (left cordoned)"; return 1; }
  fi

  local reboot_required=0
  if [ "$DRY_RUN" = 1 ]; then
    log "DRY-RUN would check /var/run/reboot-required on ${node}"
  elif ssh_node "$node" 'test -f /var/run/reboot-required'; then
    reboot_required=1
  fi

  if [ "$reboot_required" = 1 ]; then
    if [ "$DRY_RUN" = 1 ]; then
      log "DRY-RUN would reboot ${node} (reboot-required present)"
    else
      log "rebooting ${node} (reboot-required present)"
      # The connection always drops as the node reboots, so a non-zero ssh exit here is
      # expected, not a failure signal — do not treat it as fatal.
      ssh_node "$node" 'sudo reboot' || true
      log "waiting for ${node} to leave the old boot before polling for Ready"
      sleep 15
    fi
  else
    log "${node}: no reboot required, skipping reboot"
  fi

  run "wait for ${node} Ready (timeout ${READY_TIMEOUT})" \
    kubectl wait --for=condition=Ready "node/${node}" --timeout="$READY_TIMEOUT" \
    || { log "FAILED: ${node} did not return Ready in time (left cordoned)"; return 1; }

  if [ "$DRY_RUN" = 1 ]; then
    log "DRY-RUN would verify rke2-agent/rke2-server active on ${node}"
  elif ! ssh_node "$node" 'systemctl is-active --quiet rke2-agent || systemctl is-active --quiet rke2-server'; then
    log "FAILED: rke2 service not active on ${node} after reboot (left cordoned)"
    return 1
  fi

  run "uncordon ${node}" kubectl uncordon "$node" || { log "FAILED: uncordon ${node}"; return 1; }

  log "=== ${node} : done ==="
}

for node in "${NODES[@]}"; do
  if [ "$node" = "gb10" ]; then
    log "NOTE: gb10 has a known intermittent hardware power-fault (power-cycles every"
    log "      12-35 min on its own). A failure here may be unrelated to this patch —"
    log "      verify before assuming the roll broke it."
  fi
  if ! roll_one_node "$node"; then
    log "ABORT: ${node} failed to roll cleanly. Stopping — remaining nodes were NOT touched."
    log "       ${node} is left cordoned; see SKILL.md 'Rollback / abort guidance'."
    exit 1
  fi
done

log "All ${#NODES[@]} node(s) rolled successfully: ${NODES[*]}"
kubectl get nodes -o wide
