---
name: tdd-methodology
description: Strict Test-Driven Development (TDD) methodology guide using the Red-Green-Refactor cycle. Use when implementing features or fixing bugs with TDD, or when the user mentions TDD, test-first development, or comprehensive test coverage requirements. Do NOT use for pure design discussions, documentation tasks, or research-only work.
categories: [Development, Testing]
tags: [tdd, testing, red-green-refactor, quality, python]
---

# TDD Methodology Expert

Enforce and guide Test-Driven Development (TDD) methodology throughout the software development process. Apply the Red-Green-Refactor cycle strictly for every increment of functionality.

---

## When to Activate

Activate automatically when:
- The user explicitly requests TDD methodology
- The user asks to write tests or implement features in a test-first manner
- `CLAUDE.md`, `AGENTS.md`, or project memory references TDD

Do NOT use this skill for:
- Pure design or architecture discussions
- Documentation-only tasks
- Research or exploration without code changes

---

## Core Cycle: Red → Green → Refactor

Every feature increment must complete all three phases before moving to the next increment. Never skip or reorder phases.

### 🔴 Red — Write a Failing Test

1. Write a test that expresses the desired behavior
2. Run the test and verify it **fails** (for the right reason)
3. Confirm the failure message describes what is missing

**Principles:**
- Test must focus on exactly one behavior
- Test name must clearly describe the expected behavior
- Test must be readable without looking at the implementation
- The failure must be meaningful and guide implementation

**Example:**
```
1. Write: test_should_calculate_total_with_tax()
2. Run:   FAIL — "ShoppingCart has no attribute 'calculate_total'"
3. ✅ Proceed to Green
```

### 🟢 Green — Make the Test Pass

1. Write the **minimum** code to make the failing test pass
2. Run the test and verify it passes
3. Run all tests to ensure nothing broke

**Principles:**
- Write only enough code to pass the current test
- Do not add features that no test requires yet
- Shortcuts are acceptable — refactoring comes next
- Focus on correctness, not elegance

**Example:**
```
1. Implement: def calculate_total(self, tax_rate): ...
2. Run:       PASS ✅
3. All tests: PASS ✅
4. ✅ Proceed to Refactor
```

### 🔵 Refactor — Improve the Code

1. Identify duplication, poor naming, or structural issues
2. Refactor incrementally, running tests after each change
3. Verify all tests still pass
4. Improve both production code and test code

**Principles:**
- Never refactor with failing tests
- Make small, safe changes
- Run tests after every refactoring step
- Apply design patterns and best practices during this phase

**Example:**
```
1. Identify: Duplicated tax calculation logic
2. Extract:  Move to _calculate_tax() helper
3. Run:      PASS ✅
4. Improve:  Better variable names
5. Run:      PASS ✅
6. ✅ Commit and move to next increment
```

---

## Workflow Integration

### Before Any Code Task

1. Break the task into the **smallest testable behaviors**
2. Identify the simplest test case to start with
3. Announce: "🔴 RED PHASE: Writing a test for [behavior]"

### During Implementation

Follow this sequence for every increment:

```
🔴 Red:     Write failing test → Run → Verify failure
🟢 Green:   Write minimal code → Run → Verify pass
🔵 Refactor: Improve code → Run → Verify still passes
💾 Commit:  Save working, tested, clean increment
🔁 Repeat:  Next test for next behavior
```

### Communication Pattern

In every response involving code changes, state:
- **Current phase**: Red / Green / Refactor
- **Test status**: Passing or failing
- **Next steps**: What comes next in the cycle

```
🔴 RED PHASE: Writing a test for order discount calculation.

[Test code]

Running test... ❌ FAIL — "Order has no attribute 'apply_discount'"

🟢 GREEN PHASE: Implementing minimal code to pass the test.

[Implementation]

Running test... ✅ PASS
Running all tests... ✅ PASS

🔵 REFACTOR PHASE: Extracting discount logic to helper.

[Refactored code]

Running all tests... ✅ PASS
Ready to commit this increment.
```

---

## Reference Files

Load these when deeper context is needed:

- [references/tdd-principles.md](references/tdd-principles.md) — The complete Red-Green-Refactor philosophy, benefits, and best practices
- [references/code-smells.md](references/code-smells.md) — Catalog of code smells indicating test-after development; detection and refactoring strategies
- [references/testing-patterns.md](references/testing-patterns.md) — Language-agnostic patterns: AAA, Given-When-Then, fixtures, test doubles, parameterized tests

## Scripts

- `scripts/check_tdd_compliance.py` — Analyze code for TDD compliance issues (nested conditionals, long methods, missing test coverage)
- `scripts/validate_tests.py` — Validate test structure, AAA pattern, naming, and complexity

Run scripts with `--help` first to see usage options.
