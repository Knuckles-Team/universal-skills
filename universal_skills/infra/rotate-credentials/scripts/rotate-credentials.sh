#!/usr/bin/env bash
# rotate-credentials.sh — set ONE unified password for an OS account across many hosts
# over SSH, verify each, and report. Optionally rotate the in-band iDRAC/BMC user too.
#
#   rotate-credentials.sh --hosts "10.0.0.10 10.0.0.11 ..." [options]
#   rotate-credentials.sh --inventory ~/.config/agent-utilities/inventory.yaml [options]
#
# Options:
#   --user NAME        OS account to set the password for (default: genius)
#   --password PW      use this password (otherwise --generate)
#   --generate         generate a strong 20-char alnum password (printed once)
#   --ssh-user NAME    SSH login user (default: genius); needs passwordless sudo on hosts
#   --hosts "a b c"    space-separated host IPs/names
#   --inventory FILE   pull hosts from an Ansible-style inventory (ansible_host: lines)
#   --idrac            also set iDRAC/BMC user-2 password in-band (sudo ipmitool)
#   --out FILE         append the credential record to FILE (e.g. inventory/.env)
#   --dry-run          show what would happen, change nothing
#
# Requires: passwordless sudo for --ssh-user on each host. Hosts where the password
# tools crash/away (e.g. SIGILL, unreachable) are reported FAILED and SKIPPED, never
# aborting the run. Verification uses `passwd -S` (status 'P' = usable password set).
set -uo pipefail

USER_NAME="genius"; PASSWORD=""; GENERATE=0; SSH_USER="genius"
HOSTS=""; INVENTORY=""; IDRAC=0; OUT=""; DRY=0
while [ $# -gt 0 ]; do case "$1" in
  --user) USER_NAME="$2"; shift 2;;
  --password) PASSWORD="$2"; shift 2;;
  --generate) GENERATE=1; shift;;
  --ssh-user) SSH_USER="$2"; shift 2;;
  --hosts) HOSTS="$2"; shift 2;;
  --inventory) INVENTORY="$2"; shift 2;;
  --idrac) IDRAC=1; shift;;
  --out) OUT="$2"; shift 2;;
  --dry-run) DRY=1; shift;;
  *) echo "unknown arg: $1" >&2; exit 1;;
esac; done

if [ -n "$INVENTORY" ]; then
  HOSTS="$HOSTS $(grep -oE 'ansible_host:[[:space:]]*[0-9.]+' "$INVENTORY" 2>/dev/null | grep -oE '[0-9.]+')"
fi
HOSTS=$(echo "$HOSTS" | tr ' ' '\n' | grep -v '^$' | sort -u | tr '\n' ' ')
[ -n "$HOSTS" ] || { echo "no hosts (use --hosts or --inventory)" >&2; exit 1; }

if [ -z "$PASSWORD" ] && [ "$GENERATE" = 1 ]; then
  PASSWORD=$(LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 20)
  echo "GENERATED password for '$USER_NAME': $PASSWORD"
fi
# No password supplied and not generating: prompt securely at the terminal (hidden input).
# This keeps the secret out of shell history / process args / any transcript.
if [ -z "$PASSWORD" ]; then
  if [ -t 0 ]; then
    read -r -s -p "New password for '$USER_NAME': " PASSWORD; echo
    read -r -s -p "Confirm password: " PASSWORD2; echo
    [ -n "$PASSWORD" ] || { echo "empty password" >&2; exit 1; }
    [ "$PASSWORD" = "$PASSWORD2" ] || { echo "passwords do not match" >&2; exit 1; }
  else
    echo "provide --password or --generate, or run in a terminal to be prompted" >&2; exit 1
  fi
fi

SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8"
ok=0; fail=0; report=""
for h in $HOSTS; do
  if [ "$DRY" = 1 ]; then echo "DRY $h: would set $USER_NAME password (+idrac=$IDRAC)"; continue; fi
  host=$($SSH "$SSH_USER@$h" "echo \"$USER_NAME:$PASSWORD\" | sudo -n chpasswd 2>&1 && \
    st=\$(sudo -n passwd -S $USER_NAME 2>/dev/null | awk '{print \$2}'); \
    [ \"\$st\" = P ] && echo OK || echo VERIFY_FAIL:\$st" 2>&1 | tail -1)
  if echo "$host" | grep -q '^OK$'; then
    line="$h: OS=OK"
    if [ "$IDRAC" = 1 ]; then
      ir=$($SSH "$SSH_USER@$h" "sudo -n ipmitool user set password 2 '$PASSWORD' >/dev/null 2>&1 && \
        sudo -n ipmitool user test 2 16 '$PASSWORD' 2>&1 | grep -qi success && echo idrac_ok || echo idrac_fail" 2>&1 | tail -1)
      line="$line iDRAC=$ir"
    fi
    echo "$line"; report="$report\n$line"; ok=$((ok+1))
  else
    line="$h: FAILED ($host)"; echo "$line"; report="$report\n$line"; fail=$((fail+1))
  fi
done

echo ""; echo "=== rotated $ok OK, $fail failed ==="
if [ -n "$OUT" ] && [ "$DRY" != 1 ]; then
  { echo ""; echo "# unified credential rotated $(hostname) $(date -u +%FT%TZ 2>/dev/null || echo now)";
    echo "ROTATED_USER=$USER_NAME"; echo "ROTATED_PASSWORD=$PASSWORD";
    echo -e "# per-host:$report"; } >> "$OUT"
  echo "appended credential record to $OUT"
fi
