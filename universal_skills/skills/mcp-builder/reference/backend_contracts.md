# API and CLI backend contracts

A connector has one backend: an HTTP API (REST or GraphQL; GraphQL uses the SDK
`graphql` extra). The `Api` class in `<pkg>/api_client.py` has one method per
operation and the SDK serves one tool per method. A local command line is not a
connector backend: wrap the command in the system's own API or build it as an
SDK source adapter. There is no `agent` type: connectors are MCP-only.

The generator `scripts/scaffold_connector.py` is the only scaffold; follow
[connector contracts](connector_contracts.md) and write no parallel example
clients with different authentication, error or registration behavior.

## API evidence and coverage

Record the target API version and the revision or digest of its OpenAPI schema,
GraphQL schema, or official documentation. Inventory operations with their method,
path or operation name, authentication requirements, request/response schemas,
pagination and effects. Map requested operations to client methods, MCP tools and
proving tests. Report unsupported or unverified operations explicitly. A starter
health call is not proof of complete API coverage; expand to the whole API when
that is the requested scope. Add GraphQL only when requested and supported by the
target rather than assuming every REST endpoint has a GraphQL equivalent.

Keep service operations in domain modules under `api/`, with public clients
exported from `api/__init__.py`. Validate request bodies and parameters with typed
models; preserve upstream field aliases, distinguish omitted values from explicit
nulls, and keep path identifiers out of query dictionaries. Validate response
shapes, including list envelopes and GraphQL errors, before producing tool output.
Avoid guessed endpoint paths or example models represented as verified contracts.

## API transport, authentication and pagination

Use the SDK HTTP client, TLS profile and credential-reference APIs already used by
the generated transport. Preserve established upstream configuration names where
integration compatibility requires them, mapping through one explicit configuration
boundary. Never replace credential references with literal secrets in templates,
logs, manifests or committed environment files. The generated `.env.example` is
configuration documentation, not a grant to create credentials or call a service.

Keep imports, client construction for discovery, and schema generation free of
vendor calls. Resolve service clients lazily; do not probe `/auth/test` or fetch a
GraphQL schema during import or construction. Retain TLS verification, origin and
redirect controls, request deadlines and response byte limits. Shared SDK
contracts govern delegated authentication and caller identity.

Use the service's actual cursor, page or offset contract. Bound page size, total
items and total requests; terminate at end-of-page evidence and reject repeated
cursors or links outside the allowed origin. Expose continuation metadata instead
of silently fetching an unbounded collection. Retries need finite budgets and
must respect cancellation and rate-limit metadata. Retry writes only when their
idempotency contract and authorization permit it.

Keep failure classification explicit: malformed input, missing authentication,
authorization denial, absence, rate limiting, transport failure and malformed
upstream output are different outcomes. Reuse the generated error authority;
redact credentials and response details before persistence or tool output. GraphQL
can return errors with HTTP 200; reject partial results unless the tool's documented
contract explicitly permits and marks them. Do not log raw request models or
exception strings that can contain secrets.

## CLI execution boundary

A CLI backend uses its own adapter and typed operation mapping. It requires no
HTTP URL or API credentials merely to construct or serve its MCP package. Report
missing executables or unsupported versions when invoking the affected operation;
do not install software, authenticate a service, or run a probe on import.

Resolve an approved executable from configuration and map each allowed operation
to a fixed argument vector. Pass arguments as a list to an execution API without
a shell. User text must never become a command string, executable name, shell
fragment or free-form option list. Validate option values and use an end-of-options
separator where the specific command supports it; list arguments alone do not
prevent option injection. Restrict working directories and environment variables
to those required by the operation. Keep secrets out of argv and sanitize stdout,
stderr and failure details before exposing them.

Bound execution time and captured output, handle cancellation, and terminate and
reap spawned processes on failure. `capture_output=True` alone does not bound
memory use. The generated MCP tool passes AnyIO's cooperative `check_cancelled`
through the SDK worker boundary. The runner checks it at most every 50 ms during
pipe and exit waits, kills the process group, reaps the direct child, and closes
pipes before propagating cancellation. A thread offload alone is insufficient.
Check exit status and validate structured output; do not represent a
nonzero exit or truncated response as successful empty data. Do not automatically
retry commands that may have effects. SDK registration, confirmation, authorization
and effect contracts apply to command-backed operations as they do to HTTP writes.

## Verification without live dependencies

For an API integration, use recorded schema fixtures and mock transports to cover
parameter and response validation, authentication boundaries, pagination ending
and looping, rate limits, redirects, oversized output, malformed JSON and GraphQL
partial errors. Keep optional native dependencies lazy and outside the wheel-build
closure. Installed-package imports and MCP discovery must work without a live
vendor service.

For a CLI integration, inject a fake runner or use a small local fixture executable
to prove literal argument handling, rejected options, timeout, cancellation,
nonzero exit, output limits, missing executable and malformed output. Assert that
imports and MCP discovery execute no command and need no HTTP configuration.

For both backends, verify generated metadata and wheel/sdist contents, actual MCP
entrypoint imports, tool schemas and declared package content. Exercise every
supported type combination and fail invalid selections before creating files.
Use the shared quality gates and record which checks ran; scaffolding or successful
mock tests do not establish release, delivery or live-service approval.
