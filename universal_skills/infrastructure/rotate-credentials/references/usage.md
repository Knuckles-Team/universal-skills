# rotate-credentials — usage, safety, and recovery

## What it does
Sets ONE unified password for an OS account (default `genius`) across many hosts over
SSH, verifies each with `passwd -S`, and reports a per-host OK/FAILED summary. Optionally
rotates the in-band iDRAC/BMC user-2 password too (`--idrac`).

## Prerequisites
- The `--ssh-user` must already have **passwordless sudo** on every target host (the
  script uses `sudo -n`). If sudo prompts, the host reports FAILED.
- SSH key access to every host (full-mesh keys — see the `ssh-bootstrap` skill).
- `--idrac` needs `ipmitool` + `/dev/ipmi0` on Dell/IPMI hosts (in-band, no BMC creds).

## Common invocations
```bash
# Generate a fresh unified password for genius across the whole inventory
rotate-credentials.sh --generate --inventory ~/.config/agent-utilities/inventory.yaml \
    --out ~/Workspace/inventory/.env

# Set a specific password on explicit hosts, also rotate iDRAC user-2
rotate-credentials.sh --password 'S3cret...' --hosts "10.0.0.10 10.0.0.11 10.0.0.13" --idrac

# Preview only — change nothing
rotate-credentials.sh --generate --inventory <file> --dry-run
```

## Safety model
- **Never aborts on a bad host.** Unreachable hosts, sudo-prompt hosts, or hosts where
  the password tools crash are reported `FAILED` and skipped — the rest still rotate.
- **Verification** is `passwd -S <user>` → status field `P` (a usable password is set).
  `L` (locked) or `NP` (no password) is treated as failure.
- The generated password is printed **once** to stdout; capture it. With `--out` it is
  appended to a creds file — that file MUST be gitignored (it holds a plaintext secret).
- Password charset is `[A-Za-z0-9]` (20 chars) to stay safe across shells, `chpasswd`,
  and BMCs (iDRAC IPMI user passwords cap at 16 bytes — the script's `user test 2 16`
  verifies the first 16; for full-length BMC support use 16-char passwords).

## Known host quirks (homelab)
- A host whose `chpasswd`/`passwd` **SIGILLs / core-dumps** (seen on GR1080 — corrupt
  libcrypt/PAM) will report FAILED. Fix the host's libc/PAM, then re-run for just that host.
- `--idrac` only rotates the BMC **user table** (works even if BMC LAN is down). It does
  NOT enable IPMI-over-LAN; do that separately if remote ipmitool/SoL is needed.

## Recovery
If you lose the new password before it's recorded: from any host with passwordless sudo
SSH access, re-run with a known `--password` to set it again. SSH key auth is independent
of the OS password, so a bad rotation never locks you out of SSH (only of console login).
