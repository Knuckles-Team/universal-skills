# Code-Enhancer Evolution Log

A running, evidence-anchored record of how the skill is tuned. Every rubric change,
false-positive fix, or new capability gets an entry here citing the **domain output
that prompted it** — so the skill evolves from observed misses, not guesswork. This
is the skill's feedback loop (it previously had none: it monitored regressions via
baselines but never fed observations back into its own rules).

## How to add an entry
When a run surfaces a false positive, a miss, or an over/under-harsh score:
1. Add a dated entry below with: **domain**, **evidence** (repo + finding), **kind**
   (`false-positive` | `miss` | `scoring` | `capability` | `doc`), **change**, and the
   **script/reference touched**.
2. Make the code/rubric change.
3. Re-run the affected analyzer and record the before→after score.

Keep entries terse. Newest first.

---

## 2026-06-14 — Audit of agent-utilities (v0.49.0, ~415K LOC, 692 test files)

First full run against agent-utilities. Six changes, all grounded in its output.

### CE-042 (capability) — dependency-update application
- **Evidence:** `dependencies` domain is report-only; the user needs the skill to
  also *update* versions. `audit_dependencies.py` had no write path.
- **Change:** new `scripts/apply_dependency_updates.py` — bumps floors/caps in
  `pyproject.toml` + `requirements.txt` losslessly (only version operands change;
  extras/markers/comments/order preserved), `--level {patch,minor,major}`,
  `--apply`/dry-run diff, `--only`/`--skip`, `--self-test`. Reuses
  `audit_dependencies._get_latest_version` (one PyPI path). Excludes the project's
  own self-referential extras (e.g. `agent-utilities[owl]`).
- **Touched:** `scripts/apply_dependency_updates.py` (new), `scripts/selftest.py`,
  `scripts/enhance_repo.py` (opt-in `--apply-deps`).

### concepts — false-positive + scoring (30 → 75)
- **Evidence:** "68 orphaned / 69 drift / 6666 test functions missing markers". Root
  cause: `trace_concepts.py` read the registry only from `AGENTS.md` and ignored
  `docs/concepts.yaml` — the repo's canonical, auto-generated registry (259 IDs from
  `CONCEPT:` markers). The code+docs+tests triple-coverage model mis-flagged
  code+yaml concepts as orphans/drift and demanded markers on all 6666 tests.
- **Kind:** false-positive + scoring.
- **Change:** load `docs/concepts.yaml`/`concepts.yml` (+ `AGENTS.md`) as a canonical
  registry source; a concept is well-traced with ≥2 of {registry, code, docs, tests};
  redefine drift as "code marker absent from the canonical registry" (a real
  stale-registry signal — found 8); demote test/function missing-marker penalties to
  **informational** when a registry exists.
- **Touched:** `scripts/trace_concepts.py`.

### security — false-positive + severity + scoring (still F, but honest)
- **Evidence:** 13 High / 77 Med, score 0. 5× "Hardcoded Credentials" were ALL FPs:
  `TOKEN_BUDGET_MAX` (number), `SECRET`/`TOP_SECRET` (government classification enum
  *values*), `ANOMALY_TOKENS` (count), `secret_engine_id` (Vault engine id). `exec()`
  in a test fixture flagged. Every `subprocess.Popen` (list args, no shell) rated High.
  Absolute deductions floored any large repo to 0.
- **Kind:** false-positive + scoring.
- **Change:** (a) gate CWE-798 on the VALUE shape (entropy/length, exclude
  placeholder/enum words and `*_id|_max|_count|_tokens|_budget|...` names), not the
  identifier name; (b) suppress CWE-94/502/798 in test files (already CWE-78); (c)
  `subprocess.*` is Medium unless `shell=True`; (d) cap Med/Low deductions (−40/−15)
  and drop the eval/exec + subprocess attack-surface double-count. Result: 13→2
  genuine code Highs (eval, sandbox exec); score reflects real attack surface, not FPs.
- **Touched:** `scripts/analyze_security.py`.

### directory_density — false-positive (33 → 45)
- **Evidence:** flagged `validate_mcp_config.py`, `validate_diagrams.py` as "rogue
  /throwaway"; penalized `tests/` for >40 files.
- **Kind:** false-positive.
- **Change:** drop over-generic verb prefixes (`validate_`/`resolve_`/`debug_`) from the
  rogue list; exempt dedicated tooling dirs (`scripts/tools/bin/ci`); apply a 2× density
  threshold to test directories (suites legitimately mirror source breadth).
- **Touched:** `scripts/analyze_directory_density.py`.

### env_vars — scoring (55 → 80)
- **Evidence:** "Only 9% of env vars documented in README" on a ~261-config platform
  that documents env vars in `docs/`, not the README.
- **Kind:** scoring (under-credit).
- **Change:** credit env vars documented in `README.md`, `AGENTS.md`, `docs/**/*.md`,
  `.env.example` templates, and `*config*reference*` files before computing coverage.
- **Touched:** `scripts/scan_env_vars.py`.

### SKILL.md — doc accuracy
- **Evidence:** SKILL.md referenced `audit_concept_ids.py`, `detect_circular_deps.py`,
  `audit_env_var_standard.py` — none present in `scripts/`. Domain counts didn't match
  the 19 default (+2 opt-in) wired in `enhance_repo.py`.
- **Kind:** doc.
- **Change:** reconcile the Scripts list/capabilities with what actually ships; add
  CE-042; note the missing scripts as folded/not-yet-present.
- **Touched:** `SKILL.md`.

### CE-043 (capability) — dependency migration intelligence
- **Evidence:** user asked whether the skill ensures we *adopt new features* and
  *remove deprecations* introduced by dependency upgrades. The audit flagged version
  deltas but never cross-referenced changes against OUR code.
- **Change:** new `scripts/analyze_dependency_migration.py` — for each upgradable
  package (major/minor): (a) parse its changelog Added/Deprecated/Removed in the
  crossed version range (reusing `audit_changelog._get_dependency_changelog_url` /
  `_fetch_and_parse_changelog`); (b) statically map dist→import names
  (`importlib.metadata.packages_distributions`) and intersect Deprecated/Removed
  entries with the symbols our code actually imports; (c) opt-in `--run` imports the
  project under DeprecationWarning capture and keeps only warnings whose call site is
  in our tree. Scored; `--self-test`. Registered in selftest (27/27).
- **Touched:** `scripts/analyze_dependency_migration.py` (new), `scripts/selftest.py`,
  `SKILL.md`.

### CE-042 (bug) — apply_dependency_updates must skip pre-releases
- **Evidence:** applying `--level major` to agent-utilities ADDED a floor at
  `opentelemetry-instrumentation-asgi>=0.63b1` (PyPI's "latest" for these otel
  packages is a beta), which made the uv workspace unresolvable.
- **Change:** guard `_new_spec_for` to skip when `Version(latest).is_prerelease` /
  `is_devrelease` — never pin to a pre-release. Added self-test cases.
- **Touched:** `scripts/apply_dependency_updates.py`.

### Phase-3 pin-backs (data point for the workspace-resolution lesson)
Applying ALL bumps incl. major to agent-utilities (a uv *workspace* member) required
5 pin-backs to keep the whole workspace `uv lock`-able — each a real transitive cap
from a SIBLING package, not an agent-utilities bug:
1. `pydantic-ai-slim`/`pydantic-graph` 1.107→1.106 — `pydantic-acp==0.9.6` strictly
   pins `pydantic-ai-slim==1.106.0`.
2. `pandas` 3.0.3→`>=2.0.0,<3` — `llama-index-readers-file` caps `pandas<3`.
3. `packaging` 26.2→`>=24.2,<26` — every `mlflow` 3.x needs `packaging<26` (via
   `data-science-mcp[tracking]`).
4. `cryptography` 49.0.0→`>=48.0.0,<49` — mlflow needs `cryptography<49`.
5. `opentelemetry-instrumentation-{starlette,fastapi,asgi}` → unpinned (the beta-floor
   bug above + a mistral-extra clash).
**Lesson for the skill:** in a monorepo/workspace, `apply_dependency_updates` should
offer a workspace-aware mode (lock after apply, auto-pin-back on the named transitive
conflict). Logged as a future enhancement.

## 2026-06-14 (batch 2) — analyzer accuracy fixes (CE-044)

Implementing the open findings against agent-utilities revealed the analyzer
*over-counted* by not honoring the repo's lint config / suppression conventions.
Fixed so future reports reflect the real enforced gate (evidence = this run):

- **run_linters.py** — ruff/mypy/bandit now exclude the conventional gate dirs
  (`tests`/`test`/`scripts`/`script`); bandit uses the fleet-standard skip-set and
  honors inline `# nosec`. Result on agent-utilities: **1139 → 109** findings (ruff 0,
  bandit 418→10, mypy 721→99). The residual mypy is the package's genuine
  non-blocking type backlog, not noise.
- **analyze_security.py** — respect inline `# nosec`: skip any finding whose AST span
  carries one. Removes the intentional, already-annotated eval/exec/pickle/subprocess
  highs (the repo documents these trust boundaries).
- **audit_documentation.py** — broken-reference detection now validates only real
  markdown links `[text](path)`, not backticked code spans / glob patterns / `@imports`
  in prose. Result on agent-utilities: **23 broken refs → 0** (all were FPs);
  documentation 82 → 97.
- **grade_pytest.py** — assertion detection recognizes unittest `self.assert*`,
  `pytest.warns`, numpy/pandas `testing.assert*`, and documented "must not raise"
  smoke tests. no-assertion count 40 → 26.

selftest 27/27. These align the report to what the project's pre-commit actually
enforces, so a clean repo no longer reads as failing.

### Confirmed REAL (kept — not FPs)
- `changelog` (85 B): latest release heading `## [0.3.0] - 2026-05-02` vs pyproject
  `0.49.0` — genuine version drift.
- `codebase` (42 F): `kg_server.py` 7130L / `_build_server` CC=652, `multiplexer.py`
  1614L — real monoliths.
- `tests`: timed out at 300s (≈6900 tests) — expected; run a subset for grading.
