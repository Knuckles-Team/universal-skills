# Pytest Quality Rubric

> Reference for code-enhancer CE-024 domain (Pytest Quality Grading)

## F.I.R.S.T. Principles

| Principle | Description | How We Check |
|-----------|-------------|--------------|
| **Fast** | Tests should execute quickly | Covered by CE-016 (Test Execution) timing |
| **Independent** | No shared state between tests | Check fixture scoping, no global mutable state |
| **Repeatable** | Same result every run | Check for random/time-dependent code |
| **Self-validating** | Clear pass/fail via assertions | Count assertions per test |
| **Timely** | Written alongside production code | Test-to-source ratio (CE-005) |

## Scoring Breakdown (100 pts)

### 1. Naming Quality (20 pts)

**Good**: `test_user_login_with_invalid_password_returns_401()`
**Bad**: `test_login1()`, `test_case_42()`

| Check | Deduction | Trigger |
|-------|-----------|---------|
| Generic names (test_1, test_case_N) | -2 per test (max -10) | Regex pattern match |
| Non-descriptive names (<15 chars) | -5 if <50% descriptive, -2 if <80% | Character length check |

### 2. Structure & Organization (20 pts)

| Check | Deduction | Trigger |
|-------|-----------|---------|
| Test files >500 lines | -3 per file (max -10) | Line count |
| Files with >30 tests | -2 per file (max -5) | Function count |
| No subdirectory organization | -3 | >5 test files with no subdirs |
| Missing conftest.py | -2 | >10 tests without shared conftest |

**Recommended structure**:
```
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Fast, isolated tests
│   └── test_module.py
├── integration/         # Cross-boundary tests
│   └── test_api.py
└── e2e/                 # End-to-end tests
```

### 3. Fixture & Parametrize Usage (20 pts)

| Check | Deduction | Trigger |
|-------|-----------|---------|
| Low fixture usage (<20%) | -8 | >10 tests |
| Low fixture usage (<40%) | -4 | >10 tests |
| No @pytest.mark.parametrize | -5 | >10 tests |
| No shared conftest fixtures | -4 | >10 tests |

**AAA Pattern** (Arrange-Act-Assert):
```python
def test_user_creation(db_session):
    # Arrange
    user_data = {"name": "Alice", "email": "alice@example.com"}

    # Act
    user = create_user(db_session, **user_data)

    # Assert
    assert user.id is not None
    assert user.name == "Alice"
```

### 4. Assertion Quality (20 pts)

| Check | Deduction | Trigger |
|-------|-----------|---------|
| Tests with no assertions | -2 per test (max -10) | Zero assert statements |
| Weak assertions | -1 per test (max -5) | `assert result is not None`, `assert True` |
| Too many assertions (>5) | -3 | >30% of tests |

**Weak assertions to avoid**:
- `assert result is not None`
- `assert result`
- `assert True`
- `assert response`

### 5. AI Slop Detection (20 pts)

| Check | Deduction | Trigger |
|-------|-----------|---------|
| Duplicate test bodies | -1 per dup (max -10) | MD5 hash comparison |
| Over-mocking (>5 mocks) | -1 per test (max -5) | Mock/patch count |
| Very long tests (>100 lines) | -2 per test (max -5) | Line count |

**AI slop red flags**:
1. Copy-paste tests instead of parametrized/fixtures
2. Tests that mirror implementation line-by-line
3. Overuse of mocks for pure functions
4. Generic/numbered test names
5. No edge cases or error paths
6. Verbose setup in every test instead of fixtures
7. Hardcoded magic values everywhere

## Grade Scale

| Grade | Score | Interpretation |
|-------|-------|----------------|
| A | 90-100 | Clean, DRY, well-organized, behavior-focused |
| B | 80-89 | Good overall, minor improvements possible |
| C | 70-79 | Works but has duplication, long functions, or weak assertions |
| D | 60-69 | Significant structural issues |
| F | 0-59 | Monolithic, copy-paste, implementation-coupled → AI slop |

## Resources

- **Official pytest docs**: [Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- **Book**: "Python Testing with pytest" by Brian Okken
- **Linters**: `flake8-pytest-style`, `pytest-smell`
