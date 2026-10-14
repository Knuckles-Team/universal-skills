# OpenAPI connector generation

`openapi_converter.py` compiles OpenAPI 3 into operation-bound SDK clients and
one condensed MCP tool for each domain. Named registrar callables preserve the
SDK domain toggles without duplicating registrar bodies. The first non-Deprecated tag determines
the domain; absent tags use the first path segment. Names, paths and methods are
sorted. Duplicate operation identifiers and normalized domain collisions fail.

```bash
python scripts/openapi_converter.py provider-openapi.json package_name --auth-scheme api_key
```

The output includes `openapi_contract.json`, the runtime/request/response modules, named SDK
registrars for every domain, `ApiClientSystem(OpenApiClient)`, and `auth.py` with a public client factory even when
no authentication scheme is selected. `openapi_auth_scheme.py` represents selected
header or bearer authentication explicitly; `auth.py` resolves references through the SDK.
Package metadata declares
the contract as package data and the JSON Schema and Unicode regex validators as
dependencies. Request and response schemas retain source constraints, local
references, nullability and declared methods including PATCH. File inputs are
base64 bytes; filesystem paths are never opened. The converter requires a fixed
path-only server URL, JSON/form/multipart request content and standard path,
query and header parameter styles. Unsupported features fail during compilation.
Multiple request media types are rejected until a representation-complete adapter
can validate and exercise each one; selecting only the first is not full parity.

Tools accept an action enum bound to an exact method and route. They do not
accept arbitrary URLs or methods. Credential references use SDK API-key or
bearer auth, and operator TLS policy is preserved. The provider base URL is its
origin, without the OpenAPI path prefix. Writes default to disabled and require
operator enablement plus native MCP confirmation. HTTP requests have finite
bounds and exactly one attempt, including PUT and DELETE. Transport uncertainty
never triggers an automatic write retry.

The SDK confirmation helper must accept `confirmation_arguments=arguments` and
return either a boolean or `mcp.types.InputRequiredResult`. The tool returns a
pending input request immediately and dispatches only for exact `True`.
An older SDK without that interface fails closed on writes; it is not evidence of
modern protocol compatibility. Test actual native acceptance, denial and pending
round trips with the reviewed SDK before admitting write operations.

HTTP to a non-loopback provider, and credential-bearing HTTP even on loopback,
is refused by default. An operator may set the
connector's `PACKAGE_ENV_ALLOW_PLAINTEXT=true` for its configured provider origin;
this uses the SDK's `HttpClientOptions.allow_plaintext` control. HTTPS certificate
and hostname verification remain enabled. Requests cannot change origin and
redirects are refused, including HTTPS-to-HTTP redirects. No credentials are
forwarded to a redirect target.

## Signed session headers

A provider's signed session is a header credential when its authoritative contract
declares it that way. For example, ArtCraft's user session manager accepts the
signed value in the `session` header, distinct from its Omni API bearer key:

```json
{"components":{"securitySchemes":{"signed_session":{"type":"apiKey","in":"header","name":"session"}}}}
```

This fragment documents authentication only; it is not an exported provider API.
Bind only reviewed session-protected operations with
`"security": [{"signed_session": []}]`, select `--auth-scheme signed_session`, and
configure `PACKAGE_ENV_TOKEN_REF` with a credential reference. A bearer key cannot
satisfy this scheme. Unknown schemes and transport-control header names are
rejected. Declared credential headers cannot be supplied as tool parameters,
including for public operations. Do not infer authentication from route names or
create a credential as part of generation.

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

When public repository creation and publication are authorized, Pages is included
by default:

```bash
python3 scripts/github_publish.py publish /path/to/output/example-api --owner Example --name example-api --expected-login Operator --checks /path/to/evidence/checks.json --visibility public
```

The publisher uses the existing `gh` credential context, verifies the explicit
expected login, and refuses existing destinations. It creates a normal repository
with the requested visibility under the selected organization or authenticated user's account,
then uploads one captured local tree. There is no remote template lookup,
GitHub template-generation call, or legacy-template wrapper. Account names and
credentials are not embedded in the skill. Credentials are never read or
serialized by the helper. Omitting `--visibility` retains the private default;
private publication does not enable or dispatch Pages. Never infer permission to
make a repository public from a request to generate documentation.

Source symlinks, `.env` and transient log/bytecode files are refused; Git metadata,
virtual environments and known caches are excluded. The initialized README and
all subsequent blobs come from the same checked snapshot even if local files
change during upload. The original default branch and root initialization commit
are bound before upload; publication refuses intervening commits or branch changes
and never adopts them as its parent. Complete remote blob identities and executable modes are
verified before advancing the branch without force. The reported commit and
manifest bind the result. Stable repository ID, owner/name, requested visibility and
non-template status are rechecked before upload and at final attestation. The
branch is checked again after publication, but
GitHub does not make this sequence atomic against later concurrent changes.

Failed or uncertain API writes are not retried or deleted automatically. Inspect
the resulting repository state before deciding how to recover. Repository creation
never overwrites an existing repository. The helper does not merge PRs, publish
packages, alter provider services or provision credentials. Generated specification artifacts
describe requirements; they are not proof those requirements were implemented.

The API contracts are GitHub's [normal repository creation](https://docs.github.com/en/rest/repos/repos#create-an-organization-repository),
[repository initialization](https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents)
and [Git tree publication](https://docs.github.com/en/rest/git/trees#create-a-tree).

### Documentation delivery

Public publication requires the checked `.github/workflows/pages.yml`,
`mkdocs.yml` and `docs/index.md`. After attesting the complete remote tree, the
publisher configures Pages with `build_type: workflow`, reads the site back, and
requests one run of the existing active `pages.yml` workflow. It checks the
repository ID, name, public non-template status, default branch and expected head
before each write phase. An existing Actions site is reused, including its custom
domain. A legacy or private site is preserved and reported as a conflict; the
helper never changes visibility, domains, TLS settings or runner permissions.

Existing credentials must already permit repository creation, Pages configuration
and workflow dispatch. The relevant API permissions are documented in GitHub's
[Pages creation endpoint](https://docs.github.com/en/rest/pages/pages#create-a-github-pages-site)
and [workflow dispatch endpoint](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event).
Missing permissions are reported; the helper does not acquire broader access.

The receipt records `configured`, `dispatch_requested` and
`deployment_verified: false`. An accepted dispatch is not deployment evidence.
Inspect the resulting Pages run, verify its actual `head_sha` against the published
commit, require successful deployment, then check the returned HTTPS URL and the
expected documentation/readiness assets anonymously. GitHub dispatches a branch
reference, so a concurrent branch advance can change the run's source after the
helper's last check. Record the run URL, revision and live HTTP results separately.

If GitHub has not indexed the new workflow yet, or a Pages call fails, retain the
published repository and inspect its state and existing workflow runs. Do not
repeat repository creation or blindly retry a failed write. For an already
reviewed public repository, the same provisioning operation is available directly:

```bash
python3 scripts/github_publish.py pages --owner Example --name example-api --expected-login Operator --repository-id 123456 --expected-head <reviewed-commit-sha>
```

Supply the repository ID and full expected commit SHA from the reviewed
publication. This command binds to the current default branch and refuses identity,
visibility or head drift. Invoke it only when a build is intended: it requests one
new workflow run even when the site is already configured. Neither command changes
an existing repository's visibility or enables a disabled workflow.

The client constructor uses `write_mode="read-only"` by default; the explicit
`"read-write"` mode follows the unchanged operator `PACKAGE_ENV_ALLOW_WRITES`
setting. Delegated bearer authentication uses a separate HTTPS-default OIDC
client and closes both TLS profiles and clients through the canonical SDK flow.


## Complete operation parity

Retain the entire supported operation catalog from the official pinned source.
The converter emits `openapi_inventory.json`, binding the exact source bytes and
recording every operation, method, path, effective security requirement and `x-*`
annotation. Admin, security, billed and destructive operations remain represented;
provider-specific policy must interpret their requirements explicitly. Missing
security declarations are recorded as unknown, never as evidence of public access.
The ready-state checker fails until authorization is explicit in the source or
verified through the narrow [provider evidence interface](openapi_readiness.md).
Arbitrary runtime overlays are not equivalent to the pinned source. Pure inventory/schema checks remain
separate from this authorization admission. Do not treat
an undocumented effect as read-only merely because its HTTP method is GET.
Malformed security declarations, undeclared scheme references and invalid scope
arrays fail compilation. Explicit `security: []` and anonymous alternatives remain
valid declarations; structural validity does not prove credential scope or service
authorization. OpenAPI 3.0 and 3.1 scope/role rules are validated separately.

The generated package includes these helpers: `from package_module.parity import
verify_contract, verify_mcp, require_complete_coverage, verify_transport`. No sibling
builder checkout is needed. Run the checker in the existing reviewed environment:

```sh
python -m package_module.parity.check_openapi_parity source.json package_module --native --inspect
```

It rejects missing operations, method/route/parameter/response/security drift,
incomplete domain mappings, stale inventories and missing or mismatched native
MCP schemas. Expected references use the actual bounded FastMCP dereferencer;
reference sibling assertions compile to an `allOf` intersection, so a shallow
reference merge cannot overwrite a stronger constraint. Client-unsupported schemas
(such as Unicode property escapes rejected by a Python JSON Schema client) fail
explicitly; do not drop the constraint to obtain a pass. Discovery is distinct
from successful transport execution.
Raw source methods, routes and parameter placement are checked independently of
the compiler, including against captured HTTP requests, so a consistently wrong
compiler cannot certify its own routing. The source snapshot is isolated from
compiler mutation.

For exhaustive mocked transport proof, import `verify_transport` from
`scripts/openapi_transport_parity.py`. Pass the original source bytes, generated
contract, fixtures for **every** action, `api_factory(transport, operation)` and
an async `mcp_call(tool_name, arguments, client)` adapter. Each fixture supplies
`arguments`, `response` (httpx.Response keyword arguments), full `expected_result`, and
`expected_request` (`path`, plus applicable `query`, `headers`, `json`, `form` or `body`).
Multipart fixtures supply an `assert_request(request, operation, fixture)` callback
that verifies decoded fields and files.
The factory builds the real client with the supplied MockTransport; the MCP
adapter binds that client to the actual native registered tool. Both surfaces
must issue exactly one expected request. Missing fixtures, blocked dispatch,
validation errors or MCP errors fail the check. Keep schema validation,
credential requirements and confirmation enabled; no production policy patching.

Run authorization/refusal fixtures separately. A protocol unable to complete a
required confirmation is a remaining MCP acceptance blocker, not evidence of a
successful write. Mocked coverage never certifies live endpoints. Record live
verification separately and call only operations authorized for that check.

The inventory proves completeness against its source, not that a partial source
covers an entire provider suite. Preserve the official source inventory and map
all supported APIs before claiming full-suite completion. For native MCP or CLI
products preserve their complete supported catalogs and clearly identify any
connector-owned API bridge; never invent an upstream HTTP service.

Reject source exports whose URL placeholders differ from declared `in: path` names.
Do not reinterpret whole request objects as path parameters to make compilation pass.
Binary fields retain source annotations and extensions while the runtime
representation uses base64. Raw binary length, pattern, enum and composition
constraints require a representation-aware provider adapter and fail compilation;
applying them to encoded text would change their meaning. Provider extensions such as `x-immich-required` are
preserved evidence, not generic JSON Schema `required` semantics; resolve such
source discrepancies through a reviewed provider correction before acceptance.

Native Unicode property patterns use the bundled, hash-verified Unicode 18 ranges
derived from the reviewed regex 2026.9.29 runtime. Positive L/M/N properties are
translated to literal ranges; unsupported properties fail. This pins the existing
converter semantics and does not assert equivalence with an unverified provider
Node/Unicode version. The generated parity package ships the table as package data.

Native schema validity does not establish model-context suitability. The generated
runtime supports FastMCP's built-in deferred search with explicit named byte
budgets. See [readiness and provider evidence](openapi_readiness.md) for configuration,
measured full-schema disclosure and negative oversized checks. No constraints are
truncated and all authorized tools retain their original dispatch path.
