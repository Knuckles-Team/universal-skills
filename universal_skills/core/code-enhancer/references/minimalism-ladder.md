# Minimalism Ladder — the lazy-first discipline (CE-040)

> The best code is the code never written. *Lazy means efficient, not careless.*

This is the generation/refactor counterpart to `scripts/analyze_minimalism.py`
(which audits a repo for over-engineering). It tells the agent **how to write less
code in the first place**, and how to mark the shortcuts it does take.

Distilled from the ponytail skill by Dietrich Gebert
(<https://github.com/DietrichGebert/ponytail>, MIT) and adapted for code-enhancer.

## The ladder — stop at the first rung that holds

Before writing any code, walk these in order and stop as soon as one applies:

1. **Does this need to exist at all?** (YAGNI) — the cheapest code is none.
2. **Does the standard library already do this?** Use it.
3. **Does a native platform feature cover it?** (e.g. `<input type="date">`,
   a DB unique constraint, an HTTP cache header.) Use it.
4. **Does an already-installed dependency solve it?** Use it — don't add a new one.
5. **Can this be one line?** Make it one line.
6. **Only then** write the minimum code that works.

## Rules

- No abstraction that wasn't explicitly requested (no interface with one
  implementation, no factory with one product, no config nobody sets).
- No new dependency if it can be avoided. Boring over clever. Fewest files possible.
- **Deletion over addition.** When two stdlib approaches are the same size, pick the
  edge-case-correct one — lazy means less code, not the flimsier algorithm.
- Question complex requests: "Do you actually need X, or does Y cover it?"

## Mark intentional shortcuts

When you *do* take a shortcut with a known ceiling (a global lock, an O(n²) scan, a
naive heuristic, a hardcoded limit), leave a marker comment that names **both the
ceiling and the upgrade path**, so the decision is auditable and the migration route
lives in the code instead of someone's memory:

```python
# ponytail: global lock; switch to per-account locks if write throughput matters
# upgrade-path: linear scan is fine < ~1k rows; index on (org_id, ts) when it grows
```

`analyze_minimalism.py` counts these markers (`ponytail:` / `upgrade-path:`) so a
reviewer can tell a deliberate simplification from an accidental one.

## Not lazy about

Input validation at trust boundaries, error handling that prevents data loss,
security, accessibility, and anything explicitly requested. Non-trivial logic leaves
**one** runnable check behind — the smallest thing that fails if the logic breaks
(an assert-based self-check or one small test; no frameworks). Trivial one-liners
need no test.
