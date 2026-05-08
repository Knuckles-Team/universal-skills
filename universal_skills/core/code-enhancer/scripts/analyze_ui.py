#!/usr/bin/env python3
"""CE-019: UI/UX quality analysis for code-enhancer skill.

Grades user interfaces using Nielsen's 10 Usability Heuristics adapted
for automated static file analysis. Supports Web UI (React/Vue/Angular)
and Terminal UI (Textual/Rich/curses) detection.

No browser or Chrome dependency — pure static file and pattern analysis.

CONCEPT:CE-019 — UI/UX Quality Analysis
"""

import json
import re
import sys
from pathlib import Path

_SKIP_DIRS = frozenset(
    {
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".git",
        "build",
        "dist",
        ".next",
        ".nuxt",
    }
)

# ── Nielsen's 10 Usability Heuristics ──
# Each check returns (pass: bool, detail: str)
HEURISTICS = [
    "visibility_of_system_status",
    "match_real_world",
    "user_control_freedom",
    "consistency_standards",
    "error_prevention",
    "recognition_vs_recall",
    "flexibility_efficiency",
    "aesthetic_minimal_design",
    "error_recovery",
    "help_documentation",
]


def _scan_files(root: Path, extensions: set[str]) -> list[Path]:
    """Collect source files with given extensions, skipping vendored dirs."""
    return [
        f
        for f in root.rglob("*")
        if f.is_file()
        and f.suffix.lower() in extensions
        and not any(skip in f.parts for skip in _SKIP_DIRS)
    ]


def _read_all_content(files: list[Path]) -> str:
    """Read and concatenate all file contents (capped at 500KB)."""
    chunks: list[str] = []
    total = 0
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            chunks.append(content)
            total += len(content)
            if total > 500_000:
                break
        except Exception:
            continue
    return "\n".join(chunks)


def _detect_ui_type(root: Path) -> str | None:
    """Detect UI type: 'web', 'terminal', or None."""
    # Web UI
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            content = pkg_json.read_text(encoding="utf-8", errors="ignore")
            if any(
                fw in content
                for fw in (
                    "react",
                    "vue",
                    "angular",
                    "@angular",
                    "svelte",
                    "next",
                    "nuxt",
                    "vite",
                    "webpack",
                )
            ):
                return "web"
        except Exception:
            pass

    html_files = _scan_files(root, {".html", ".htm"})
    if len(html_files) > 5:
        return "web"

    # Terminal UI (Python)
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8", errors="ignore")
            if any(
                lib in content
                for lib in (
                    "textual",
                    "rich",
                    "blessed",
                    "urwid",
                    "prompt-toolkit",
                    "curses",
                    "npyscreen",
                )
            ):
                return "terminal"
        except Exception:
            pass

    # Check Python imports for TUI libraries
    py_files = _scan_files(root, {".py"})
    for f in py_files[:50]:  # Sample first 50
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            if any(
                imp in content
                for imp in (
                    "import textual",
                    "from textual",
                    "import rich",
                    "from rich",
                    "import curses",
                    "import blessed",
                )
            ):
                return "terminal"
        except Exception:
            continue

    return None


# ────────────────────── Web UI Heuristic Checks ──────────────────────


def _web_visibility(content: str, files: list[Path]) -> tuple[bool, str]:
    """H1: Loading indicators, progress bars, spinners."""
    indicators = ["loading", "spinner", "progress", "skeleton", "placeholder"]
    found = [i for i in indicators if i in content.lower()]
    return len(found) >= 2, f"Status indicators found: {', '.join(found) or 'none'}"


def _web_real_world(content: str, files: list[Path]) -> tuple[bool, str]:
    """H2: Semantic HTML, natural labels."""
    semantic = ["<nav", "<main", "<article", "<section", "<aside", "<header", "<footer"]
    found = [s for s in semantic if s in content]
    return len(found) >= 3, f"Semantic elements: {len(found)}/7"


def _web_user_control(content: str, files: list[Path]) -> tuple[bool, str]:
    """H3: Navigation, undo, back buttons, cancel actions."""
    patterns = [
        "undo",
        "cancel",
        "back",
        "goBack",
        "navigate",
        "router.push",
        "history",
    ]
    found = [p for p in patterns if p in content]
    return len(found) >= 2, f"Control patterns: {', '.join(found) or 'none'}"


def _web_consistency(content: str, files: list[Path]) -> tuple[bool, str]:
    """H4: CSS variables, component reuse, design tokens."""
    css_files = [f for f in files if f.suffix in (".css", ".scss")]
    css_vars = content.count("var(--")
    component_files = [
        f for f in files if f.suffix in (".jsx", ".tsx", ".vue", ".svelte")
    ]
    return (
        css_vars >= 5 or len(component_files) >= 5,
        f"CSS vars: {css_vars}, components: {len(component_files)}",
    )


def _web_error_prevention(content: str, files: list[Path]) -> tuple[bool, str]:
    """H5: Form validation, required fields, confirmations."""
    patterns = [
        "required",
        "validate",
        "validation",
        "confirm",
        "pattern=",
        'type="email"',
    ]
    found = [p for p in patterns if p in content]
    return len(found) >= 2, f"Prevention patterns: {', '.join(found) or 'none'}"


def _web_recognition(content: str, files: list[Path]) -> tuple[bool, str]:
    """H6: Visible navigation, breadcrumbs, labels."""
    patterns = ["breadcrumb", "sidebar", "menu", "dropdown", "tooltip", "aria-label"]
    found = [p for p in patterns if p in content.lower()]
    return len(found) >= 2, f"Recognition aids: {', '.join(found) or 'none'}"


def _web_flexibility(content: str, files: list[Path]) -> tuple[bool, str]:
    """H7: Responsive design, keyboard navigation, shortcuts."""
    patterns = [
        "@media",
        "responsive",
        "useMediaQuery",
        "onKeyDown",
        "keyboard",
        "shortcut",
        "hotkey",
    ]
    found = [p for p in patterns if p in content]
    return len(found) >= 2, f"Flexibility features: {', '.join(found) or 'none'}"


def _web_aesthetic(content: str, files: list[Path]) -> tuple[bool, str]:
    """H8: Clean layout, whitespace, minimal clutter."""
    css_content = ""
    for f in files:
        if f.suffix in (".css", ".scss"):
            try:
                css_content += f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                pass
    has_spacing = any(p in css_content for p in ("gap:", "padding:", "margin:", "grid"))
    has_colors = css_content.count("var(--") >= 3 or css_content.count("#") >= 5
    return (
        has_spacing and has_colors,
        f"Spacing system: {has_spacing}, Color system: {has_colors}",
    )


def _web_error_recovery(content: str, files: list[Path]) -> tuple[bool, str]:
    """H9: Error boundary, error messages, try-catch in UI."""
    patterns = [
        "ErrorBoundary",
        "error-boundary",
        "catch",
        "fallback",
        "error message",
        "toast",
        "notification",
    ]
    found = [p for p in patterns if p in content]
    return len(found) >= 2, f"Error recovery: {', '.join(found) or 'none'}"


def _web_help(content: str, files: list[Path]) -> tuple[bool, str]:
    """H10: Help pages, tooltips, documentation links."""
    patterns = [
        "tooltip",
        "help",
        "documentation",
        "docs",
        "guide",
        "tutorial",
        "aria-describedby",
        "title=",
    ]
    found = [p for p in patterns if p in content.lower()]
    return len(found) >= 2, f"Help features: {', '.join(found) or 'none'}"


# Accessibility sub-checks for web
def _web_accessibility(content: str, files: list[Path]) -> dict:
    """Check WCAG 2.1 AA key criteria."""
    checks = {
        "alt_tags": bool(re.search(r'alt="[^"]+"|alt=\'[^\']+\'', content)),
        "aria_labels": "aria-label" in content or "aria-labelledby" in content,
        "role_attributes": "role=" in content,
        "lang_attribute": 'lang="' in content or "lang='" in content,
        "focus_management": "tabIndex" in content
        or "tabindex" in content
        or ":focus" in content,
        "color_contrast": "contrast" in content.lower()
        or "prefers-color-scheme" in content,
    }
    return checks


# ────────────────────── Terminal UI Heuristic Checks ──────────────────────


def _tui_visibility(content: str, files: list[Path]) -> tuple[bool, str]:
    """H1: Spinners, status bars, progress indicators."""
    patterns = ["spinner", "progress", "status", "StatusBar", "loading", "ProgressBar"]
    found = [p for p in patterns if p in content]
    return len(found) >= 1, f"TUI status: {', '.join(found) or 'none'}"


def _tui_real_world(content: str, files: list[Path]) -> tuple[bool, str]:
    """H2: Natural command names, readable labels."""
    # Check for argparse/click with descriptive help text
    has_help = "help=" in content or "help_text=" in content
    return has_help, f"Help text in CLI arguments: {has_help}"


def _tui_user_control(content: str, files: list[Path]) -> tuple[bool, str]:
    """H3: Ctrl+C handling, exit/quit, confirmation prompts."""
    patterns = [
        "KeyboardInterrupt",
        "signal.SIGINT",
        "Ctrl+C",
        "quit",
        "exit",
        "confirm",
        "Confirm",
    ]
    found = [p for p in patterns if p in content]
    return len(found) >= 2, f"Control patterns: {', '.join(found) or 'none'}"


def _tui_consistency(content: str, files: list[Path]) -> tuple[bool, str]:
    """H4: Consistent color scheme, key bindings."""
    patterns = ["Style", "theme", "color", "Color", "BINDINGS", "key_bindings"]
    found = [p for p in patterns if p in content]
    return len(found) >= 2, f"Consistency patterns: {', '.join(found) or 'none'}"


def _tui_error_prevention(content: str, files: list[Path]) -> tuple[bool, str]:
    """H5: Input validation, --dry-run flags."""
    patterns = ["validate", "dry.run", "dry_run", "--dry-run", "confirmation"]
    found = [p for p in patterns if p in content.lower()]
    return len(found) >= 1, f"Prevention: {', '.join(found) or 'none'}"


def _tui_recognition(content: str, files: list[Path]) -> tuple[bool, str]:
    """H6: Tab completion, command suggestions, autocomplete."""
    patterns = ["complete", "autocomplete", "suggest", "completer", "tab_complete"]
    found = [p for p in patterns if p in content.lower()]
    return len(found) >= 1, f"Recognition aids: {', '.join(found) or 'none'}"


def _tui_flexibility(content: str, files: list[Path]) -> tuple[bool, str]:
    """H7: Keyboard shortcuts, config files, aliases."""
    patterns = ["shortcut", "keybind", "BINDINGS", "config", "settings", "alias"]
    found = [p for p in patterns if p in content]
    return len(found) >= 2, f"Flexibility: {', '.join(found) or 'none'}"


def _tui_aesthetic(content: str, files: list[Path]) -> tuple[bool, str]:
    """H8: Aligned output, box drawing, colors, tables."""
    patterns = [
        "Table",
        "Panel",
        "Box",
        "border",
        "Rich",
        "rich.table",
        "rich.panel",
        "align",
        "center",
    ]
    found = [p for p in patterns if p in content]
    return len(found) >= 2, f"Aesthetic elements: {', '.join(found) or 'none'}"


def _tui_error_recovery(content: str, files: list[Path]) -> tuple[bool, str]:
    """H9: Descriptive stderr, exit codes, error formatting."""
    patterns = [
        "sys.exit",
        "exit(1)",
        "stderr",
        "console.print_exception",
        "traceback",
        "error:",
        "Error:",
    ]
    found = [p for p in patterns if p in content]
    return len(found) >= 2, f"Error handling: {', '.join(found) or 'none'}"


def _tui_help(content: str, files: list[Path]) -> tuple[bool, str]:
    """H10: --help flag, man pages, usage docs."""
    patterns = ["--help", "argparse", "click", "typer", "usage:", "Usage:"]
    found = [p for p in patterns if p in content]
    return len(found) >= 2, f"Help/docs: {', '.join(found) or 'none'}"


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


_WEB_CHECKS = [
    _web_visibility,
    _web_real_world,
    _web_user_control,
    _web_consistency,
    _web_error_prevention,
    _web_recognition,
    _web_flexibility,
    _web_aesthetic,
    _web_error_recovery,
    _web_help,
]

_TUI_CHECKS = [
    _tui_visibility,
    _tui_real_world,
    _tui_user_control,
    _tui_consistency,
    _tui_error_prevention,
    _tui_recognition,
    _tui_flexibility,
    _tui_aesthetic,
    _tui_error_recovery,
    _tui_help,
]


def analyze_ui(root_dir: str = ".") -> dict:
    """Analyze UI/UX quality using Nielsen's 10 heuristics.

    Returns:
        dict with domain, score, grade, findings, heuristic_results.
        If no UI detected, returns score=N/A with an informational note.
    """
    root = Path(root_dir).resolve()
    ui_type = _detect_ui_type(root)

    if ui_type is None:
        return {
            "domain": "UI/UX Quality",
            "score": -1,  # N/A — not scored
            "grade": "N/A",
            "ui_type": None,
            "findings": ["No UI detected — domain not applicable"],
            "justifications": [
                {
                    "criterion": "ui_detection",
                    "points": -1,
                    "evidence": str(root),
                    "reasoning": "No web or terminal UI framework detected. Domain skipped.",
                }
            ],
            "heuristic_results": [],
            "accessibility": {},
        }

    # Collect relevant files
    if ui_type == "web":
        extensions = {
            ".html",
            ".htm",
            ".css",
            ".scss",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".vue",
            ".svelte",
        }
        checks = _WEB_CHECKS
    else:  # terminal
        extensions = {".py"}
        checks = _TUI_CHECKS

    files = _scan_files(root, extensions)
    content = _read_all_content(files)

    # Run heuristic checks
    heuristic_results: list[dict] = []
    passed_count = 0

    for i, check_fn in enumerate(checks):
        passed, detail = check_fn(content, files)
        heuristic_results.append(
            {
                "heuristic": HEURISTICS[i],
                "passed": passed,
                "detail": detail,
                "points": 10 if passed else 0,
            }
        )
        if passed:
            passed_count += 1

    # Accessibility (web only)
    accessibility = {}
    if ui_type == "web":
        accessibility = _web_accessibility(content, files)

    # Scoring: 10 heuristics × 10 points each = 100 max
    score = passed_count * 10
    findings: list[str] = []

    failed_heuristics = [h for h in heuristic_results if not h["passed"]]
    if failed_heuristics:
        for h in failed_heuristics:
            findings.append(f"Failed heuristic '{h['heuristic']}': {h['detail']}")

    # Accessibility bonus/penalty for web
    if ui_type == "web" and accessibility:
        a11y_pass = sum(1 for v in accessibility.values() if v)
        a11y_total = len(accessibility)
        if a11y_pass < a11y_total // 2:
            findings.append(f"Accessibility: {a11y_pass}/{a11y_total} WCAG checks pass")

    justifications = [
        {
            "criterion": f"ui_heuristics_{ui_type}",
            "points": score,
            "evidence": json.dumps(
                {
                    "ui_type": ui_type,
                    "files_analyzed": len(files),
                    "heuristics_passed": passed_count,
                }
            ),
            "reasoning": (
                f"{ui_type.upper()} UI detected. {passed_count}/10 Nielsen heuristics pass. "
                f"Analyzed {len(files)} {ui_type} files."
            ),
        }
    ]

    return {
        "domain": "UI/UX Quality",
        "score": score,
        "grade": _score_to_grade(score),
        "ui_type": ui_type,
        "findings": findings,
        "justifications": justifications,
        "heuristic_results": heuristic_results,
        "accessibility": accessibility,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(analyze_ui(target), indent=2))
