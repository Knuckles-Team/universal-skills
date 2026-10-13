# OpenAPI readiness and provider evidence

The generated checker reports `ready: true` only for its stated scope: exact source
and contract agreement, authorization evidence, and budgeted native schema
disclosure. This is not release, credential, transport, or live-service acceptance.
Use `--inspect` to inspect incomplete evidence while keeping `ready: false`.
The CLI writes its JSON diagnostic receipt to stderr, keeping the package's
stdio MCP channel clear. Redirect stderr to save the receipt.

## Explicit model-facing budgets

There is no default client limit. Supply a JSON object with exactly these fields:

| Field | Required value |
|---|---|
| `version` | Integer `1` |
| `client` | Nonempty target client/profile name |
| `discovery` | `eager` or `regex-search` |
| `max_input_schema_bytes` | Positive integer |
| `max_output_schema_bytes` | Positive integer |
| `max_tool_bytes` | Positive integer |
| `max_listing_bytes` | Positive integer |
| `max_search_result_bytes` | Positive integer |

Choose limits from the intended client's supported budget, not from the generated
catalog's size. No fixture limit certifies a production client. Measurements use
canonical compact UTF-8 JSON after FastMCP's bounded reference expansion. Receipts
report each input/output schema size, complete tool size/hash, initial listing and
each exact search response. These are schema payload bytes, not token estimates or
JSON-RPC envelope sizes; reserve the client's remaining context separately.

Set `PACKAGE_ENV_MCP_CLIENT_BUDGET` to this JSON file in the normal server
configuration, substituting the generated package's uppercase environment prefix.
Then use the same file for admission:

```sh
python -m package_module.parity.check_openapi_parity source.json package_module --native --client-budget client-budget.json
```

The checker builds the ordinary server and rejects readiness unless its active
budget equals the supplied budget. An inspection-only transform cannot certify
an unconfigured runtime. A configured server refuses policy replacement.

`regex-search` reuses FastMCP `RegexSearchTransform`. Initial discovery exposes
`search_tools` and `call_tool`; search returns at most one complete schema per call.
Every generated domain is retrieved by exact name and compared against its full
contract during admission. Direct tools and the proxy keep the original native
registration, validation, authorization and confirmation path. The underlying
catalog is not reduced. Search uses FastMCP's authorized catalog. Extra project
tools are also subject to runtime disclosure limits; their semantic completeness
requires the project's separate tests.

An oversized input schema, output schema, complete tool, listing or search response
fails explicitly. No text truncation, constraint removal or permissive substitute
schema is used. A single domain larger than the target budget remains blocked;
choose a reviewed smaller tool boundary or a client able to accept it. `eager`
checks the entire normal listing under the same limits.

## Narrow provider evidence interface

Keep original OpenAPI bytes immutable. Both conversion and verification accept:

```sh
python scripts/openapi_converter.py source.json package_module --provider-overlay provider-evidence.json --expected-overlay-sha256 REVIEWED_DIGEST --evidence-root pinned-provider-source
```

The generated checker and `scripts/verify_api_integration.py` accept these same
three options. Verification requires the original overlay and evidence again;
a saved contract receipt alone does not establish authorization. The expected
overlay digest comes from independent review, not a field that approves itself.

Version 1 overlay fields are `version`, `raw_source_sha256`,
`effective_source_sha256`, `evidence_files`, `corrections` and
`authorization_classifications`. The executable contract and failure examples
are in `scripts/openapi_provider_overlay.py`, `scripts/openapi_provider_evidence.py`
and `tests/test_mcp_builder_provider_overlay.py` in the builder repository.

Only two narrowly defined evidence forms are supported:

- `require-property` adds one existing object property to a component's `required`
  list, with exact before/after component hashes and source evidence. It cannot
  remove constraints, edit routes or alter operation/security objects.
- `explicit-public-decorator` classifies an operation with absent source/root
  security from a pinned provider declaration. It binds operation ID, method,
  path and operation hash, plus nonempty category, preconditions and source
  evidence. Preconditions remain visible in the receipt. It does not synthesize
  `security: []`, grant credentials or bypass provider authorization.

Evidence binds source commit, file SHA-256, optional Git blob identity and line
bounds. Paths must be relative regular files under the supplied root; symlinks,
traversal, duplicate fields, missing evidence, hash drift and unsupported changes
fail closed. Evidence reads use POSIX no-follow descriptors; unsupported platforms
fail rather than claiming verification. Files are bounded to 16 MiB each.

Component/operation hashes use sorted compact JSON with ASCII escapes. Effective
source hashes use sorted JSON with two-space indentation, ASCII escapes and a
trailing newline, encoded as UTF-8. Raw hashes always cover original bytes.
The inventory retains raw operation/security metadata alongside the verified
correction/classification receipt. Unknown operations not classified remain
blocked for readiness. Broader source repairs need a separately reviewed adapter;
this interface does not admit arbitrary patches or generalized authentication
inference.

The Python `verify_contract` and `verify_transport` APIs accept `source_bytes`,
`overlay_bytes`, `expected_overlay_sha256` and `evidence_root` as applicable.
`verify_transport` already receives source bytes as its first argument. Keep the
actual client, schema checks and native confirmation enabled in mocked probes.
