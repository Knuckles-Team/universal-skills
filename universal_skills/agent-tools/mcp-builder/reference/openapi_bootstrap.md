# OpenAPI connector generation

`openapi_converter.py` compiles OpenAPI 3 into operation-bound SDK clients and
one condensed MCP tool for each domain. The first non-Deprecated tag determines
the domain; absent tags use the first path segment. Names, paths and methods are
sorted. Duplicate operation identifiers and normalized domain collisions fail.

```bash
python scripts/openapi_converter.py provider-openapi.json package_name --auth-scheme api_key
```

The output includes `openapi_contract.json`, `openapi_runtime.py`, an explicit
registrar for every domain, and `auth.py` with a public client factory even when
no authentication scheme is selected. Package metadata declares
the contract as package data and the JSON Schema and Unicode regex validators as
dependencies. Request and response schemas retain source constraints, local
references, nullability and declared methods including PATCH. File inputs are
base64 bytes; filesystem paths are never opened. The converter requires a fixed
path-only server URL, JSON/form/multipart request content and standard path,
query and header parameter styles. Unsupported features fail during compilation.

Tools accept an action enum bound to an exact method and route. They do not
accept arbitrary URLs or methods. Credential references use SDK API-key or
bearer auth, and operator TLS policy is preserved. The provider base URL is its
origin, without the OpenAPI path prefix. Writes default to disabled and require
operator enablement plus native MCP confirmation. HTTP requests have finite
bounds and exactly one attempt, including PUT and DELETE. Transport uncertainty
never triggers an automatic write retry.

HTTP to a non-loopback provider is refused by default. An operator may set the
connector's `PACKAGE_ENV_ALLOW_PLAINTEXT=true` for its configured provider origin;
this uses the SDK's `HttpClientOptions.allow_plaintext` control. HTTPS certificate
and hostname verification remain enabled. Requests cannot change origin and
redirects are refused, including HTTPS-to-HTTP redirects. No credentials are
forwarded to a redirect target.

## Private GitHub template bootstrap

`github_template.py` uses the existing `gh` credential context and verifies the
actor before a write. It refuses existing destination repositories. It never
reads or serializes credential values. Both template and generated repositories
are created private. Generation calls the GitHub template `/generate` API and
checks the reviewed template head before and after the call.

Preparation is deterministic and local:

```bash
python scripts/github_template.py render template-source rendered-project --variables variables.json
```

The variable file is an explicit map of literal source strings to target strings.
Replacement occurs once, simultaneously, in canonical paths and UTF-8 content,
including hidden files. Non-text files and Git executable modes are preserved.
Symlinks, path aliases, traversal, collisions and transient files are rejected
before rendering starts. A normalized comparison must enumerate every allowed domain-code
or README edit; `verify` reports every unexpected changed, added or removed file.

Publication requires a JSON checks record containing `passed: true` and `files`
equal to the complete validated template manifest, mapping each path to its
`sha256` and Git `mode` (`100644` or `100755`). That record is
evidence supplied by the caller after normal tests, hooks and built-site checks;
the bootstrap does not run or certify those checks itself.

```bash
python scripts/github_template.py publish-template template-source --owner Example --name mcp-connector-template --checks checks.json
python scripts/github_template.py create --owner Example --name example-mcp --template Example/mcp-connector-template --template-sha REVIEWED_COMMIT
```

Failed or uncertain API writes are not retried or deleted automatically. Inspect
the resulting repository state before deciding how to recover. The reusable
automation does not merge PRs, publish packages, configure Pages, alter live
services or provision credentials. Generated specification artifacts describe
requirements; they are not proof those requirements have been implemented.
