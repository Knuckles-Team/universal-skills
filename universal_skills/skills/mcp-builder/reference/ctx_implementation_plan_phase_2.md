# Context migration reference

The historical fleet-wide instrumentation plan is retired. It described a past
rollout, guessed destructive effects from tool names and used old helper APIs.

For a requested connector change, use [SDK context helpers](ctx_helpers.md) and
[connector effect requirements](connector_contracts.md#source-and-effect-contracts).
Limit edits to the selected connector and validate actual action/effect declarations.
