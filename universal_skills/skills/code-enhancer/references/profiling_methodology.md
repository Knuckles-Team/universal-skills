# Runtime & Scale Profiling Methodology

How code-enhancer profiles what a *running instance* of a project actually costs,
and how many instances fit in a memory budget. Covers domains **CE-036 Runtime
Profiling** (`analyze_runtime_profile.py`) and **CE-037 Scale Profiling**
(`analyze_scale_profile.py`).

Both domains **execute the target** (import its entry module / spawn instances),
so they are **opt-in**: skipped in the default sweep, run only when named, e.g.
`enhance_repo.py <repo> --domains runtime_profile,scale_profile`.

## What gets measured

### Runtime Profiling (CE-036)
- **Import RSS** — resident memory the entry module pulls in, measured in an
  isolated child via `/proc/self/status` `VmRSS` before/after `import`.
- **Import wall time** and the **heaviest transitive imports**, parsed from
  `python -X importtime`. This is the single most diagnostic signal for a memory
  blow-up: it shows exactly which dependency is loaded into *every* process.
- **Heavy-dependency flag** — if `torch`, `transformers`, `playwright`, etc. load
  unconditionally at import, that is surfaced as a finding (lazy-import them or
  move them behind a service boundary).

Crucially it profiles the **console-script entry module** (from
`[project.scripts]`), not the bare top-level `__init__` — a thin `__init__` hides
the real import weight and yields a falsely rosy score.

### Scale Profiling (CE-037)
- Spawns **N idle instances** concurrently (import + idle, no main loop — a
  faithful proxy for a just-started instance's base footprint), samples each
  child's RSS, and reports **per-instance MB**, **instances/GB**, and a
  projection against common RAM sizes (1/2/4/8 GB).

## Budgets & scoring

| Signal | Good (100 pts) | Bad (0 pts) |
|---|---|---|
| Import RSS | ≤ 80 MB | ≥ 400 MB |
| Import wall time | ≤ 300 ms | ≥ 2000 ms |
| Density | ≥ 12 instances/GB | ≤ 2 instances/GB |

Runtime score = 60% memory + 40% startup, linear between bounds. Scale score is
linear on instances/GB. These are tuned for CLI/TUI/service processes; adjust the
constants at the top of each script for heavier app classes.

## Interpreting results — the common failure mode

A lightweight tool that imports to tens of MB but spikes to hundreds of MB / GB in
production is almost always **importing a heavy backend into the frontend process**
on some non-startup path (a dashboard, an optional command). The fix is to keep the
frontend free of the heavy package and talk to it over a service boundary (HTTP),
and to add an import-guard test that fails if the heavy module enters `sys.modules`.
The `importtime` heaviest-imports list points straight at the offender.

## Per-language tooling (beyond the automated Python path)

`analyze_runtime_profile.py` automates Python and emits a neutral score plus a
tool matrix for other ecosystems:

| Language | Memory | CPU / startup |
|---|---|---|
| Python | memray, tracemalloc, `-X importtime`, `/proc` RSS | py-spy, cProfile, hyperfine |
| Rust | heaptrack, `valgrind --tool=massif` | `cargo flamegraph`, hyperfine |
| Go | `pprof` (runtime/pprof) | `go test -bench`, pprof, hyperfine |
| Java | `jmap -histo`, JFR | async-profiler, JFR, hyperfine |
| Node/TS | `node --prof`, clinic.js heap | `node --prof`, 0x, clinic.js, hyperfine |

`memray` and `py-spy` are optional extras; the scripts degrade to stdlib
(`tracemalloc` / `resource` / `/proc`) when they are not installed.

## Safety

These domains run the target's import-time code and spawn processes. Run them on
trusted repositories only, the same trust model as the existing `run_tests` and
`run_precommit` domains. Scale profiling never runs by default.
