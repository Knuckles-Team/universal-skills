# Profile templates (mcp-client-onboarder)

Each profile generates one or more Eunomia allow-rules for `agent:<client_id>`,
merged into the multiplexer's embedded policy (`eunomia_policy.json`) under a
`default_effect: deny` base. Resolution order: **deny by default → `_base`
(meta-tools for everyone) → the client's profile rules**. The `_base` rule is
never overwritten by onboarding.

| Profile | Rule(s) generated | Effect |
|---|---|---|
| `full-access` | one rule, no resource conditions | list + execute every tool |
| `read-only` | one rule, action `list` only | discover everything, execute nothing (real tools) |
| `server-scoped` | one rule per `--servers` entry, `attributes.name startswith <prefix>__` | list + execute only those servers' tools |
| `role-based` | server-scoped for the servers in `roles.json[<role>]` | list + execute the role's servers' tools |

The JSON files here are **reference shapes** (`{{CLIENT}}`/`{{PREFIX}}`
placeholders); `policy_rules.build_rules()` is the source of truth that emits the
concrete rules.
