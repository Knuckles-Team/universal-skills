<#
.SYNOPSIS
  universal-skills — one-click install / easy setup (Windows mirror of install.sh).

.DESCRIPTION
  Installs the universal-skills package (PyPI via uv/pip, or editable for dev) and
  deploys the skills — including universal-installer and agent-os-genesis (alias
  agent-utilities-genesis) — into every detected AI tool AND the agent-utilities XDG
  space, preferring symlinks (Windows: a directory JUNCTION when symlinks need admin,
  then a copy). This is the starting point for agent-os-genesis.

.EXAMPLE
  # Run this reviewed file from a release artifact or clone:
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
function Run {
  param(
    [Parameter(Mandatory = $true)][string]$Executable,
    [string[]]$Arguments = @()
  )
  $rendered = @($Executable) + ($Arguments | ForEach-Object { '"' + ($_ -replace '"', '\"') + '"' })
  Info ($rendered -join ' ')
  if ($DryRun) { return }
  & $Executable @Arguments
  if ($LASTEXITCODE -ne 0) { throw "command failed" }
}

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  throw "uv not found; install a verified uv release before running this installer"
}
$Version = if ($env:UNIVERSAL_SKILLS_VERSION) { $env:UNIVERSAL_SKILLS_VERSION } else { "1.2.1" }
if ($Version -notmatch '^[0-9]+\.[0-9]+\.[0-9]+[a-zA-Z0-9.+-]*$') {
  throw "invalid exact universal-skills version"
}
$LinkArgs = if ($Copy) { @() } else { @("--symlink") }

# 1) Install the package (persistent, so --symlink targets a stable location).
if ($Editable) {
  Run "uv" @("pip", "install", "-e", $RepoDir)
} else {
  Run "uv" @("tool", "install", "universal-skills==$Version")
}

# 2) Resolve the install-skills CLI.
if (Get-Command install-skills -ErrorAction SilentlyContinue) {
  $InstallSkills = "install-skills"
  $InstallPrefix = @()
} else {
  Warn "install-skills not on PATH — invoking via python."
  $InstallSkills = "python"
  $InstallPrefix = @("-c", "from universal_skills.core.skill_installer import main; main()")
}

# 3) Deploy skills into every detected tool, preferring symlinks/junctions.
$InstallArgs = $InstallPrefix + @("--all-detected") + $LinkArgs
if ($Skills) { $InstallArgs += @("--skills", $Skills) }
Run $InstallSkills $InstallArgs

# 4) Optional MCP wiring.
if ($Mcp) {
  $McpInstall = python -c "import importlib.util as u,os; s=u.find_spec('universal_skills'); print(os.path.join(os.path.dirname(s.origin),'agent-tools','mcp-installer','scripts','install.py')) if s else print('')"
  if ($McpInstall -and (Test-Path $McpInstall)) {
    Run "python" @($McpInstall, "--config", $Mcp, "--all-detected")
  } else {
    Warn "mcp-installer not found in the installed package — skipping MCP wiring."
  }
}

Info "Done. agent-os-genesis (alias agent-utilities-genesis) + universal-installer are deployed."
Info "Next: invoke `"agent-os-genesis`" (or `"day0`") in your AI tool to deploy the Agent OS."
