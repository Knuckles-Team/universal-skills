# Universal Skills - Pydantic AI Skills

![PyPI - Version](https://img.shields.io/pypi/v/universal-skills)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/universal-skills)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/universal-skills)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/universal-skills)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/universal-skills)
![PyPI - License](https://img.shields.io/pypi/l/universal-skills)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/universal-skills)

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/universal-skills)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/universal-skills)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/universal-skills)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/universal-skills)

![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/universal-skills)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/universal-skills)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/universal-skills)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/universal-skills)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/universal-skills)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/universal-skills)

*Version: 0.1.4*

## Overview

Universal Skills is a collection of shared, reusable skills designed for Pydantic AI Agents. It provides a standardized way to give agents advanced capabilities like codebase searching, file navigation, and inter-agent communication.

## Included Skills

The following universal skills are available. You can disable specific skills by setting their corresponding environment variables to `False`.

| Skill Directory         | Description                                                          | Disable Flag (`=False`)             |
|:------------------------|:---------------------------------------------------------------------|:------------------------------------|
| `agent-workflows`       | Agent-to-Agent communication, orchestration, and subagent dispatch.  | `AGENT_WORKFLOWS_ENABLE`            |
| `browser-tools`         | Web browser interaction and E2E visual QA via Playwright.            | `BROWSER_TOOLS_ENABLE`              |
| `cloudflare-deploy`     | Deploy applications and infrastructure to Cloudflare.                | `CLOUDFLARE_DEPLOY_ENABLE`          |
| `database-tools`        | Connect and query PostgreSQL, MySQL, and MSSQL databases.            | `DATABASE_TOOLS_ENABLE`             |
| `developer-utilities`   | Formatting, conversion, generation, cryptographic, and networking. | `DEVELOPER_UTILITIES_ENABLE`        |
| `document-tools`        | Read, edit, analyze, or create document files (PDF, spreadsheet, etc)| `DOCUMENT_TOOLS_ENABLE`             |
| `github-tools`          | GitHub workflows, PR comments, CI fixes, and git practices.          | `GITHUB_TOOLS_ENABLE`               |
| `google-workspace`      | Google Workspace ecosystem integration (Gmail, Drive, Docs, etc).    | `GOOGLE_WORKSPACE_ENABLE`           |
| `jupyter-notebook`      | Create, scaffold, or edit Jupyter notebooks.                         | `JUPYTER_NOTEBOOK_ENABLE`           |
| `mcp-builder`           | Guide for creating high-quality FastMCP servers.                     | `MCP_BUILDER_ENABLE`                |
| `project-planning`      | High-level reasoning, brainstorming, debugging, and research.        | `PROJECT_PLANNING_ENABLE`           |
| `security-tools`        | Threat modeling, Sentry error logs, and security code analysis.      | `SECURITY_TOOLS_ENABLE`             |
| `skill-creator`         | Guide for creating effective skills for the universal-skills package.| `SKILL_CREATOR_ENABLE`              |
| `system-tools`          | Hardware and OS operations (screenshots, bluetooth, tmux).           | `SYSTEM_TOOLS_ENABLE`               |
| `systems-manager`       | Fast codebase search, file navigation, and structural code analysis. | `SYSTEMS_MANAGER_ENABLE`            |
| `web-artifacts`         | Frontend design, UI building, and artifact generation.               | `WEB_ARTIFACTS_ENABLE`              |

## Installation

```bash
pip install universal-skills
```

## Usage

Universal skills are typically loaded using the `get_universal_skills_path()` utility, which can be integrated into your agent's toolset. The utility will automatically respect the environment variables shown above to filter out disabled skills.

```python
from universal_skills.skill_utilities import get_universal_skills_path
from pydantic_ai_skills import SkillsToolset

# Load enabled universal skills
skills = SkillsToolset(directories=get_universal_skills_path())
```
