---
name: codebase-untangle
domain: development
skill_type: skill
description: >-
  Redesign a tangled repository so that a change lands in one place. Use when a repository resists change, when gates keep finding the same kind of problem, or when asked to refactor, untangle, simplify or restructure.
license: MIT
tags: [refactor, architecture, simplification, coupling, gates, spec-kit]
metadata:
  version: '1.6.2'
---

# Codebase untangle

Scope: Redesign a tangled repository so that a change lands in one place. A staged procedure that lists every structural problem before changing anything, redesigns from first principles with a decision log, files the redesign as spec rows, then fixes and reviews until nothing worth fixing remains. Use when a repository resists change, when gates keep finding the same kind of problem, or when asked to refactor, untangle, simplify or restructure.

Use this skill to redesign structure. For a graded audit of many domains use `code-enhancer`; for what each gate measures use `gates-and-code-placement`. This skill ends in spec rows and code, not a report.

The binding principles are in constitution Articles I, XI and XXV. This skill is the procedure that applies them.

## Done means

- Few special cases, and the count fell at every pass.
- A typical change touches one place.
- Every import points toward code that changes less, and none reaches an internal of another unit.
- Every gate named below is green on the whole tree, with no allowance added.

## Procedure

1. **Settle comments and tests first.** Ask the owner whether to prune stale comments and to rewrite brittle tests before the structural work. Tests must assert behaviour through the public surface; a test that fails on a refactor is a problem to list in step 2.
2. **List every problem and change nothing.** Write one numbered list in a scratch file outside the repository. Use these categories:
   - *Hidden links*: global state, import-time side effects, an unstated call order, a caller that reaches an internal.
   - *Needless links*: things that change for different reasons but are tied together, a dependency that points toward code that changes more, a cycle.
   - *Surplus*: dead code, unused parameters, pass-through wrappers, speculative generality, duplicates.
   - *Special cases*: a branch, flag or exception that patches one symptom instead of the cause.
   - *Custom code in environment*: a script in a deployment or environment repository that encodes behaviour instead of configuring a specified feature.
   - *Implicit lifecycles*: status held in flags, strings or nullable timestamps.
3. **Measure with our gates, read-only.** Run the census modes and attach their findings to the list: `kiss-census`, `complexity-census` (cccc), `dupehound` and `jscpd-census` for clones, the `coupling` gate for import direction, the surface audit for connectors, and `state-machine-census` for lifecycles. A gate finding is a listed problem; a problem the gates cannot see is listed by hand.
4. **Redesign from first principles.** Ask what the units should be if the code were written today: group what changes together, separate what changes for different reasons, order the layers by stability, make interfaces deep. Add a new abstraction (interface, trait, protocol, base class, port, factory, wrapper, option parameter) only when two call sites need it today; one caller gets concrete code (constitution Article XI). Write a decision log: one line per decision, each naming the problem numbers it solves. A problem with no decision is not yet solved; a decision with no problem is speculative and is dropped.
5. **File the redesign before code.** Follow the spec-kit flow: route each part to its owning repository, extend the owning spec first, add rows with a bound test and a `Shape:` sentence, then plan and tasks. A script in an environment repository becomes a feature row in the owning repository, and the script is replaced by configuration. Never write code for a part that has no row.
6. **Fix everything.** Fix each cause at the root; do not add an exemption, baseline or suppression. Delete what step 2 marked as surplus in the same change. Keep every pull request inside the repository's time and size limits, with the `Spec:` trailer in the commit.
7. **Review until clean.** Run a fresh review pass over the diff, using a reviewer that has not seen the decision log, and compare its list against the original. Re-run step 3. Repeat steps 2 to 6 on what remains. Stop when a pass finds nothing worth fixing, and report the special-case count before and after.

## Steps

1. Settle comment pruning and test rewrites with the owner before structural work.
   Run `git status --short` to confirm a clean tree. Verify that the owner's answer is recorded in the scratch list.
2. Write the numbered problem list in a scratch file outside the repository.
   Use `mktemp -d` for the location. Verify that every item carries one of the listed categories.
3. Attach the read-only gate findings.
   Run the census modes named in the Procedure (`kiss-census`, `complexity-census`, `dupehound`, `state-machine-census`). Verify that every gate finding appears as a listed problem and that no file changed.
4. Write the decision log and file spec rows before any code.
   Run `ls specs/` in the owning repository. Verify that each decision names problem numbers and each part has a row.
5. Fix each cause at the root and delete the surplus.
   Run the repository's test command after each change. Verify that the suite passes and that no exemption, baseline, or shim was added (`git diff --stat`).
6. Review with a fresh reviewer and repeat the census.
   Re-run the census modes from step 3, for example `complexity-census`. Verify that the special-case count fell and that every gate is green on the whole tree.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| A gate stays red after the fix | The cause was patched with a special case instead of fixed at the root | Revert the patch, return to the problem list, and redesign the unit so the finding disappears with no allowance |
| Decision has no matching problem | Speculative abstraction added | Delete the decision and the abstraction; keep concrete code until two call sites need it |
| Reviewer finds new problems each pass | Fixes introduced new coupling | Repeat the Procedure from step 2 on the remaining items and stop only when a pass finds nothing worth fixing |

## Do not

- Change behaviour while listing, or list while fixing.
- Treat a gate going green as proof the design is good; the done criteria decide.
- Keep a shim, alias or compatibility path for the old structure.
