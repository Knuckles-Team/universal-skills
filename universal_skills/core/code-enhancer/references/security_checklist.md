# Security Analysis Checklist

Reference material for the code-enhancer security analysis domain.

## CWE Top-25 (Python-Relevant Subset)

| CWE ID | Name | Python Indicators |
|--------|------|-------------------|
| CWE-78 | OS Command Injection | `os.system()`, `subprocess.call()` with shell=True |
| CWE-79 | Cross-site Scripting | Template rendering without escaping |
| CWE-89 | SQL Injection | String formatting in SQL queries |
| CWE-94 | Code Injection | `eval()`, `exec()`, `compile()` |
| CWE-200 | Exposure of Sensitive Info | Error messages with stack traces in production |
| CWE-276 | Incorrect Default Permissions | `os.chmod(0o777)`, world-readable files |
| CWE-327 | Broken Crypto | `hashlib.md5()`, `hashlib.sha1()` for security |
| CWE-400 | Uncontrolled Resource Consumption | No timeouts on network calls |
| CWE-502 | Deserialization of Untrusted Data | `pickle.loads()`, `yaml.load()` without Loader |
| CWE-676 | Use of Potentially Dangerous Function | `__import__()`, `globals()` manipulation |
| CWE-703 | Improper Check for Error Conditions | Bare `except:` or `except Exception: pass` |
| CWE-798 | Hardcoded Credentials | Passwords/tokens as string literals |

## STRIDE Threat Model

| Threat | Description | Python Check |
|--------|-------------|--------------|
| **S**poofing | Identity impersonation | Auth token validation, session management |
| **T**ampering | Data modification | Input validation, HMAC verification |
| **R**epudiation | Deniability of actions | Logging, audit trails |
| **I**nformation Disclosure | Data leaks | Error handling, debug mode checks |
| **D**enial of Service | Availability attacks | Rate limiting, resource caps, timeouts |
| **E**levation of Privilege | Unauthorized access | RBAC checks, principle of least privilege |

## OWASP Top-10 Python Checklist

1. **Broken Access Control** — Verify authorization on every endpoint
2. **Cryptographic Failures** — Use `secrets` module, avoid `random` for security
3. **Injection** — Parameterized queries, no string formatting for SQL/shell
4. **Insecure Design** — Threat model before implementation
5. **Security Misconfiguration** — No debug mode in production, secure defaults
6. **Vulnerable Components** — Run `pip-audit`, check CVE databases
7. **Auth Failures** — Strong password policies, MFA, session timeouts
8. **Data Integrity Failures** — Verify package integrity, sign releases
9. **Logging Failures** — Log security events, protect log files
10. **SSRF** — Validate URLs, restrict outbound requests

## Bandit Rule Categories

| Category | Rules | Skip Recommendation |
|----------|-------|---------------------|
| Assert usage | B101 | Skip in test files |
| Subprocess | B404, B603, B607 | Review case-by-case |
| Hardcoded passwords | B105, B106, B107 | Always flag |
| SSL/TLS | B501, B503 | Always flag |
| Pickle | B301, B302 | Always flag |
| YAML | B506 | Flag if using `yaml.load()` without SafeLoader |

## Production Resilience (Release It! + DDIA)

Checks derived from *Release It!* (Nygard) and *Designing Data-Intensive
Applications* (Kleppmann):

### Timeout Coverage

| Library | Check | Action |
|---------|-------|--------|
| `requests` | `timeout=` parameter present | Flag calls without explicit timeout |
| `httpx` | `timeout=` parameter present | Flag calls without explicit timeout |
| `aiohttp` | `timeout=` in session/request | Flag calls without explicit timeout |
| `urllib3` | `timeout` parameter | Flag calls without explicit timeout |

### Retry Safety

| Pattern | Check | Risk |
|---------|-------|------|
| Unbounded retry | `while True` retry without max | Retry storm |
| No backoff | Retry without delay/jitter | Thundering herd |
| Non-idempotent retry | POST/PUT retried without safety | Data corruption |
| Missing `tenacity`/`backoff` | No structured retry library | Ad-hoc retry logic |

### Circuit Breaker & Bulkhead

| Pattern | Detection | Note |
|---------|-----------|------|
| `pybreaker` usage | Import detection | Standard circuit breaker |
| Custom circuit breaker | State machine pattern | Manual implementation |
| Bulkhead isolation | Thread pool / semaphore limits | Resource isolation |
| Rate limiting | `ratelimit` / token bucket | Overload protection |

### Consistency Boundaries (DDIA)

| Check | What It Detects |
|-------|----------------|
| Multi-aggregate writes | Transaction spanning multiple roots |
| Missing idempotency keys | Retry-sensitive endpoints without dedup |
| Undocumented staleness | Cache/view reads without freshness annotation |
