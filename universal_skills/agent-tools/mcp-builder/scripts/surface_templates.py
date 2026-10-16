"""Select documentation and packaging surfaces before formatting a scaffold.

Every generated connector is MCP-only and depends on ``agent-connector-sdk``
alone. Unknown template names pass through unchanged.
"""

import re


def _bumpversion(text: str) -> str:
    """Drop the README section: the generated README has no version marker."""
    sections = re.split(r"(?m)(?=^\[bumpversion(?::|\]))", text)
    return "".join(
        section
        for section in sections
        if "file:README.md" not in section.partition("\n")[0]
    )


def _installation(text: str) -> str:
    return text.replace('pip install -e ".[all]"', 'pip install -e ".[mcp]"')


def select_template(name: str, template: str) -> str:
    """Select a named scaffold constant before its placeholders are formatted."""
    selectors = {
        "BUMPVERSION_CFG": _bumpversion,
        "DOCS_INSTALLATION_MD": _installation,
    }
    if name in selectors:
        return selectors[name](template)
    return template
