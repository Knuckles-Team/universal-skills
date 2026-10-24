# Security Standards Reference

## OWASP Top 10 Code Pattern Detection

| ID | Vulnerability | Patterns |
|----|--------------|----------|
| A01 | Broken Access Control | Missing auth, open admin routes, IDOR |
| A02 | Crypto Failures | MD5/SHA1, hardcoded keys, weak random |
| A03 | Injection | eval(), exec(), f-string SQL, shell=True |
| A05 | Security Misconfig | DEBUG=True, wildcard CORS, defaults |
| A06 | Vulnerable Components | CVEs in deps, outdated packages |
| A08 | Integrity Failures | pickle.loads, no signature verification |

## Scoring

### Positive (+points)
- SECURITY.md: +10
- Dep pinning: +5
- Security linter in CI: +10
- Input validation (Pydantic): +10
- Auth framework (JWT/OAuth): +10

### Negative (-points)
- eval()/exec(): -15
- Hardcoded secrets: -20
- subprocess shell=True: -10
- No input validation: -10
- assert for validation: -5
