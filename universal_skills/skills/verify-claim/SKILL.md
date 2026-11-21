---
name: verify-claim
description: >-
  Machine-check a statement and record the proof receipt as evidence on its
  claim. An agent proposes a formal statement, the lean-mcp connector checks it,
  and the receipt is recorded in the knowledge engine. Use when a claim must be
  proven rather than argued, when a theorem needs a checker verdict, or when a
  claim's standing depends on a machine-checked proof.
license: MIT
metadata:
  domain: research
  skill_type: skill
  tags: [verification, lean, proof, claims, evidence, arbora]
---

# Verify a claim

A claim is proven only when a checker accepted a formal statement of it. This skill runs that loop through the arbora door. The agent never edits a receipt and never decides standing: the engine does.

## Procedure

1. Propose the claim. Call `write` with the engine claim operation `Propose` and the claim id. Preview first, then resubmit with the `plan_ref`.
2. Write the formal statement as a Lean declaration in a project under the connector's workspace root. Keep it small and name the declaration.
3. Check it. Call `act` with `fleet.call`, server `lean-mcp`, tool `lean_check`, with `project_dir`, `file` and `declaration`.
4. Read the receipt: `checker_id`, `toolchain_version`, `declaration`, `artifact_digest`, `axioms`, `has_sorry` and `verdict`. A refusal such as `TOOLCHAIN_MISMATCH` or `CHECK_TIMEOUT` returns no receipt: report the code and stop.
5. Record the receipt unchanged. Call `write` with the engine claim operation `RecordEvidence`, channel `process`, `supports` true, and the receipt in the `proof` field. Preview first, then resubmit with the `plan_ref`.
6. Link the declaration to the claim. Write the `formalizes` edge from the declaration to the claim.
7. Read the standing. Call `ask` with the engine claim operation `Get`, or the query for machine-checked claims. Report `proven` or `unproven` with the axioms.

## Rules

- A receipt with `has_sorry` true or verdict `fail` is recorded as it is and never reported as proven.
- Report an axiom outside `propext`, `Classical.choice` and `Quot.sound` as nonstandard.
- Discover the exact operation ids with `find` before concluding that one is missing.
- A statement the agent cannot formalize stays a claim. Say so; do not weaken the statement to make it check.
