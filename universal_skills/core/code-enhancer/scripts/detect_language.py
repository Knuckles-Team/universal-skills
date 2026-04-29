#!/usr/bin/env python3
"""CE-018: Language ecosystem detection for code-enhancer skill.

Detects primary and secondary languages in a project by scanning for
ecosystem indicator files. Returns a ``LanguageProfile`` dict consumed
by all downstream analyzers to adapt their scanning patterns.

CONCEPT:CE-018 — Language Ecosystem Detection
"""

import json
import sys
from pathlib import Path

# Mapping of indicator files → language ecosystem metadata
ECOSYSTEM_INDICATORS: dict[str, dict] = {
    # Python
    "pyproject.toml": {"lang": "python", "build": "pyproject", "weight": 10},
    "setup.py": {"lang": "python", "build": "setuptools", "weight": 8},
    "setup.cfg": {"lang": "python", "build": "setuptools", "weight": 6},
    "requirements.txt": {"lang": "python", "build": "pip", "weight": 5},
    "Pipfile": {"lang": "python", "build": "pipenv", "weight": 5},
    "poetry.lock": {"lang": "python", "build": "poetry", "weight": 7},
    # Go
    "go.mod": {"lang": "go", "build": "go-modules", "weight": 10},
    "go.sum": {"lang": "go", "build": "go-modules", "weight": 5},
    # Node / TypeScript
    "package.json": {"lang": "node", "build": "npm", "weight": 10},
    "tsconfig.json": {"lang": "typescript", "build": "tsc", "weight": 8},
    "yarn.lock": {"lang": "node", "build": "yarn", "weight": 5},
    "pnpm-lock.yaml": {"lang": "node", "build": "pnpm", "weight": 5},
    "bun.lockb": {"lang": "node", "build": "bun", "weight": 5},
    # Rust
    "Cargo.toml": {"lang": "rust", "build": "cargo", "weight": 10},
    "Cargo.lock": {"lang": "rust", "build": "cargo", "weight": 5},
    # Java / Kotlin
    "pom.xml": {"lang": "java", "build": "maven", "weight": 10},
    "build.gradle": {"lang": "java", "build": "gradle", "weight": 10},
    "build.gradle.kts": {"lang": "kotlin", "build": "gradle-kts", "weight": 10},
    # Ruby
    "Gemfile": {"lang": "ruby", "build": "bundler", "weight": 10},
    # C# / .NET
    "*.csproj": {"lang": "csharp", "build": "dotnet", "weight": 10},
    "*.sln": {"lang": "csharp", "build": "dotnet", "weight": 8},
}

# File extension → language mapping for file-count weighting
EXTENSION_MAP: dict[str, str] = {
    ".py": "python", ".pyi": "python",
    ".go": "go",
    ".js": "node", ".jsx": "node", ".ts": "typescript", ".tsx": "typescript",
    ".mjs": "node", ".cjs": "node",
    ".rs": "rust",
    ".java": "java", ".kt": "kotlin", ".kts": "kotlin",
    ".rb": "ruby",
    ".cs": "csharp",
    ".html": "web", ".css": "web", ".scss": "web", ".vue": "web",
    ".svelte": "web",
}

# Test framework indicators per language
TEST_FRAMEWORKS: dict[str, dict[str, str]] = {
    "python": {"pytest": "pytest", "unittest": "unittest", "nose": "nose2"},
    "go": {"go_test": "go test"},
    "node": {"jest": "jest", "vitest": "vitest", "mocha": "mocha"},
    "typescript": {"jest": "jest", "vitest": "vitest"},
    "rust": {"cargo_test": "cargo test"},
    "java": {"junit": "junit", "testng": "testng"},
    "ruby": {"rspec": "rspec", "minitest": "minitest"},
}

# Linter tools per language
LINTER_TOOLS: dict[str, list[str]] = {
    "python": ["ruff", "mypy", "bandit", "pylint", "flake8"],
    "go": ["go vet", "golangci-lint", "staticcheck"],
    "node": ["eslint", "prettier"],
    "typescript": ["eslint", "tsc", "prettier"],
    "rust": ["cargo clippy", "cargo fmt"],
    "java": ["checkstyle", "spotbugs", "pmd"],
    "ruby": ["rubocop", "reek"],
}

_SKIP_DIRS = {".venv", "venv", "__pycache__", "node_modules", ".git",
              "build", "dist", ".tox", ".mypy_cache", ".ruff_cache",
              "target", ".gradle", ".idea"}


def _count_files_by_extension(root: Path) -> dict[str, int]:
    """Count source files by extension, skipping vendored/build dirs."""
    counts: dict[str, int] = {}
    for f in root.rglob("*"):
        if f.is_file() and not any(skip in f.parts for skip in _SKIP_DIRS):
            ext = f.suffix.lower()
            if ext in EXTENSION_MAP:
                lang = EXTENSION_MAP[ext]
                counts[lang] = counts.get(lang, 0) + 1
    return counts


def _detect_ui_type(root: Path, file_counts: dict[str, int]) -> str | None:
    """Detect UI type: 'web', 'terminal', or None."""
    # Web UI detection
    web_count = file_counts.get("web", 0)
    node_count = file_counts.get("node", 0) + file_counts.get("typescript", 0)
    if web_count > 5 or node_count > 10:
        # Check for React/Vue/Angular/Svelte
        pkg_json = root / "package.json"
        if pkg_json.exists():
            try:
                content = pkg_json.read_text(encoding="utf-8", errors="ignore")
                if any(fw in content for fw in ("react", "vue", "angular", "@angular", "svelte", "next")):
                    return "web"
            except Exception:
                pass
        if web_count > 10:
            return "web"

    # Terminal UI detection (Python-specific for now)
    py_count = file_counts.get("python", 0)
    if py_count > 0:
        pyproject = root / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text(encoding="utf-8", errors="ignore")
                if any(lib in content for lib in ("textual", "rich", "curses", "blessed", "urwid", "prompt-toolkit")):
                    return "terminal"
            except Exception:
                pass

    return None


def detect_language(root_dir: str = ".") -> dict:
    """Detect language ecosystem for a project.

    Returns:
        LanguageProfile dict with: primary_language, secondary_languages,
        build_system, test_frameworks, linters, ui_type, file_counts, etc.
    """
    root = Path(root_dir).resolve()

    # Phase 1: Scan for indicator files
    detected: dict[str, int] = {}  # lang → cumulative weight
    build_systems: list[str] = []

    for name, meta in ECOSYSTEM_INDICATORS.items():
        if "*" in name:
            # Glob pattern (e.g., *.csproj)
            if list(root.glob(name)):
                lang = meta["lang"]
                detected[lang] = detected.get(lang, 0) + meta["weight"]
                build_systems.append(meta["build"])
        elif (root / name).exists():
            lang = meta["lang"]
            detected[lang] = detected.get(lang, 0) + meta["weight"]
            build_systems.append(meta["build"])

    # Phase 2: Count source files for weighting
    file_counts = _count_files_by_extension(root)
    for lang, count in file_counts.items():
        detected[lang] = detected.get(lang, 0) + min(count, 20)  # Cap file-count weight

    # Phase 3: Determine primary and secondary languages
    if not detected:
        return {
            "primary_language": "unknown",
            "secondary_languages": [],
            "build_systems": [],
            "test_frameworks": [],
            "linters": [],
            "ui_type": None,
            "file_counts": file_counts,
            "detected_weights": detected,
        }

    sorted_langs = sorted(detected.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_langs[0][0]
    secondary = [lang for lang, _ in sorted_langs[1:] if lang != primary]

    # Phase 4: Determine available test frameworks and linters
    available_test_fws = list(TEST_FRAMEWORKS.get(primary, {}).values())
    available_linters = LINTER_TOOLS.get(primary, [])

    # Phase 5: UI type detection
    ui_type = _detect_ui_type(root, file_counts)

    return {
        "primary_language": primary,
        "secondary_languages": secondary,
        "build_systems": list(set(build_systems)),
        "test_frameworks": available_test_fws,
        "linters": available_linters,
        "ui_type": ui_type,
        "file_counts": file_counts,
        "detected_weights": detected,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(detect_language(target), indent=2))
