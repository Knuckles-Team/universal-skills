# Contract: the approval gate of a workflow skill

Provider: arbora ARBORA-IDENTITY-R019
Consumer: universal-skills US-BUSINESS-ROLES-R001.2

A workflow skill requests an approval before a gated step. It proceeds only after a grant.

## Wire shape

- Request: the gate kind (`legal_filing`, `money`, `publish`, `production`), the subject record and a summary for the approver.
- Response: `granted`, `denied` or `pending`.

## Refusal codes

- `denied` ends the run with no gated step done. `pending` leaves the run waiting.

## Authoritative types

- The approval operations that `ARBORA-IDENTITY-R019` serves.
