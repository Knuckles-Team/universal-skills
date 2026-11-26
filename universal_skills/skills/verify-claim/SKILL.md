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

## Steps

1. Propose the claim. Call `write` with the engine claim operation `Propose` and the claim id, previewing first and resubmitting with the `plan_ref` and `execute=true`. Verify that the response returns the claim id in the engine's claim record.
2. Write the formal statement as a small, named Lean declaration in a project under the connector's workspace root, for example in `Claim.lean`. Verify that `grep -n "theorem\|lemma" Claim.lean` shows the named declaration and no `sorry`.
3. Check it with `act` calling `fleet.call`, server `lean-mcp`, tool `lean_check`, arguments `project_dir`, `file` and `declaration`. Verify that the result carries a receipt with `checker_id`, `toolchain_version`, `declaration`, `artifact_digest`, `axioms`, `has_sorry` and `verdict`. A refusal such as `TOOLCHAIN_MISMATCH` or `CHECK_TIMEOUT` returns no receipt, so report the code and stop.
4. Record the receipt unchanged with `write` and the engine claim operation `RecordEvidence`, channel `process`, `supports` true, receipt in the `proof` field, preview first. Verify that the returned evidence entry holds the same `artifact_digest` as the receipt.
5. Link the declaration with `write` of the `formalizes` edge from the declaration to the claim. Verify that `ask` on the claim shows the `formalizes` edge.
6. Read the standing with `ask` and the engine claim operation `Get`. Verify that the reported standing is `proven` or `unproven` and that the axioms are listed.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `TOOLCHAIN_MISMATCH` refusal | The project pins a Lean toolchain the connector does not have | Align the `lean-toolchain` file in the project with the connector's toolchain version, then call `lean_check` again with the same arguments. |
| `CHECK_TIMEOUT` refusal | The declaration is too heavy for the checker budget | Split the statement into smaller lemmas in `Claim.lean` and check the named final declaration. |
| `has_sorry` is true | A proof step was left as `sorry` | Record the receipt as is, report the claim as unproven, and replace every `sorry` before re-checking. |
| Operation id not found | The engine claim operation name differs in this deployment | Call `find` with `intent="claim propose"` to read the exact operation id and use it. |

## Rules

- A receipt with `has_sorry` true or verdict `fail` is recorded as it is and never reported as proven.
- Report an axiom outside `propext`, `Classical.choice` and `Quot.sound` as nonstandard.
- Discover the exact operation ids with `find` before concluding that one is missing.
- A statement the agent cannot formalize stays a claim. Say so; do not weaken the statement to make it check.
