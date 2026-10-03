---
name: gates-and-code-placement
domain: development
skill_type: skill
description: >-
  What each shared pipelines quality gate actually enforces (complexity, KISS,
  clone, privacy, secret-history) as the hook source implements it, and the
  one-sentence rule for which repository new code belongs in. Use before
  writing code anywhere in the fleet, or when a gate fails and the fix isn't
  obvious from its one-line message.
license: MIT
tags: [pipelines, gates, complexity, kiss, clones, privacy, code-placement]
metadata:
  version: '1.0.0'
---

# Gates and code placement

`pipelines_hooks` is the shared, repository-agnostic pre-commit package every
repository in the fleet consumes (`.pre-commit-hooks.yaml`; run one gate with
`pipelines-hook <id>`). Every gate returns 0 clean, 1 findings, 2 cannot-run.
What follows is read from the gate source and `.config/kiss.toml`, not
restated from policy prose, so it stays correct when a cap changes.

## Complexity (cccc)

Caps, per function, including nested children: **cyclomatic 10, cognitive
15** (`pipelines_hooks/complexity/__init__.py`). Both metrics are measured for
every function in every cccc-supported file; extraction moves complexity into
the child, so a parent that now looks clean is not the whole story.

- `complexity-staged` compares the **staged index** against **HEAD** (never
  the working tree) and fails only a function that is **NEW** over a cap or
  **WORSE** than it was. An existing over-cap function left unchanged passes;
  nothing is written, no count is frozen, and the real numbers print on every
  run — it is diff-scoped, deliberately not a baseline.
- `complexity-census` measures every tracked file and fails on the real
  backlog above zero: no baseline, no allowlist.
- One Rust-only exemption, re-derived from source on every run, never
  persisted as a list of names or files: a flat, exhaustive `match` may exceed
  the cyclomatic cap alone (never the cognitive cap) when its cognitive score
  is within cap, it contains at least one `match`, no arm is irrefutable
  (`_`, a bare binding, or an alternation containing one), and its residual
  (measured cyclomatic minus arm count) is itself within the cyclomatic cap.
  Decomposing an exhaustive match trades away a compiler guarantee for a
  metric, so the rule accepts the residual instead.
- Fix path: split the function or replace branching with dispatch; do not
  raise a threshold or add a suppression comment — the gate's own guidance
  text states an inline suppression is treated as a one-line baseline.

## KISS

`.config/kiss.toml` in the pipelines repository is its own authoritative config — per the
fleet rule that a repository's own KISS config wins over any other copy of
the numbers. Its `[python]` table (verified against `origin/main`): 35
statements/function, 15 local variables, 20 calls/function, 3 positional
args, 1 boolean parameter, 5 returns/function, 3 return values/function, 4
indentation depth, 2 nested function depth, 3 statements/try block, 5
decorators/function, 10 methods/class, 10 functions/file, 30 imported
names/file, 200 statements/file, 300 lines/file, 1 interface type/file.

`branches_per_function`, `keyword_only_args`, `concrete_types_per_file`,
`cycle_size`, `dependency_depth` and `indirect_dependencies` are deliberately
set to an effectively-off value in this file — each is owned by a different
gate instead (branching by cccc, cycles by the import-cycles hook): one
metric, one tool. The pipelines repository has no Rust source and so carries no
`[rust]` table; a repository that does have Rust KISS caps enforces them with
the same pinned `kiss` fork build, from **that** repository's own
`.config/kiss.toml` — read it there rather than assume the Python numbers
above apply, or that any one fleet-wide Rust number is current.

- `kiss-staged` is diff-scoped the same way as `complexity-staged`: only
  findings attributable to the staged change fail; pre-existing debt in a
  touched file stays visible in the census but does not fail the commit.
- `kiss-census` checks every tracked file and fails on any finding — "every
  finding fails, there is no advisory class and no baseline" (the hook's own
  docstring).
- Never invoke the `kiss` binary directly without going through these hooks:
  a bare `kiss check` with no `--config` writes a self-calibrating
  `.kissconfig`, and a multi-path invocation reports a false clean.

## Clone gates

Two independent tools, two different identity mechanisms — read the actual
keying code before assuming either behaves like the other:

- **`jscpd-differential`** compares the base commit's tree against
  `git merge-tree --write-tree <base> HEAD` (the tree this change would
  actually produce, not the branch tip) and fails on any pair present after
  that is absent before. A pair's identity
  (`pipelines_hooks/clones/jscpd_keys.py`) is `(format, sha256 digest of the
  matched fragment text, the pair's two file paths sorted, an ordinal)`.
  **Line numbers and symbol names are never part of the key** — a line shift
  elsewhere does not manufacture a new pair, and renaming a function does not
  remove one: the hash is over the duplicated text itself, not an
  identifier, so the same duplicated body is the same key under any name.
  This gate's own failure message states it plainly: "this gate has no
  suppression mechanism."
- **`dupehound-changed`** flags a changed function that structurally
  reimplements an existing one (detection is structural — shape of the code,
  not its identifier names). It does carry one reviewed register,
  `.config/dupehound-distinct.toml` (not present in the pipelines repository today):
  a **hand-written**, per-entry-justified (12+ word reason required) list of
  pairs a human has reviewed as genuinely distinct. Each entry pins a content
  digest of both functions' normalized text, so it **rots** — fails again —
  the moment either function's body changes, even if neither name does. The
  module's own docstring draws the contrast explicitly: "a baseline is
  machine-written, unexplained and grows by default. This register is
  HAND-WRITTEN, carries a reason per entry, and ROTS." Renaming one side does
  not dodge a real finding either: the underlying detection is structural, so
  the clone still gets reported under the new name, and a register entry
  keyed in part by the old name no longer matches it — it simply reports as
  a fresh, unregistered finding.

## Privacy and secret history

- `tracked-privacy` fails on any finding at all: "the absolute maximum is
  zero findings; there is no count-based allowance." It requires an external
  identity catalog and fails closed (exit 2) rather than scanning a silently
  narrower set when the catalog is missing.
- `secret-history` scans the patch text of every commit in the unpublished
  range (so a credential a later commit deletes still fails it) and has
  **no allowlist file**. The one exemption that exists at all is a reviewed
  inline marker, `# sanitizer:ignore - <reason>`, which must carry a
  non-empty reason after the separator — a bare marker is rejected. This is a
  documented, reviewed, per-line exemption, not a blanket suppression.

**Taken together:** there is no baseline file, no silently-growing allowlist,
and no count-based exemption anywhere in these gates. The two mechanisms that
come closest — the dupehound distinct-pairs register and the secret-history
inline marker — are both hand-written, require a stated reason, and are
designed to force re-review when the code they cover changes, not to
permanently suppress a finding.

## Code placement

One dependency direction runs through the ecosystem's core repositories:
**pipelines → epistemic-graph → agent-connector-sdk → agent-utilities →
agent-webui → graph-os**. Each repository's own `AGENTS.md` states what it
owns under a "What this repository owns" heading — that heading, not this
skill, is the authoritative answer for a specific capability, because it is
what gets kept current as boundaries shift (for example, agent-utilities is
presently contracting to an orchestration-only control plane, with durable
graph/semantics code moving to epistemic-graph and connector code to
agent-connector-sdk rather than staying in agent-utilities).

The rule: **new code goes to the repository that owns that capability, never
to whichever checkout happens to be open.** Durable graph storage, query,
reasoning and semantics belong in epistemic-graph; connector transport,
manifests and certification belong in agent-connector-sdk; the agent
orchestration plane (planning, delegation, skills/workflow runtime) belongs
in agent-utilities; the served MCP/REST/control-plane runtime belongs in
graph-os; shared CI/quality/workflow machinery like this package belongs in
pipelines. When it is not obvious which repository owns a piece of new
behavior, read that repository's own `AGENTS.md` ownership section before
writing anything — do not infer ownership from this table alone, since it is
a pointer, not the contract.
