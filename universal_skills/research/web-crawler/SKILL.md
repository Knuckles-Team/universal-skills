---
name: web-crawler
domain: research
skill_type: skill
description: >-
  Bounded, privacy-aware website and sitemap crawler with AgentConfig-managed
  egress, TLS, output confinement, and optional GraphOS document ingestion. Use
  when fetching one page, crawling a site or sitemap, or ingesting approved web
  content into GraphOS.
tags: [web, crawler, documentation, scrape, extract, markdown, sitemap, knowledge-graph, graph-os, ingest]
license: MIT
metadata:
  version: '1.3.0'
  author: Repository Maintainers
---
# Web Crawler Skill

`scripts/crawl.py` crawls a page, a sitemap, or a same-origin section and emits
privacy-sanitized markdown. Its default acquisition path is the shared bounded
HTTP client. Headless-browser fetching is disabled unless an operator enables
`SOURCE_HTTP_ALLOW_BROWSER_FETCH` through `AgentConfig`.

Every outbound destination is checked immediately before I/O. Seed URLs,
robots and sitemap locations, nested sitemap entries, redirects, browser
navigation results, and recursively discovered links all use the same policy.
Only HTTP(S) URLs without embedded credentials are accepted. Private or
reserved destinations are denied unless their exact hostname is configured in
`SOURCE_HTTP_ALLOWED_PRIVATE_HOSTS`; cross-host redirects and sitemap entries
require an exact `SOURCE_HTTP_ALLOWED_REDIRECT_HOSTS` entry.

## Usage

```bash
python scripts/crawl.py --urls https://docs.example.org/guide/ --strategy recursive --output-dir crawler-output
```

Strategies:

1. `single` fetches one or more individual pages.
2. `chunked` splits each page at H1/H2 boundaries.
3. `sitemap-sequential` processes bounded sitemap entries one at a time.
4. `sitemap-parallel` processes bounded sitemap entries with limited concurrency.
5. `recursive` follows validated same-origin links to the configured depth.

Auto-discovery checks bounded `robots.txt` and `sitemap.xml` responses. An
automatically discovered sitemap remains inside the seed origin unless its host
is explicitly approved. `--ignore-prefix-restriction` relaxes only the path
prefix; it never relaxes URL, DNS, private-address, or origin controls.

### Bounds

- `--max-depth`: 1–8; default 3.
- `--max-concurrent`: 1–16; default 4.
- `--max-pages`: 1–5,000; default 500.
- at most 50 seed URLs, 1,000 extracted links per page, three nested sitemap
  levels, 5,000 sitemap locations, and 512 chunks per page.
- response bodies, redirects, CAs, proxies, and private-host exceptions come
  from `AgentConfig` (`SOURCE_HTTP_MAX_RESPONSE_BYTES`,
  `SOURCE_HTTP_MAX_REDIRECTS`, and the shared TLS profile fields).
- page and MCP response/request sizes and timeouts have hard ceilings in the
  security runtime.
- one invocation emits at most 5,000 files/records and 512 MiB across disk or
  stdout, even if per-page and page-count limits would permit more.

There is no insecure command-line switch. TLS verification, system trust,
custom CA bundles, mTLS, and proxies are resolved at runtime through the shared
transport-security profile. An insecure TLS profile still requires the central
two-part explicit acknowledgement; the crawler does not create a bypass of its
own.

## Output and privacy

`--output-dir` is resolved under `WORKSPACE_PATH` when that AgentConfig field is
configured, otherwise under the agent-utilities XDG data directory. Absolute
paths are accepted only when they remain beneath one of those roots. Existing
symlink components, traversal outside the allowed roots, and symlink targets
are rejected. Files are written atomically with private permissions and opaque,
content-neutral names.

Before content crosses stdout, disk, or GraphOS persistence boundaries, the
shared persistence privacy guard redacts recognized personal identifiers,
secrets, machine-specific paths, and runtime identity terms. Logs contain only
counts and stable error categories—not URLs, endpoints, filesystem paths,
tokens, response bodies, or upstream exception text.

If `--output-dir` is omitted, sanitized content is written to stdout. Use a
confined output directory for sitemap and recursive jobs.

## Optional browser mode

Set `SOURCE_HTTP_ALLOW_BROWSER_FETCH=true` through `AgentConfig` only when a
site genuinely requires rendered JavaScript. Browser mode:

- keeps the Chromium sandbox enabled;
- preflights every top-level navigation through the bounded HTTP policy;
- validates the final navigation URL before accepting content;
- constrains Chromium DNS resolution to seed and explicitly approved hosts;
- disables iframe processing;
- uses bounded page/wait timeouts and concurrency; and
- accepts only a bounded CSS selector through `--wait-for` (arbitrary CLI
  JavaScript is rejected).

A browser necessarily has a larger subresource egress surface than the default
HTTP parser. Keep browser mode disabled for untrusted or ordinary static
content. Because Chromium cannot faithfully consume every shared transport
profile, browser mode accepts only verified system trust with no custom CA,
mTLS material, or configured proxy. Those profiles fail closed; use the default
HTTP path, which supports them natively. The fixed content-cleaning script is
packaged code, not runtime input.

## Knowledge Graph ingestion

Knowledge Graph ingestion is active when a GraphOS endpoint is supplied at
runtime through `--kg-endpoint` or `GRAPH_OS_URL`; `--no-kg-ingest` disables it.
`GRAPH_OS_TOKEN`, when needed, is runtime-only and is never logged or persisted
by this skill.

The endpoint is validated by the same SSRF policy on every request. GraphOS TLS,
CA, mTLS, and proxy settings resolve through the `graph-os` transport profile.
Redirects are rejected, JSON-RPC request/response bodies and session headers are
bounded, and malformed SSE/JSON fails closed.

The crawler calls only `document_process` with privacy-sanitized content. Its
source provenance is a stable, non-reversible reference rather than a raw URL.
The former URL-only mode was removed because it delegated a second fetch and
could persist a sensitive location outside this skill's privacy boundary.
Failure is best-effort: the first MCP failure disables further submissions for
the run while local sanitized output continues.

## Runtime policy example

The values below are deployment-neutral. Store profile catalogs and certificate
material behind secret references rather than committing paths or PEM data.

```text
SOURCE_HTTP_MAX_RESPONSE_BYTES=10485760
SOURCE_HTTP_MAX_REDIRECTS=3
SOURCE_HTTP_ALLOWED_PRIVATE_HOSTS=[]
SOURCE_HTTP_ALLOWED_REDIRECT_HOSTS=[]
SOURCE_HTTP_ALLOW_BROWSER_FETCH=false
GRAPH_OS_TLS_PROFILE=graph-os-production
TLS_PROFILES_REF=secret://runtime/tls-profiles
```

Exact private and redirect hosts may be supplied at runtime when an operator
intentionally crawls an intranet source. Do not use wildcard entries.
