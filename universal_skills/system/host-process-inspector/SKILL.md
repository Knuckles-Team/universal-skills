---
name: host-process-inspector
description: Read-only host process inspector for a hot, slow, or swap-thrashing machine. Over SSH via tunnel-manager (or systems-manager) it ranks the worst CPU/RAM offenders, finds zombie/defunct processes and names their non-reaping parent, flags orphaned-to-PID1 runaways (a search or job whose launching session exited and got reparented to init), detects swap exhaustion and which processes hold the most swap, lists uninterruptible D-state processes, and — best effort — maps a culprit PID back to its owning tmux session. Produces a ranked hog report with kill/reap candidates and a load-vs-cores verdict. Use when a host's load is high, a box feels sluggish, or leaked/zombie processes are suspected. Read-only — it NEVER kills, reaps, or tunes anything; pair it with the systems-issue-troubleshooter workflow or host-doctor for gated remediation. Not for disk cleanup (use host-disk-reclaimer) or plain resource sampling (use host-resource-sampler).
license: MIT
tags: [system, host, process, zombie, runaway, swap, cpu, diagnostics, ops, ssh]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
requires:
  - tunnel-manager-mcp
  - systems-manager-mcp
---

# Host Process Inspector

Find **what is actually eating a host** — runaway processes, leaked/zombie children,
and swap exhaustion — and rank them. This skill **only inspects**; it never kills,
reaps, or changes anything. It produces the evidence and the candidate list that a
human (or the `host-doctor` / `systems-issue-troubleshooter` workflow) then acts on.

## Golden rules
- **Read-only, always.** Every command here is a `ps` / `free` / `/proc` read. No
  `kill`, no `swapoff`, no service restart. Remediation is a separate, gated step.
- **Rank by impact, not by name.** A process named `claude` or `python` may actually
  be a runaway `ugrep` or an MCP server — read the **full cmdline** (`/proc/<pid>/cmdline`),
  not just `comm`. The truncated name lies; the argv tells the truth.
- **Judge load against cores.** Load 8 on a 64-core box is idle; load 37 on 24 cores is
  on fire. Always divide by `nproc`.
- **Zombies hold no CPU or RAM.** A `<defunct>` process is a dead process-table entry
  (a PID slot + exit code) waiting for its parent to `wait()`. It is never the resource
  problem — report it, name the buggy parent, but do not treat a low zombie count as the
  cause of a hot box. Look for runaways first.
- **Verify identity before naming a kill candidate.** PIDs recycle. Re-read the cmdline
  at report time so a recommendation points at the process you actually saw.

## What to look for (the five signals)

### 1. Runaway / orphan hogs (usually the real culprit)
The worst offender is typically a long-lived, high-CPU process whose launching session
died, leaving it **reparented to PID 1 (systemd/init)** with nothing to reap it.

```
ps -eo pid,ppid,user,pcpu,pmem,etime,args -ww --sort=-pcpu | head -15
```
Flag any row where **`pcpu` is large AND `etime` is long (hours/days) AND `ppid == 1`** —
that is an orphaned runaway (the canonical case: a recursive `grep`/`ugrep`/`find`
launched from a code session that escaped to scan `/` and never stopped). Confirm the
real command:
```
tr "\0" " " < /proc/<pid>/cmdline; echo
readlink /proc/<pid>/cwd
```

### 2. Zombie / defunct processes + their parents
```
ps -eo stat=,ppid,pid,user,args | grep -E "^Z"
```
For each zombie, identify the **parent that isn't reaping it** (the `ppid`):
```
ps -o pid,ppid,etime,nlwp,stat,args -ww -p <ppid>
```
Report `zombie -> parent (cmd)`. A parent that re-spawns a short-lived child every poll
cycle and reaps it a cycle late will always show ~1 lingering zombie — note it as a minor
parent bug, not a leak.

### 3. Swap exhaustion + who is in swap
```
free -m            # flag if Swap used / total > 80%
```
Find the biggest swap holders (per-process `VmSwap` from `/proc`):
```
for d in /proc/[0-9]*; do s=$(awk "/VmSwap/{print \$2}" $d/status 2>/dev/null); \
  [ -n "$s" ] && [ "$s" -gt 0 ] && echo "$s ${d#/proc/} $(cat $d/comm 2>/dev/null)"; \
done | sort -rn | head -10
```
Full swap thrashes I/O and inflates load via wait states. Distinguish *active* swappers
(large resident + still busy) from *cold* pages parked long ago by idle processes.

### 4. Uninterruptible (D-state) processes
```
ps -eo stat=,pid,args | grep -E "^D"
```
D-state = blocked in a kernel call (usually I/O or a stuck mount). Many D-state procs
explain a high load with low CPU — point at the underlying device/mount, not the procs.

### 5. tmux attribution (best effort, per user)
When a hog belongs to an interactive session, map it back so the user knows which window
to look at. List panes, then walk the process tree up to a pane's shell:
```
tmux list-panes -a -F "S=#{session_name} W=#{window_index}:#{window_name} pane_pid=#{pane_pid} cmd=#{pane_current_command}"
pstree -s -p <pid>
```
If `pstree -s -p <pid>` reaches a `bash` whose pid equals a `pane_pid`, the hog belongs to
that session. An orphan (ppid 1) belongs to **no** pane — say so explicitly.

## Default thresholds (tune per host)
| Signal | Flag when |
|--------|-----------|
| Load | `load_1m / nproc > 1.0` (sustained) |
| Single process | `pcpu > 200%` **and** `etime > 1 day` |
| Orphan runaway | above **and** `ppid == 1` |
| Swap | `used / total > 0.80` |
| Zombies | `count > 0` (report; rarely urgent) |

## Output
A ranked report: per host, the load-vs-cores verdict, the top CPU/RAM offenders with
**full cmdlines**, the orphan-runaway list (the safe, high-value kill candidates),
zombie→parent pairs, swap pressure + top swap holders, any D-state blockers, and tmux
attribution where found. End with a prioritized **candidate** list (kill / reap / tune)
for a human to approve — never an action taken.

## Remote hosts
Host-agnostic. For a remote machine, run each probe over SSH via `tunnel-manager`
(`tm__remote action=run_command host=<alias-or-ip>`) or fan out across a group with
`tm__inventory action=run_command group=<group>`. `systems-manager`'s `list_processes`
(returns per-process `status`, so `status == "zombie"` is directly detectable) and
`get_os_statistics` are an alternative structured source when SSH fan-out isn't wanted.

## Known gotchas (from real runs)
- **The remote `bash -c` wrapper breaks nested single-quotes.** `tm__remote` wraps your
  command in `bash -c '...'`, so an inner `awk '$1 ~ /Z/'` aborts with *"unexpected EOF
  while looking for matching `'`"*. Author probes with **double quotes** and headerless
  `ps -eo field=` forms, or `grep -E "^Z"` instead of an awk single-quote pattern.
- **`comm` (and `pstree`) can disagree with the real command.** A process can report
  `comm=claude` while its `/proc/<pid>/cmdline` is a `ugrep ... /`. Trust the cmdline.
- **Load is a moving average.** After you remove a big hog, `load_1m` decays over
  ~1–15 min — re-sample a few minutes later before declaring victory; the instantaneous
  `ps --sort=-pcpu` picture recovers immediately.
- **`du`/full-`/`-scan hogs are the classic leak** — an orphaned recursive search at
  hundreds of %CPU for days is pure waste and the single safest, highest-value kill.
- **tmux is per-user.** `tmux list-sessions` only sees the server for the SSH login user;
  a hog under another user's tmux won't map — note it as unattributed rather than guessing.
