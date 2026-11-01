"""Size, complexity and clone limits shared by every code-enhancer analyzer.

The values come from the thresholds table of the organization constitution
(`.specify/memory/constitution.md` in the pipelines repository), which article XI
and article XII govern. This module is the one place the skill holds them; the
skill never sets a looser or a private limit.
"""

from __future__ import annotations

import ast

MAX_CYCLOMATIC = 10
MAX_COGNITIVE = 15
MAX_STATEMENTS_PER_FUNCTION = 35
MAX_INDENT_DEPTH = 4
MAX_POSITIONAL_ARGS = 3
MAX_LINES_PER_FILE = 300
CLONE_SIMILARITY = 0.85


def statement_count(node: ast.AST) -> int:
    """Count the statements in a function body, nested ones included."""
    return sum(
        isinstance(child, ast.stmt) for child in ast.walk(node) if child is not node
    )
