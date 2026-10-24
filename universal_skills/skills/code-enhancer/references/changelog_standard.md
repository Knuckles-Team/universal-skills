# Changelog Standard Reference

> Reference for code-enhancer CE-023 domain (Changelog Audit)

## Keep a Changelog 1.1.0 Format

The community standard for changelogs is [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

### Guiding Principles

- Changelogs are for **humans**, not machines.
- There should be an entry for every **single version**.
- The same types of changes should be **grouped**.
- Versions and sections should be **linkable**.
- The **latest version** comes first.
- The **release date** of each version is displayed.
- Mention whether you follow **Semantic Versioning**.

### Standard Categories

| Category | Description |
|----------|-------------|
| `Added` | New features |
| `Changed` | Changes in existing functionality |
| `Deprecated` | Soon-to-be removed features |
| `Removed` | Now removed features |
| `Fixed` | Bug fixes |
| `Security` | Vulnerability fixes |

### Version Header Format

```
## [X.Y.Z] - YYYY-MM-DD
```

### Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-
```

## PyPI Integration

Add these URLs to `pyproject.toml` for PyPI sidebar links:

```toml
[project.urls]
Repository = "https://github.com/yourusername/yourproject.git"
Changelog = "https://github.com/yourusername/yourproject/blob/main/CHANGELOG.md"
```

The `Changelog` key is a recognized label — PyPI will render it as a sidebar link.

## Tools

### keepachangelog (Python)

```python
import keepachangelog

# Parse to dictionary
data = keepachangelog.to_dict("CHANGELOG.md")

# Get raw (unparsed) dict
raw = keepachangelog.to_raw_dict("CHANGELOG.md")

# Create a new release from Unreleased
new_version = keepachangelog.release("CHANGELOG.md")
```

**Note**: The `changelogs` package (pyupio) is **broken on Python 3.12+** due
to its use of the removed `imp` module. Use `keepachangelog` instead.

## Scoring Criteria (CE-023)

| Criterion | Points | Description |
|-----------|--------|-------------|
| CHANGELOG.md exists | 25 | File present at project root |
| Keep a Changelog format | 25 | Parseable by keepachangelog, valid categories |
| Version alignment | 25 | Latest version matches pyproject.toml |
| Recency & Unreleased | 25 | Has [Unreleased] section, entries within 30 days |
