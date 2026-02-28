---
name: qa-planning
description: Generate comprehensive QA test plans, manual test cases, regression test suites, and bug reports. Use when planning QA strategy for features or releases, writing test cases, building regression suites, or documenting bugs. Triggers include "test plan", "test cases", "regression suite", "bug report", "QA strategy", "write tests for", "validate the". Do NOT use for automated code-level tests — use tdd-methodology instead.
categories: [Development, Productivity]
tags: [qa, testing, test-plans, regression, bug-reports, quality-assurance]
---

# QA Test Planning

Generate structured QA artifacts: test plans, manual test cases, regression suites, and bug reports. Focuses on manual QA strategy and documentation, complementing automated testing.

---

## Quick Start

| Request | Output |
|---------|--------|
| "Create a test plan for {feature}" | Complete test plan document |
| "Generate test cases for {feature}" | Step-by-step test cases |
| "Build a smoke test suite" | Critical path tests, prioritized |
| "Document bug: {description}" | Structured bug report |

---

## Workflow

```
1. ANALYZE
   → Parse feature/requirements
   → Identify test types needed
   → Determine scope and priorities

2. GENERATE
   → Create structured deliverables
   → Apply templates and best practices
   → Include edge cases and negative tests

3. VALIDATE
   → Check completeness
   → Verify traceability to requirements
   → Ensure actionable, reproducible steps
```

---

## Test Plan Template

```markdown
# Test Plan: [Feature/Release Name]

## Objective
[What are we testing and why]

## Scope
**In Scope:** [Features, test types, platforms]
**Out of Scope:** [Exclusions and known limitations]

## Test Strategy
- Test types: Functional, UI, Integration, Regression
- Approach: Black box, boundary analysis, equivalence partitioning

## Environment
- Platforms: [OS, browsers, devices]
- Test data: [Sources and requirements]

## Entry Criteria
- [ ] Requirements documented and reviewed
- [ ] Test environment provisioned
- [ ] Test data prepared

## Exit Criteria
- [ ] 100% P0 tests pass
- [ ] 90%+ P1 tests pass
- [ ] No open critical bugs

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk] | H/M/L | H/M/L | [Strategy] |

## Timeline
[Estimate and milestones]
```

---

## Test Case Template

```markdown
## TC-001: [Clear Test Case Title]

**Priority:** P0 | P1 | P2 | P3
**Type:** Functional | UI | Integration | Regression | Security
**Estimated Time:** [N] minutes

### Objective
[What business behavior are we validating]

### Preconditions
- [Setup requirement 1]
- [Test data: e.g., user account test@example.com / Pass123!]

### Test Steps

1. [Navigate to / Perform action]
   **Expected:** [Exact expected result]

2. [Next action]
   **Expected:** [Expected outcome]

3. [Final action / Verify]
   **Expected:** [Final state or output]

### Test Data
- Input: [Values to use]
- User: [Account credentials if needed]

### Post-conditions
- [System state after passing]
- [Cleanup needed]

### Edge Cases to Also Test
- [TC-002: Negative case — invalid input]
- [TC-003: Boundary value — maximum input]
```

---

## Bug Report Template

```markdown
# BUG-[ID]: [Clear, Specific Title — Component: symptom when action]

**Severity:** Critical | High | Medium | Low
**Priority:** P0 | P1 | P2 | P3
**Type:** Functional | UI | Performance | Security

## Environment
- OS: [Windows 11 / macOS 14 / etc.]
- Browser: [Chrome 120 / Firefox 121 / etc.]
- Build/Version: [Commit or release]
- URL: [Exact page where bug occurs]

## Description
[Concise summary of the issue]

## Steps to Reproduce
1. [Specific step]
2. [Specific step]
3. [Observe issue]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Evidence
- Screenshot: [attached / link]
- Console errors: [paste output]
- Network response: [if relevant]

## Impact
- Users affected: [Scope]
- Frequency: Always | Intermittent | Rare
- Workaround: [If one exists]
```

---

## Severity Definitions

| Level | Criteria | Examples |
|-------|----------|----------|
| **Critical (P0)** | System crash, data loss, security breach | Payment fails, login broken |
| **High (P1)** | Major feature broken, no workaround | Search not returning results |
| **Medium (P2)** | Feature partial, workaround exists | Filter missing option |
| **Low (P3)** | Cosmetic, rare edge case | Minor alignment issue |

---

## Regression Suite Structure

| Suite Type | Duration | When to Run | Coverage |
|------------|----------|-------------|----------|
| Smoke | 15–30 min | Daily / Pre-deploy | Critical paths only |
| Targeted | 30–60 min | Per PR/change | Affected module |
| Full | 2–4 hours | Pre-release | All P0 and P1 |
| Sanity | 10–15 min | After hotfix | Quick validation |

### Prioritization

- **P0** — Business critical, security; run every time
- **P1** — Major features and common flows; run weekly+
- **P2** — Minor features, edge cases; run at releases
- **P3** — Cosmetic / rare; run full regression only

**Release gate:** All P0 pass + 90%+ P1 pass. Any P0 failure blocks release.

---

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| Vague test steps ("Click the button") | Can't reproduce reliably | Specific actions with exact expected results |
| Missing preconditions | Tests fail unexpectedly | Document all setup requirements |
| No test data | Tester is blocked | Provide sample data or generation method |
| Generic bug titles ("Button broken") | Hard to track | Specific: "[Feature] symptom when [action]" |
| Skipping edge cases | Miss critical bugs | Include boundary values, null inputs, concurrent access |

---

## Best Practices

**Writing test cases:**
- One concept per test case — keep them focused and short
- Test both positive (happy path) and negative scenarios
- Document all edge cases as separate test cases

**Bug reports:**
- Always provide reproducible steps; if intermittent, describe frequency
- Include environment details — bugs are often environment-specific
- Link to Figma/design spec for UI bugs

**Regression suites:**
- Automate P0/P1 where possible; keep manual tests for exploratory/UI
- Update the suite after every release to capture new coverage gaps
- Run smoke tests first — if they fail, fix the build before running the full suite
