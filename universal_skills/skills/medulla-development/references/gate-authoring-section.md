## 4. Authoring a gate — how not to ship coverage you do not have

The most repeated failure in this program is not a gate that fails; it is a gate
that **reports coverage it does not have**. One passed on an empty universe; one
measured two of the five properties it claimed; one crashed and still looked
green. A gate is a claim about the world, and an unfalsified claim is worth
nothing. Four rules. The evidence for each — the full worked instances, with the
`file:line` you can open — is in
[`references/gates-reference.md`](references/gates-reference.md) →
*"Evidence behind the gate-authoring rules"*.

### 4.1 Prove it FAILS on a known-bad input before you trust a pass

A gate you have only ever seen pass has demonstrated nothing (**G4**; §7.5 is
the same rule for fixes). Construct the violation the gate exists to catch, run
it, watch it exit non-zero, then remove the violation. If you cannot construct
the bad input, you do not yet know what the gate enforces.

**A gate whose universe is empty must FAIL (G9). Copy this shape** —
`scripts/check_mint_lease_call_sites.py:88-95` refuses its own empty universe
with *"found ZERO calls … either the scan paths drifted or the feature was
deleted … don't let it go quietly blind."* ⚠ It is nearly alone: measured
2026-09-04 across the 27 `scripts/check_*.py` gates, **24 have no emptiness test
at all** and only this one turns a test into a refusal (command in the
reference; it is a heuristic, so audit the gate you copy from).

### 4.2 State the universe and the denominator, in the gate's own output

**G1 applies to gates, not only to reports.** A gate must print what it
*scanned*, not only what it found: "0 violations in 0 files" and "0 violations
in 1,077 files" are different verdicts and most output cannot tell them apart.
Two live instances, both in the reference: a universe that silently **grew**
(`arch-lint.toml` excludes `**/target/**`, but the committed target dir is
`target-isolated`, so 1,144 of 4,642 findings are vendored codegen), and one
that silently **emptied** (a real `git commit` exports `GIT_DIR`/`GIT_INDEX_FILE`
into every hook and `git -C <root> ls-files` does **not** override them; a
liveness gate reported `orphan_modules: 4 → 196` with zero source changes).

Two independent fixes for that second one already exist here —
`scripts/_git_subprocess_env.py` and `scanner_contract.run_git`/`sanitized_env` —
while two gates still call `git ls-files` with no `env=`. Adopt one of the two;
write neither a third nor a bare call. **Test a suspect gate both ways:** plain,
then with `GIT_DIR` and `GIT_INDEX_FILE` set to the worktree's real gitdir and
index. Different answers mean the universe is ambient, not declared.

### 4.3 Never key a gate on a byte offset, a line number, or a symbol name

All three have broken here. A gate keyed on the **text** of the code cannot
distinguish a contract that was **lost** from one that **moved** — and
refactoring moves things, which is the whole point of the work these gates
supervise. The false positive is the expensive direction: it reds the tree,
sends someone to fix correct code, and trains everyone to override the gate.

`scripts/check_exact_fault_restart_harness.py` fails today with **18 missing
literals, every one of which is present in the tree** — a file became a module
directory, a function moved into a submodule, and a parameter type was
*tightened* from a raw `WriteTransaction` to the validated `MutationWrite`. Its
sibling `persisted-mutation-contract` fails the mirror-image way (it expects a
module **directory** where the tree has a file). Full table in the reference.

**Key on behaviour instead**, in this order: **(1)** compile or run it — a
`#[test]` or a trait bound that fails to build is immune to renaming, because
the compiler follows the rename; **(2)** ask the language, not the bytes — parse
(`ast`, `syn`, `tree-sitter`) and assert on the resolved item; **(3)** search the
whole universe, not one path — assert on the *count and location set*, as
`check_mint_lease_call_sites.py` does, so a move re-reports a new location
instead of claiming a deletion; **(4)** if you truly must pin text, pin it
against the HEAD blob's content — never a symbol, a signature, a line number or
a byte offset — say which file it is expected in and *why that file*, and make
the failure message say "moved or missing", not "missing".

### 4.4 A gate is a ledger, not a ratchet

**G8.** No baseline that updates itself; no `--update-baseline` flag (none
exists in this repo — keep it that way). The permitted shape is a reviewed human
ledger, `scripts/check_integration_baseline.py`'s: every entry carries
`# owner=@handle review-by=YYYY-MM-DD`, it fails when something NEW joins **and**
when something on it starts **passing**, and it grows only by a deliberate edit.
Copy that or add nothing. And when you retire a gate, read its tests first — one
of them is probably pinning the bug.

---
