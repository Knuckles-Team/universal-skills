---
name: host-resource-sampler
skill_type: skill
description: Read-only host resource sampler for diagnosing OOM kills, pressure stalls, swap use, disk exhaustion, and inode exhaustion locally or over SSH. Emits one compact JSON record containing load, memory and swap, Linux PSI for CPU/memory/I/O, the current cgroup-v2 memory limits/current/peak/swap/events, byte and inode usage with warning thresholds for key filesystems, and bounded size measurements for known build targets and caches. Use before or during guarded compilation and as the probe invoked by repository-manager's bounded scheduled runs. It never deletes data, changes limits, starts a scheduler, or remediates the host.
domain: system
license: MIT
tags: [metrics, host, monitoring, psi, cgroup, memory, swap, disk, inode, telemetry]
metadata:
  version: '1.3.1'
  author: Genius
requires:
  - systems-manager-mcp
  - tunnel-manager-mcp
---

# Host Resource Sampler

Collect one read-only, machine-readable health sample from a host. The sampler makes
no system changes and does not launch background work.

Run locally:

```bash
scripts/sample_resources.py
```

The single-line `host-resource-sample/v1` JSON record includes:

- UTC observation time, host name, load averages, memory available, and swap used;
- `/proc/pressure/{cpu,memory,io}` `some`/`full` averages and totals;
- cgroup-v2 `memory.current`, `high`, `max`, `peak`, swap limits/use, and both
  `memory.events` counters, including `oom` and `oom_kill` where available;
- byte and inode capacity for `/`, `/home`, `/tmp`, `/var/tmp`, and every `--path`;
- low-priority, bounded `du` measurements for uv, pip, pre-commit, Torch, and
  Hugging Face caches, `$CARGO_TARGET_DIR` when set, and every `--size-path`.

Missing optional kernel files are represented by empty or null fields. Directory
measurements time out independently after 10 seconds by default, so a large cache
cannot stall the whole sample. Override that bound with `--size-timeout SECONDS`.

## Filesystem thresholds

Byte warnings default to 85% and inode warnings to 80%. Override them per sample:

```bash
scripts/sample_resources.py \
  --disk-byte-warning 90 \
  --disk-inode-warning 75 \
  --path /srv \
  --size-path /var/tmp/build-target
```

Each filesystem record carries `byte_warning` and `inode_warning` booleans. An inode
warning matters even when many bytes remain: creating logs, sockets, lock files, or
compiler outputs can fail once the inode pool is exhausted.

## Guarded periodic use

`repository-manager` remains the authority for guarded runs and scheduling. Have its
bounded runner invoke this script with a short runtime limit, a small cgroup memory
limit, and stdout captured by the existing rotated journal/log destination. The script
emits exactly one JSON line and performs no automatic deletion, which makes repeated
samples append-safe. Do not install a second timer or cron entry from this skill.

For a remote host, invoke the same command with `tunnel-manager-mcp`, or use
`systems-manager-mcp` to collect equivalent fields. Fan-out belongs to the calling
workflow; this atomic skill samples one host per invocation.
