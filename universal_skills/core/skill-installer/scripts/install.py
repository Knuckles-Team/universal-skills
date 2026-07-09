#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import subprocess
import sys
import logging
from pathlib import Path
from typing import List, Optional

try:
    from agent_utilities.base_utilities import get_logger, retrieve_package_name
except ImportError:
    # Fallback if agent_utilities is not available
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def retrieve_package_name():
        return "universal_skills"

else:
    logger = get_logger(__name__)

# Try to import utilities from the packages
try:
    from universal_skills import skill_utilities
except ImportError:
    skill_utilities = None

try:
    from skill_graphs import skill_graph_utilities
except ImportError:
    skill_graph_utilities = None

# Per-agent frontmatter adapter (Codex et al. reject our top-level keys). Try the
# relative import (normal package context) first, then fall back to an absolute
# import off this file's own directory — covers direct script execution
# (`python install.py`) AND the `install-skills` console-script shim, neither of
# which give this module a real dotted package (its parent dir is hyphenated:
# `core/skill-installer/`, not a valid Python identifier).
try:
    from . import adapters
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import adapters
    except ImportError:
        adapters = None


# Entry-point group through which any installed agent-package contributes its
# own skills. Kept as a standalone local copy (not imported from agent-utilities)
# so the installer still runs when agent-utilities is absent — same rationale as
# the ImportError fallbacks above. CONCEPT:OS-5.52.
SKILL_PROVIDER_GROUP = "agent_utilities.skill_providers"


def _iter_skill_providers() -> List[tuple]:
    """Resolve every ``agent_utilities.skill_providers`` entry-point to a dir.

    Returns ``(provider_name, asset_dir)`` tuples. Resolves each contributor's
    data directory via ``importlib.resources`` without importing the agent's
    business logic. Unresolvable/uninstalled providers are skipped, not fatal.
    """
    from importlib.metadata import entry_points
    from importlib.resources import as_file, files

    out: List[tuple] = []
    seen: set = set()
    try:
        eps = entry_points(group=SKILL_PROVIDER_GROUP)
    except TypeError:  # pragma: no cover - very old importlib.metadata
        eps = entry_points().get(SKILL_PROVIDER_GROUP, [])
    for ep in sorted(eps, key=lambda e: e.name):
        if ep.name in seen:
            continue
        try:
            with as_file(files(ep.value)) as resolved:
                path = Path(resolved)
            if path.is_dir():
                out.append((ep.name, path))
                seen.add(ep.name)
        except Exception as e:  # noqa: BLE001
            # Failure-isolated by contract: a provider that can't be resolved — not
            # installed, bad value, or whose package raises on import (e.g. a heavy
            # connector __init__ with a circular import) — is SKIPPED, never fatal, so
            # one broken package can't abort discovery for the rest of the fleet.
            logger.debug("Could not resolve skill provider %s: %s", ep.name, e)
            continue
    return out


def get_tool_paths() -> dict:
    """Return per-tool skill-install directories, OS-aware.

    Kept in parity with the mcp-installer's tool set so a single bootstrap can
    install both skills and MCP config into every agent tool a host has. Each
    value is the *skills* directory for that tool; ``detect_present_tools()``
    decides which of these to write to in ``--all-detected`` mode.
    """
    is_windows = sys.platform == "win32"
    is_mac = sys.platform == "darwin"
    home = Path("~").expanduser()

    paths = {
        "windsurf": home / ".codeium" / "windsurf" / "skills",
        "claude": home / ".claude" / "skills",
        "openclaw": home / ".openclaw" / "skills",
        "antigravity": home / ".gemini" / "antigravity" / "skills",
        "codex": home / ".codex" / "skills",
        "devin": home / ".config" / "devin" / "skills",
        "cursor": home / ".cursor" / "skills",
        # xAI Grok Code CLI — `grok` and `grok-code` are aliases for the same dir.
        "grok": home / ".grok" / "skills",
        "grok-code": home / ".grok" / "skills",
    }

    # OpenCode
    if is_windows:
        appdata = Path(os.environ.get("APPDATA", "~\\AppData\\Roaming")).expanduser()
        paths["opencode"] = appdata / "opencode" / "skills"
        paths["zed"] = appdata / "Zed" / "skills"
    else:
        paths["opencode"] = home / ".config" / "opencode" / "skills"
        paths["zed"] = home / ".config" / "zed" / "skills"

    # Agent Utilities / Agent Terminal UI (shared config dir)
    if is_windows:
        localappdata = Path(
            os.environ.get("LOCALAPPDATA", "~\\AppData\\Local")
        ).expanduser()
        agent_utils_path = localappdata / "agent-utilities" / "skills"
    elif is_mac:
        agent_utils_path = (
            home / "Library" / "Application Support" / "agent-utilities" / "skills"
        )
    else:
        # XDG *data* dir (platformdirs user_data_dir), matching agent-utilities'
        # ``core.paths.skills_dir()`` which the agent factory auto-loads — NOT the
        # config dir. (macOS/Windows above already use their data dir.)
        xdg_data = Path(
            os.environ.get("XDG_DATA_HOME") or (home / ".local" / "share")
        ).expanduser()
        agent_utils_path = xdg_data / "agent-utilities" / "skills"
    paths["agent-utilities"] = agent_utils_path
    paths["agent-terminal-ui"] = agent_utils_path

    return paths


# Standard skill paths for various tools (OS-aware; parity with mcp-installer).
TOOL_PATHS = get_tool_paths()

# Workspace-specific skill paths (relative to workspace root)
WORKSPACE_PATHS = {
    "antigravity": Path(".agent/skills"),
    "default": Path(".agent/skills"),
}


def detect_present_tools() -> dict:
    """Return the subset of TOOL_PATHS whose tool is actually installed.

    A tool counts as present when the parent of its skills directory exists
    (e.g. ``~/.claude`` for Claude Code). This keeps ``--all-detected`` from
    materialising skill folders for tools the host doesn't have. Duplicate
    destinations (agent-utilities/agent-terminal-ui share a dir) are collapsed.
    """
    present: dict = {}
    seen: set = set()
    for tool, skills_dir in TOOL_PATHS.items():
        marker = skills_dir.parent
        if not marker.exists():
            continue
        resolved = str(skills_dir)
        if resolved in seen:
            continue
        seen.add(resolved)
        present[tool] = skills_dir
    return present


def _skill_type(path: Path) -> Optional[str]:
    """Read the ``skill_type`` frontmatter (skill|workflow|graph) from a skill dir."""
    skill_md = path / "SKILL.md"
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    fm = text.split("---", 2)[1] if text.count("---") >= 2 else ""
    m = re.search(r"^skill_type:\s*([A-Za-z]+)\s*$", fm, re.MULTILINE)
    return m.group(1).lower() if m else None


def _matches_layer(path: Path, layer: str) -> bool:
    """Filter a skill source path by layer.

    ``atomic`` = an atomic building-block skill — what an agent invokes directly, so
    it belongs in Claude. ``workflows`` = a skill-workflow, meant for the graph-os
    orchestrator (Claude fires them via ``kg-delegate`` / ``graph_orchestrate
    execute_workflow``) and usually NOT installed into Claude — that would bloat the
    always-loaded skill list. ``all`` = no filter.

    Classification is by the authoritative ``skill_type`` frontmatter; the path
    (``/workflows/`` segment or a ``*-workflows`` parent) is a back-compat fallback.
    """
    st = _skill_type(path)
    if st in ("skill", "workflow", "graph"):
        is_workflow = st == "workflow"
    else:
        is_workflow = (
            f"{os.sep}workflows{os.sep}" in f"{path}{os.sep}"
            or path.parent.name.endswith("-workflows")
        )
    if layer == "atomic":
        return not is_workflow
    if layer == "workflows":
        return is_workflow
    return True


UNIVERSAL_PROVIDER = "universal-skills"


def get_source_paths(
    skill_names: Optional[List[str]] = None,
    group: Optional[str] = None,
    include_graphs: bool = False,
    layer: str = "all",
    providers: Optional[set] = None,
) -> List[Path]:
    """Uses utility functions to locate source paths of skills and graphs.

    ``providers`` optionally restricts which contributors are installed: the built-in
    ``universal-skills`` and/or specific agent-package ``skill_providers`` names. When
    ``None`` (default) every available provider is installed.
    """
    sources = []
    want_universal = providers is None or UNIVERSAL_PROVIDER in providers

    # Universal Skills
    if want_universal and not skill_utilities:
        logger.error("Could not import skill_utilities.")
    elif want_universal:
        # If specific skill names provided, search for them individually
        if skill_names:
            for name in skill_names:
                paths = skill_utilities.get_universal_skills_path(name=name.strip())
                sources.extend([Path(p) for p in paths])
        # If group (category) provided, get everything in that category
        elif group:
            paths = skill_utilities.get_universal_skills_path(category=group)
            sources.extend([Path(p) for p in paths])
        # Otherwise get all
        else:
            paths = skill_utilities.get_universal_skills_path()
            sources.extend([Path(p) for p in paths])
        # Restrict to the requested layer (atomic skills vs graph-os workflows).
        if layer != "all":
            sources = [p for p in sources if _matches_layer(p, layer)]

    # Skill Graphs
    if include_graphs and skill_graph_utilities:
        if skill_names:
            for name in skill_names:
                paths = skill_graph_utilities.get_skill_graphs_path(name=name.strip())
                sources.extend([Path(p) for p in paths])
        elif group:
            paths = skill_graph_utilities.get_skill_graphs_path(category=group)
            sources.extend([Path(p) for p in paths])
        else:
            paths = skill_graph_utilities.get_skill_graphs_path()
            sources.extend([Path(p) for p in paths])
    elif include_graphs:
        logger.warning("Could not import skill_graph_utilities.")

    # Package-contributed skills (entry-point providers, CONCEPT:OS-5.52).
    # Any installed agent-package that declares an ``agent_utilities.skill_providers``
    # entry-point contributes the ``SKILL.md`` dirs under its asset directory.
    wanted = {n.strip() for n in skill_names} if skill_names else None
    for _provider_name, asset_dir in _iter_skill_providers():
        if providers is not None and _provider_name not in providers:
            continue
        for skill_md in sorted(asset_dir.rglob("SKILL.md")):
            skill_dir = skill_md.parent
            parts = skill_dir.parts
            is_graph = "skill_graphs" in parts or "skill-graphs" in parts
            # Honour the same gates as the universal-skills branch.
            if is_graph and not include_graphs:
                continue
            if wanted is not None and skill_dir.name not in wanted:
                continue
            if group and group not in parts:
                continue
            if layer != "all" and not _matches_layer(skill_dir, layer):
                continue
            sources.append(skill_dir)

    # De-dup by resolved path so a skill is never installed twice.
    seen: set = set()
    deduped: List[Path] = []
    for src in sources:
        key = str(src.resolve())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(src)
    return deduped


# Removed get_skill_graphs_source_path as it's merged into get_source_paths


def get_workspace_root() -> Optional[Path]:
    """Attempts to find the workspace root by looking for .git or other markers."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / ".agent").exists():
            return parent
    return current


def _remove_dest(skill_dst: Path) -> None:
    """Remove an existing destination, whether it's a symlink, file, or directory."""
    if skill_dst.is_symlink() or skill_dst.is_file():
        skill_dst.unlink()
    elif skill_dst.is_dir():
        shutil.rmtree(skill_dst)


def _prune_broken_symlinks(target_path: Path) -> int:
    """Remove dead symlinks (target no longer exists) from an install dir.

    Refactors leave cruft: a **renamed** skill (``kg-delegation-router`` → ``kg-delegate``)
    or a **removed** one leaves behind a symlink pointing at a source path that is gone.
    The capability is already unavailable, and a dead link confuses skill discovery, so
    we prune it. Only *broken* links are touched — valid links (including a moved skill
    that was just repointed to its new source) are left alone. Also sweeps the
    ``skill-graphs/`` subdir. Returns the number pruned.
    """
    pruned = 0
    for root in (target_path, target_path / "skill-graphs"):
        if not root.is_dir():
            continue
        for entry in root.iterdir():
            # ``exists()`` follows the link, so a symlink that is *also* not exists()
            # is precisely a dangling/broken link.
            if entry.is_symlink() and not entry.exists():
                try:
                    dead_target = os.readlink(entry)
                    entry.unlink()
                    logger.info(f"Pruned broken symlink: {entry.name} → {dead_target}")
                    pruned += 1
                except OSError as e:
                    logger.warning(f"Could not prune broken symlink {entry.name}: {e}")
    if pruned:
        logger.info(
            f"Pruned {pruned} broken symlink(s) left by renamed/removed skills."
        )
    return pruned


def _try_windows_junction(dst: Path, src: Path) -> bool:
    """On Windows, create a directory JUNCTION (the symlink equivalent that needs no
    admin / Developer Mode). Returns True on success. ``mklink /J`` is a cmd builtin,
    so it must run through ``cmd /c``."""
    if os.name != "nt":
        return False
    import subprocess

    try:
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
            check=True,
            capture_output=True,
        )
        return True
    except Exception:
        return False


def _transform_skill_md(skill_dst: Path, contract) -> None:
    """Overwrite ``<skill_dst>/SKILL.md`` with its per-agent-adapted frontmatter."""
    skill_md = skill_dst / "SKILL.md"
    if adapters is None or not skill_md.is_file():
        return
    original = skill_md.read_text(encoding="utf-8", errors="replace")
    transformed = adapters.transform_frontmatter(original, contract)
    if transformed != original:
        skill_md.write_text(transformed, encoding="utf-8")


def _install_transformed_copy(
    skill_src: Path, skill_dst: Path, force: bool, contract
) -> bool:
    """Copy ``skill_src`` → ``skill_dst`` and rewrite its SKILL.md for ``contract``.

    Shared by the top-level skill install and (for ``flat_discovery`` targets) each
    promoted nested sub-skill. Returns True if a copy was performed.
    """
    if skill_dst.exists() and not force:
        logger.info(
            f"Skipping {skill_dst.name} (already exists). Use --force to overwrite."
        )
        return False
    if skill_dst.exists() or skill_dst.is_symlink():
        _remove_dest(skill_dst)
    shutil.copytree(skill_src.resolve(), skill_dst)
    _transform_skill_md(skill_dst, contract)
    return True


def install_skills(
    target_path: Path,
    skill_names: Optional[List[str]] = None,
    group: Optional[str] = None,
    force: bool = False,
    include_graphs: bool = False,
    symlink: bool = False,
    layer: str = "all",
    prune: bool = True,
    providers: Optional[set] = None,
    contract=None,
):
    """Install skills to the target path by copy (default) or symlink.

    When ``symlink=True``, each skill is symlinked to its source in the installed
    ``universal_skills`` package instead of copied. This avoids duplicating files on disk and means
    the installed skills track the package automatically on every ``pip install -U`` — there is no
    stale copy to re-sync. Falls back to a copy if the filesystem refuses the symlink (e.g. Windows
    without privileges). This is the same pattern the bundled skills already use (e.g. the
    ``code-enhancer`` skill is a symlink into this package).

    ``contract`` is the target tool's :class:`adapters.AgentContract` (default:
    permissive, i.e. no behavior change). When it ``requires_transform`` (e.g.
    Codex), skills are always COPIED (never symlinked) and each installed
    ``SKILL.md`` has its frontmatter adapted to the target's rules.
    """
    if contract is None and adapters is not None:
        contract = adapters.get_contract("")
    requires_transform = bool(contract is not None and contract.requires_transform)

    if not target_path.exists():
        logger.info(f"Creating target directory: {target_path}")
        target_path.mkdir(parents=True, exist_ok=True)

    sources = get_source_paths(
        skill_names, group, include_graphs, layer=layer, providers=providers
    )
    if not sources:
        logger.error("No skill/graph sources found to install.")
        return False

    # A transform-requiring target (frontmatter must be rewritten per skill) can
    # never be symlinked — the installed copy must diverge from the source file.
    effective_symlink = symlink and not requires_transform
    if symlink and requires_transform:
        logger.info(
            "Target requires a frontmatter transform → copying, not symlinking."
        )

    installed_count = 0
    for skill_src in sources:
        # Determine destination
        # Documentation graphs go into a sub-folder, whether they came from the
        # canonical skill_graphs package or a provider's ``skill-graphs/`` subdir —
        # UNLESS the target is flat-discovery (e.g. Codex), which has no nested
        # lookup, so the graph goes at the target's top level instead.
        is_graph = (
            "skill_graphs" in skill_src.parts or "skill-graphs" in skill_src.parts
        )
        dest_name = (
            adapters.resolve_dest_name(skill_src.name, contract)
            if requires_transform
            else skill_src.name
        )
        if is_graph:
            if requires_transform and contract.flat_discovery:
                dest_root = target_path
            else:
                dest_root = target_path / "skill-graphs"
                dest_root.mkdir(parents=True, exist_ok=True)
            skill_dst = dest_root / dest_name
        else:
            skill_dst = target_path / dest_name

        src_abs = skill_src.resolve()

        # Idempotent: an already-correct symlink needs no work (even without --force).
        if effective_symlink and skill_dst.is_symlink() and skill_dst.resolve() == src_abs:
            logger.info(f"{skill_src.name} already symlinked → up to date.")
            continue

        # Never install a skill into itself or its own subtree. If the resolved
        # destination equals the source, or either is an ancestor of the other, a copy
        # would recurse and a symlink would create a self-referential loop
        # (`kg-ingest/kg-ingest -> kg-ingest`) — and `_remove_dest` below would first
        # delete the real source. Skip such degenerate targets outright.
        dst_abs = skill_dst.resolve()
        if src_abs == dst_abs or src_abs in dst_abs.parents or dst_abs in src_abs.parents:
            logger.warning(
                f"Skipping {skill_src.name}: destination {dst_abs} is the source itself "
                f"or shares its subtree — would create a self-referential link."
            )
            continue

        if requires_transform:
            if _install_transformed_copy(skill_src, skill_dst, force, contract):
                installed_count += 1
                if contract.flat_discovery and not is_graph:
                    for nested_src in adapters.iter_promotable_nested(skill_src):
                        nested_dst = target_path / adapters.resolve_dest_name(
                            nested_src.name, contract
                        )
                        if _install_transformed_copy(
                            nested_src, nested_dst, force, contract
                        ):
                            installed_count += 1
            continue

        # Repoint a stale symlink — broken (dead target) or pointing at a MOVED source
        # (same skill name, refactored to a new package/path) — freely in symlink mode:
        # correcting a link to its authoritative current source is always safe and is
        # exactly how a refactor should propagate. Only a real copied dir/file still
        # needs --force to overwrite.
        stale_symlink = skill_dst.is_symlink() and skill_dst.resolve() != src_abs
        if effective_symlink and stale_symlink:
            logger.info(f"Repointing {skill_src.name} → moved/updated source.")
        elif skill_dst.exists() and not force:
            logger.info(
                f"Skipping {skill_src.name} (already exists). Use --force to overwrite."
            )
            continue

        verb = "Symlinking" if effective_symlink else "Installing"
        logger.info(f"{verb} {skill_src.name} to {skill_dst}...")
        try:
            if skill_dst.exists() or skill_dst.is_symlink():
                _remove_dest(skill_dst)
            if effective_symlink:
                try:
                    os.symlink(src_abs, skill_dst, target_is_directory=True)
                except OSError as link_err:
                    # Windows symlinks need admin/Developer Mode; a directory
                    # junction is the no-privilege equivalent. Try it before copying.
                    if _try_windows_junction(skill_dst, src_abs):
                        logger.info(
                            f"Symlink unavailable for {skill_src.name} ({link_err}); "
                            "used a Windows directory junction instead."
                        )
                    else:
                        logger.warning(
                            f"Symlink unavailable for {skill_src.name} ({link_err}); copying instead."
                        )
                        shutil.copytree(src_abs, skill_dst)
            else:
                shutil.copytree(src_abs, skill_dst)
            installed_count += 1
        except Exception as e:
            logger.error(f"Failed to install {skill_src.name}: {e}")

    # After (re)installing, sweep away dead links from renamed/removed skills so a
    # refactor leaves no orphaned stubs. Only on a FULL install — a targeted
    # --skills/--group run must not touch links outside its scope.
    if prune and not skill_names and not group:
        _prune_broken_symlinks(target_path)

    mode = "symlinked" if symlink else "installed"
    logger.info(f"Successfully {mode} {installed_count} items.")
    return True


def _find_portability_checker() -> Optional[Path]:
    """Locate ``scripts/check_frontmatter_portability.py`` from a repo checkout.

    Dev-only tooling (not shipped inside the installed ``universal_skills``
    package), so this is only found when running against a checkout — e.g. via
    ``pip install -e .`` from this repo. Absent otherwise, in which case
    ``--validate`` no-ops rather than failing the install.
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "scripts" / "check_frontmatter_portability.py"
        if cand.is_file():
            return cand
    return None


def _run_validate(target_path: Path) -> None:
    """Run the frontmatter portability gate against an emitted target dir."""
    checker = _find_portability_checker()
    if checker is None:
        logger.debug(
            "check_frontmatter_portability.py not found (not a repo checkout); "
            "skipping --validate."
        )
        return
    try:
        proc = subprocess.run(
            [sys.executable, str(checker), str(target_path), "--max-violations", "0"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"--validate could not run the portability checker: {e}")
        return
    if proc.returncode != 0:
        logger.warning(
            f"--validate: frontmatter portability issues in {target_path}:\n"
            f"{proc.stdout}{proc.stderr}"
        )
    else:
        logger.info(f"--validate: {target_path} passed the frontmatter portability gate.")


def _available_providers() -> List[str]:
    """All installable skill providers: universal-skills + agent-package contributors."""
    provs = [UNIVERSAL_PROVIDER]
    for name, _ in _iter_skill_providers():
        if name not in provs:
            provs.append(name)
    return provs


def _prompt_choice(title: str, items: List[tuple]) -> List[str]:
    """Numbered multi-select prompt with an 'all' shortcut. Returns selected keys.

    ``items`` is a list of ``(key, display)`` tuples. Empty input or 'a'/'all'
    selects everything; otherwise comma/space-separated indices pick a subset.
    """
    print(f"\n{title}")
    for i, (_, disp) in enumerate(items, 1):
        print(f"  {i}) {disp}")
    print("  a) all")
    raw = input("Select (numbers, comma/space separated, or 'a' for all): ").strip().lower()
    if raw in ("", "a", "all"):
        return [k for k, _ in items]
    picks = [
        items[int(tok) - 1][0]
        for tok in re.split(r"[,\s]+", raw)
        if tok.isdigit() and 1 <= int(tok) <= len(items)
    ]
    return picks or [k for k, _ in items]


def _run_interactive(detected: dict) -> tuple:
    """Interactively choose target tools and source providers.

    Returns ``(selected_tools: dict, providers: set | None)`` where ``providers`` is
    ``None`` when every provider was selected (install-all).
    """
    if detected:
        tool_items = [(k, f"{k}  →  {v}") for k, v in detected.items()]
        tool_keys = _prompt_choice(
            "Install skills into which detected AI tools?", tool_items
        )
        selected_tools = {k: detected[k] for k in tool_keys}
    else:
        print("\nNo agent tools detected on this host — skipping tool selection.")
        selected_tools = {}

    all_provs = _available_providers()
    prov_items = [
        (
            p,
            "universal-skills (built-in library)"
            if p == UNIVERSAL_PROVIDER
            else f"{p} (agent-package)",
        )
        for p in all_provs
    ]
    prov_keys = _prompt_choice(
        "Install skills from which packages? (agent-packages ship their own skills)",
        prov_items,
    )
    providers = None if set(prov_keys) == set(all_provs) else set(prov_keys)
    return selected_tools, providers


def main():
    parser = argparse.ArgumentParser(
        description="Install universal-skills into agent tools"
    )
    parser.add_argument(
        "--tool",
        help=("Target tool: " + ", ".join(sorted(TOOL_PATHS)) + "."),
    )
    parser.add_argument(
        "--all-detected",
        action="store_true",
        help="Install into every agent tool detected on this host (skips absent tools).",
    )
    parser.add_argument(
        "--all",
        dest="all_tools",
        action="store_true",
        help="Install into every known tool path whether or not it is detected.",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help=(
            "Interactively choose which DETECTED AI tools to install into (with an "
            "'all' option) AND which skill-provider packages to install from "
            "(universal-skills + every pip-installed agent-package that ships skills). "
            "Auto-enabled on a bare invocation when a TTY is present; skipped without a TTY."
        ),
    )
    parser.add_argument(
        "--providers",
        help=(
            "Comma-separated skill providers to install from: 'universal-skills' "
            "and/or agent-package names (default: all installed providers)."
        ),
    )
    parser.add_argument("--path", help="Explicit custom path to install skills into")
    parser.add_argument(
        "--scope",
        choices=["global", "workspace"],
        default="global",
        help="Installation scope (default: global)",
    )
    parser.add_argument(
        "--skills", help="Comma-separated list of skill names to install (default: all)"
    )
    parser.add_argument(
        "--group", "--category", help="Install all skills in a specific category"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing skills"
    )
    parser.add_argument(
        "--symlink",
        "--link",
        action="store_true",
        help=(
            "Symlink skills to the installed universal_skills package instead of copying. "
            "No duplicate files; skills auto-update on every 'pip install -U universal-skills'."
        ),
    )
    parser.add_argument(
        "--install-skill-graphs",
        action="store_true",
        help="Also install skill-graphs from the skill-graphs repository",
    )
    parser.add_argument(
        "--no-prune",
        dest="prune",
        action="store_false",
        help=(
            "Do NOT remove broken symlinks left by renamed/removed skills. Pruning is "
            "on by default for a full install (skipped automatically for a targeted "
            "--skills/--group run)."
        ),
    )
    parser.add_argument(
        "--no-xdg",
        dest="no_xdg",
        action="store_true",
        help=(
            "Do NOT also update the canonical agent-utilities XDG skills store. By "
            "default every global install ALSO writes there (it is the dir the "
            "agent-utilities factory + agent-terminal-ui auto-load), so it stays current "
            "whichever external tool you target."
        ),
    )
    parser.add_argument(
        "--layer",
        choices=["all", "atomic", "workflows"],
        default="all",
        help=(
            "Which layer to install. 'atomic' = atomic building-block skills only "
            "(recommended for Claude — the agent invokes these directly). 'workflows' "
            "= skill-workflows only (these run on the graph-os orchestrator; Claude "
            "fires them via kg-delegate). 'all' = both (default)."
        ),
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help=(
            "After installing into a target whose agent contract required a frontmatter "
            "transform (e.g. Codex), run the frontmatter-portability gate against the "
            "emitted skills and log the result (a non-fatal warning on violations). "
            "No-op against a plain pip install (the checker is repo-checkout-only)."
        ),
    )

    args = parser.parse_args()

    skill_names = args.skills.split(",") if args.skills else None
    provider_filter: Optional[set] = (
        {p.strip() for p in args.providers.split(",") if p.strip()}
        if args.providers
        else None
    )

    # ── Interactive picker (tools + providers) ──────────────────────────────
    # Runs when explicitly requested, or on a bare invocation (no target flag) with a
    # TTY. Without a TTY, --interactive degrades to --all-detected so automation
    # (install.sh --all-detected) is never blocked on a prompt.
    no_target_flag = not (
        args.all_detected or args.all_tools or args.path or args.tool
    )
    interactive_targets: dict = {}
    if args.interactive and not sys.stdin.isatty():
        logger.warning(
            "--interactive requested but no TTY; installing into all detected tools "
            "from all providers instead."
        )
        args.all_detected = True
    elif (args.interactive or no_target_flag) and sys.stdin.isatty():
        interactive_targets, sel_providers = _run_interactive(detect_present_tools())
        if provider_filter is None:
            provider_filter = sel_providers

    # ── Resolve destinations ────────────────────────────────────────────────
    # Build the set of skill dirs to write to. The agent-utilities XDG store is
    # ALWAYS included (unless --no-xdg, global scope) because it is the canonical dir
    # the agent-utilities factory + agent-terminal-ui auto-load — we keep it current on
    # every run, whichever external tool you also target. A bare ``install-skills``
    # (no --tool/--path) therefore updates exactly that store.
    targets: dict = {}
    targets.update(interactive_targets)
    if args.all_detected or args.all_tools:
        found = detect_present_tools() if args.all_detected else dict(TOOL_PATHS)
        if not found:
            print(
                "No agent tools detected on this host. Use --tool/--path to target one "
                "explicitly, or --all to install into every known path.",
                file=sys.stderr,
            )
            sys.exit(1)
        targets.update(found)
    elif args.path and args.tool:
        # Both given: install to a CUSTOM directory but still apply --tool's
        # frontmatter contract (e.g. dry-running what Codex would receive without
        # touching the real ~/.codex/skills). Label by tool so adapters.get_contract
        # resolves the right contract; the destination is still --path.
        targets[args.tool.lower()] = Path(args.path).expanduser()
    elif args.path:
        targets[args.path] = Path(args.path).expanduser()
    elif args.tool:
        tool_key = args.tool.lower()
        if args.scope == "global":
            # Fallback to treating an unknown tool as a literal path.
            target = TOOL_PATHS.get(tool_key) or Path(args.tool).expanduser()
        else:  # workspace scope
            root = get_workspace_root()
            target = root / WORKSPACE_PATHS.get(tool_key, WORKSPACE_PATHS["default"])
        targets[tool_key] = target

    # Always keep the canonical agent-utilities XDG store in sync (global scope only).
    if not args.no_xdg and args.scope == "global":
        targets.setdefault("agent-utilities (xdg)", TOOL_PATHS["agent-utilities"])

    if not targets:
        print(
            "Error: nothing to do — pass --tool / --path / --all-detected / --all, or "
            "omit them to update just the agent-utilities XDG store (don't combine that "
            "with --no-xdg).",
            file=sys.stderr,
        )
        sys.exit(1)

    # Collapse duplicate destinations (e.g. agent-utilities/agent-terminal-ui, or the
    # XDG store when it is also the explicit target), then install into each.
    seen: set = set()
    for label, target in targets.items():
        if str(target) in seen:
            continue
        seen.add(str(target))
        logger.info(f"→ {label}: {target}")
        contract = adapters.get_contract(label) if adapters is not None else None
        install_skills(
            target,
            skill_names,
            args.group,
            args.force,
            args.install_skill_graphs,
            symlink=args.symlink,
            layer=args.layer,
            prune=args.prune,
            providers=provider_filter,
            contract=contract,
        )
        if args.validate and contract is not None and contract.requires_transform:
            _run_validate(target)


if __name__ == "__main__":
    main()
