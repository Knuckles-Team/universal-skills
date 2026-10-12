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

## Publish the local scaffold

The installed `mcp-builder` skill owns the canonical scaffold, scripts and assets.
Generate the destination package directly with its intended name; no GitHub
repository is used as a template and no substitution pass is needed.

Run from this skill directory:

```bash
python3 scripts/scaffold_package.py example-api --type api_client,mcp --generation-date 2026-10-12 --output-dir /path/to/output
python3 scripts/github_publish.py manifest /path/to/output/example-api > /path/to/evidence/files.json
```

`manifest` inventories every authored file, including hidden files and binary
assets, using SHA-256 and Git executable mode (`100644` or `100755`). It does not
mark any checks as passed. Generated readiness and documentation hash manifests
come from the local scaffold; refresh them with the generated project's helpers
after intentional edits, then validate that final tree. Fixed generation inputs
and date produce deterministic bytes and modes.

After the project's required checks actually pass, record their evidence outside
the source tree. The publication checks JSON must contain `passed: true` and
`files` equal to the complete validated manifest, together with the actual check
commands/results. The publisher verifies the bound snapshot but does not run or
certify those checks itself. Do not place the checks record inside the tree it
attests.

When repository creation and publication are authorized:

```bash
python3 scripts/github_publish.py publish /path/to/output/example-api --owner Example --name example-api --expected-login Operator --checks /path/to/evidence/checks.json
```

The publisher uses the existing `gh` credential context, verifies the explicit
expected login, and refuses existing destinations. It creates a normal private
repository under the selected organization or authenticated user's account,
then uploads one captured local tree. There is no remote template lookup,
GitHub template-generation call, or legacy-template wrapper. Account names and
credentials are not embedded in the skill. Credentials are never read or
serialized by the helper.

Source symlinks, `.env` and transient log/bytecode files are refused; Git metadata,
virtual environments and known caches are excluded. The initialized README and
all subsequent blobs come from the same checked snapshot even if local files
change during upload. Complete remote blob identities and executable modes are
verified before advancing the branch without force. The reported commit and
manifest bind the result; the branch is checked again after publication, but
GitHub does not make this sequence atomic against later concurrent changes.

Failed or uncertain API writes are not retried or deleted automatically. Inspect
the resulting repository state before deciding how to recover. The helper does
not modify existing repositories, merge PRs, publish packages, configure Pages,
alter live services or provision credentials. Generated specification artifacts
describe requirements; they are not proof those requirements were implemented.

The API contracts are GitHub's [normal repository creation](https://docs.github.com/en/rest/repos/repos#create-an-organization-repository),
[repository initialization](https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents)
and [Git tree publication](https://docs.github.com/en/rest/git/trees#create-a-tree).
