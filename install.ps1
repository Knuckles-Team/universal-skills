<#
.SYNOPSIS
  universal-skills — one-click install / easy setup (Windows mirror of install.sh).

.DESCRIPTION
  Installs the universal-skills package (PyPI via uv/pip, or editable for dev) and
  deploys the skills — including skill-installer and agent-os-genesis (alias
  agent-utilities-genesis) — into every detected AI tool AND the agent-utilities XDG
  space, preferring symlinks (Windows: a directory JUNCTION when symlinks need admin,
  then a copy). This is the starting point for agent-os-genesis.

.EXAMPLE
  irm https://knuckles-team.github.io/universal-skills/install.ps1 | iex
  # or from a clone:
  ./install.ps1 -Editable -Mcp .\mcp_config.json
#>
[CmdletBinding()]
param(
  [switch]$Editable,
  [switch]$Copy,
  [string]$Skills = "",
  [string]$Mcp = "",
  [switch]$DryRun
)
$ErrorActionPreference = "Stop"
function Info($m) { Write-Host "==> $m" -ForegroundColor Cyan }
function Warn($m) { Write-Host "warn: $m" -ForegroundColor Yellow }
function Run($cmd) { Info $cmd; if (-not $DryRun) { Invoke-Expression $cmd } }

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HaveUv = [bool](Get-Command uv -ErrorAction SilentlyContinue)
$Link = if ($Copy) { "" } else { "--symlink" }

# 1) Install the package (persistent, so --symlink targets a stable location).
if ($Editable) {
  if ($HaveUv) { Run "uv pip install -e `"$RepoDir`"" } else { Run "pip install -e `"$RepoDir`"" }
} else {
  if ($HaveUv) { Run "uv tool install universal-skills" } else { Run "pip install universal-skills" }
}

# 2) Resolve the install-skills CLI.
if (Get-Command install-skills -ErrorAction SilentlyContinue) {
  $InstallSkills = "install-skills"
} else {
  Warn "install-skills not on PATH — invoking via python."
  $InstallSkills = "python -c `"from universal_skills.core.skill_installer import main; main()`""
}

# 3) Deploy skills into every detected tool, preferring symlinks/junctions.
$SkillsArg = if ($Skills) { "--skills $Skills" } else { "" }
Run "$InstallSkills --all-detected $Link $SkillsArg"

# 4) Optional MCP wiring.
if ($Mcp) {
  $McpInstall = python -c "import importlib.util as u,os; s=u.find_spec('universal_skills'); print(os.path.join(os.path.dirname(s.origin),'agent-tools','mcp-installer','scripts','install.py')) if s else print('')"
  if ($McpInstall -and (Test-Path $McpInstall)) {
    Run "python `"$McpInstall`" --config `"$Mcp`" --all-detected"
  } else {
    Warn "mcp-installer not found in the installed package — skipping MCP wiring."
  }
}

Info "Done. agent-os-genesis (alias agent-utilities-genesis) + skill-installer are deployed."
Info "Next: invoke `"agent-os-genesis`" (or `"day0`") in your AI tool to deploy the Agent OS."
