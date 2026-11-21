# Contract: the business profile read

Provider: medulla and arbora (rows to file; US-BUSINESS-ROLES-R001.1 depends on them)
Consumer: universal-skills US-BUSINESS-ROLES-R001.1

A workflow skill reads one tenant profile from the knowledge graph through a served operation.

## Wire shape

- Request: the tenant and the list of field names the skill declares in `Profile inputs`.
- Response: a value, or an absence marker, for each field.

## Refusal codes

- An absent required field makes the skill stop and ask one question. It never guesses a value.

## Authoritative types

- The profile vocabulary of the engine and its served read operation, both to be named by their owners.
