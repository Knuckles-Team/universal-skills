# Contract — prompt-agents

Provider: scion-sdk SCION-CONNECTOR-CONTROL-R916.8
Consumer: universal-skills US-MCP-BUILDER-R011.18

## Wire shape

A prompt JSON holds `title`, `identity.role`, `identity.goal`, `instructions.core_directive` and `agent`. `agent` holds `kind` (`operator` or `business-role`), `business_role`, `tools`, `skills`, `data.reads`, `data.writes`, `guardrails.approval_required`, `guardrails.never` and `outputs`. A business-role prompt matches one `BusinessRole(name, tasks, description)` in `ROLES`.

## Refusal codes

`prompt_agent_findings(document, decl, served_tools, skills, name)` returns one finding per broken rule: a tool outside the contract steps, an unknown skill or data location, an empty `never` list, a destructive tool outside `approval_required`, or a business role with no `BusinessRole`.

## Authoritative types

[`scion_sdk/surface_contracts.py`](https://github.com/Knuckles-Team/scion-sdk/blob/main/scion_sdk/surface_contracts.py) defines `BusinessRole` and `prompt_agent_findings`.

## Test vectors

[`tests/test_mcp_builder_connector_scaffold.py`](https://github.com/Knuckles-Team/universal-skills/blob/main/tests/test_mcp_builder_connector_scaffold.py) asserts the same rules on the generated prompts.
