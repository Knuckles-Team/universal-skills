# Industry Frameworks Reference

## CHAOSS Metrics (Community Health Analytics Open Source Software)

### Activity Metrics
- **Commit Frequency**: Commits per week/month — measures development velocity
- **Contributors**: Unique contributors per period — measures community size
- **Issues Opened/Closed**: Issue velocity — measures responsiveness
- **PR Merge Time**: Time from PR open to merge — measures review efficiency
- **Bus Factor**: Minimum contributors whose departure would stall the project

### Diversity & Inclusion
- **Contributor Demographics**: Geographic and organizational diversity
- **New Contributor Retention**: % of first-time contributors who return

## DORA Metrics (DevOps Research and Assessment)

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| Deployment Frequency | On-demand | Daily-Weekly | Weekly-Monthly | Monthly+ |
| Lead Time for Changes | < 1 hour | 1 day - 1 week | 1 week - 1 month | 1-6 months |
| Change Failure Rate | 0-15% | 16-30% | 16-30% | 46-60% |
| Time to Restore | < 1 hour | < 1 day | 1 day - 1 week | 1 week+ |

## OWASP (Open Web Application Security Project)

### Top 10 (2021)
1. A01: Broken Access Control
2. A02: Cryptographic Failures
3. A03: Injection
4. A04: Insecure Design
5. A05: Security Misconfiguration
6. A06: Vulnerable and Outdated Components
7. A07: Identification and Authentication Failures
8. A08: Software and Data Integrity Failures
9. A09: Security Logging and Monitoring Failures
10. A10: Server-Side Request Forgery (SSRF)

## 12-Factor App Methodology

1. **Codebase**: One codebase tracked in VCS, many deploys
2. **Dependencies**: Explicitly declare and isolate dependencies
3. **Config**: Store config in the environment
4. **Backing Services**: Treat backing services as attached resources
5. **Build, Release, Run**: Strictly separate build and run stages
6. **Processes**: Execute the app as stateless processes
7. **Port Binding**: Export services via port binding
8. **Concurrency**: Scale out via the process model
9. **Disposability**: Maximize robustness with fast startup and graceful shutdown
10. **Dev/Prod Parity**: Keep development, staging, and production as similar as possible
11. **Logs**: Treat logs as event streams
12. **Admin Processes**: Run admin/management tasks as one-off processes

## SemVer 2.0.0 (Semantic Versioning)

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes
- Pre-release: `1.0.0-alpha`, `1.0.0-beta.1`
- Build metadata: `1.0.0+build.123`

## SOLID Principles

| Principle | Description | Detection Signal |
|-----------|-------------|-----------------|
| **S**ingle Responsibility | A class should have one reason to change | File size, method count |
| **O**pen/Closed | Open for extension, closed for modification | Plugin/hook patterns |
| **L**iskov Substitution | Subtypes must be substitutable | Proper inheritance |
| **I**nterface Segregation | Many specific interfaces > one general | Protocol/ABC usage |
| **D**ependency Inversion | Depend on abstractions, not concretions | DI patterns, protocols |

## Clean Architecture (Robert C. Martin)

Concentric layers (inner → outer):
1. **Entities**: Enterprise business rules
2. **Use Cases**: Application business rules
3. **Interface Adapters**: Controllers, presenters, gateways
4. **Frameworks & Drivers**: Web, DB, UI, external agencies

**Dependency Rule**: Source code dependencies only point inward.

## IEEE/ISO Software Quality Standards

### ISO/IEC 25010 — Product Quality Model
- Functional Suitability
- Performance Efficiency
- Compatibility
- Usability
- Reliability
- Security
- Maintainability
- Portability

### ISO/IEC 25023 — Measurement of System and Software Quality
Provides metrics for each characteristic in ISO 25010.
