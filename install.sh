#!/bin/sh
# universal-skills — one-click install / easy setup.
#
# Installs the universal-skills package (PyPI via uv/pip, or editable for dev) and then
# deploys the skills — including universal-installer and agent-os-genesis (alias
# agent-utilities-genesis) — into EVERY detected AI tool (Claude Code, Antigravity,
# Windsurf, OpenCode, Cursor, Zed, Codex, Devin) AND the agent-utilities XDG space
# (~/.config/agent-utilities/skills), preferring SYMLINKS to the installed package
# (Windows falls back to a directory junction, then a copy).
#
# This is the technical starting point for agent-os-genesis: once installed, the
# `universal-installer` skill (and the `install-skills` CLI) are present and can deploy
# any other skill. agent-os-genesis is then loadable/invocable in your tools.
#
# Usage (download first so the installer can be reviewed before execution):
#   curl -fSLo universal-skills-install.sh https://knuckles-team.github.io/universal-skills/install.sh
#   sh universal-skills-install.sh
#   # or from a clone:
#   sh install.sh [--editable] [--copy] [--skills a,b] [--mcp <config.json>] [--no-mcp] [--dry-run]
#
# Flags:
#   --editable        Dev install: `uv pip install -e .` / `pip install -e .` from the
#                     repo (skills symlink to your working tree). Default: PyPI install.
#   --copy            Copy skills instead of symlinking (default: symlink).
#   --skills a,b,c    Only deploy these skills (default: all). e.g. --skills agent-os-genesis
#   --mcp <path>      Also wire MCP servers from this mcp_config.json into detected tools.
#   --no-mcp          Skip MCP wiring (default if no --mcp given).
#   --dry-run         Print the steps without executing.
set -eu

PACKAGE_VERSION="1.2.1"
EDITABLE=0; LINK="--symlink"; SKILLS=""; MCP_CONFIG=""; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --editable) EDITABLE=1 ;;
    --copy) LINK="" ;;
    --skills)
      [ $# -ge 2 ] || { echo "--skills requires a value" >&2; exit 2; }
      SKILLS="$2"; shift ;;
    --mcp)
      [ $# -ge 2 ] || { echo "--mcp requires a value" >&2; exit 2; }
      MCP_CONFIG="$2"; shift ;;
    --no-mcp) MCP_CONFIG="" ;;
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
  shift
done

info() { printf '\033[36m==>\033[0m %s\n' "$1"; }
warn() { printf '\033[33mwarn:\033[0m %s\n' "$1"; }
run() {
  info "$*"
  [ "$DRY" -eq 1 ] || "$@"
}

# Repo root = this script's dir (so --editable installs from the checkout).
REPO_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
HAVE_UV=0; command -v uv >/dev/null 2>&1 && HAVE_UV=1

# 1) Install the package. A PERSISTENT install is required so --symlink targets a
#    stable location (an ephemeral `uvx` run would leave dangling links).
if [ "$EDITABLE" -eq 1 ]; then
  if [ "$HAVE_UV" -eq 1 ]; then
    run uv pip install -e "$REPO_DIR" || run pip install -e "$REPO_DIR"
  else
    run pip install -e "$REPO_DIR"
  fi
else
  if [ "$HAVE_UV" -eq 1 ]; then
    run uv tool install "universal-skills==$PACKAGE_VERSION" || \
      run pip install "universal-skills==$PACKAGE_VERSION"
  else
    run pip install "universal-skills==$PACKAGE_VERSION"
  fi
fi

# 2) Resolve the install-skills CLI (uv tool puts it on PATH; else call via python).
if command -v install-skills >/dev/null 2>&1; then
  run_install_skills() { run install-skills "$@"; }
else
  run_install_skills() {
    run python3 -c 'from universal_skills.core.skill_installer import main; main()' "$@"
  }
  warn "install-skills not on PATH — invoking via python."
fi

# 3) Deploy skills into every detected tool, preferring symlinks.
if [ -n "$LINK" ] && [ -n "$SKILLS" ]; then
  run_install_skills --all-detected "$LINK" --skills "$SKILLS"
elif [ -n "$LINK" ]; then
  run_install_skills --all-detected "$LINK"
elif [ -n "$SKILLS" ]; then
  run_install_skills --all-detected --skills "$SKILLS"
else
  run_install_skills --all-detected
fi

# 4) Optional: wire MCP servers (genesis needs the graph-os + connector MCP servers).
if [ -n "$MCP_CONFIG" ]; then
  MCP_INSTALL="$(python3 -c 'import importlib.util as u,os; s=u.find_spec("universal_skills"); print(os.path.join(os.path.dirname(s.origin),"agent-tools","mcp-installer","scripts","install.py")) if s else print("")' 2>/dev/null || true)"
  if [ -n "$MCP_INSTALL" ] && [ -f "$MCP_INSTALL" ]; then
    run python3 "$MCP_INSTALL" --config "$MCP_CONFIG" --all-detected
  else
    warn "mcp-installer not found in the installed package — skipping MCP wiring."
  fi
fi

info "Done. agent-os-genesis (alias agent-utilities-genesis) + universal-installer are deployed."
info "Next: open your AI tool and invoke \"agent-os-genesis\" (or \"day0\") to deploy the Agent OS,"
info "or \"deploy <package> with agent-os-genesis\" to stand up a single connector."
