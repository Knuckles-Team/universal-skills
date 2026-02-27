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

*Version: 0.1.13*

## Overview

Universal Skills is a collection of shared, reusable skills designed for Pydantic AI Agents. It provides a standardized way to give agents advanced capabilities like codebase searching, file navigation, and inter-agent communication.

## Included Skills

The following universal skills are available. You can disable specific skills by setting their corresponding environment variables to `False` (default is `True`).

| Skill Directory       | Description                                                           | Disable Flag                          | Install Command                         |
|:----------------------|:----------------------------------------------------------------------|:--------------------------------------|:----------------------------------------|
| `agent-builder`       | Templates and guidelines for building Single and Multi-Agent systems. | `AGENT_BUILDER_ENABLE=False`          | `universal-skills[agent-builder]`       |
| `agent-workflows`     | Agent-to-Agent communication, orchestration, and subagent dispatch.   | `AGENT_WORKFLOWS_ENABLE=False`        | `universal-skills[agent-workflows]`     |
| `browser-tools`       | Web browser interaction and E2E visual QA via Playwright.             | `BROWSER_TOOLS_ENABLE=False`          | `universal-skills[browser-tools]`               |
| `cloudflare-deploy`   | Deploy applications and infrastructure to Cloudflare.                 | `CLOUDFLARE_DEPLOY_ENABLE=True` (D)   | `universal-skills[cloudflare-deploy]`           |
| `database-tools`      | Connect and query PostgreSQL, MySQL, and MSSQL databases.             | `DATABASE_TOOLS_ENABLE=False`         | `universal-skills[database-tools]`      |
| `developer-utilities` | Formatting, conversion, generation, cryptographic, and networking.    | `DEVELOPER_UTILITIES_ENABLE=False`    | `universal-skills[developer-utilities]` |
| `document-tools`      | Read, edit, analyze, or create document files (PDF, spreadsheet, etc) | `DOCUMENT_TOOLS_ENABLE=False`         | `universal-skills[document-tools]`      |
| `github-tools`        | GitHub workflows, PR comments, CI fixes, and git practices.           | `GITHUB_TOOLS_ENABLE=False`           | `universal-skills[github-tools]`        |
| `google-workspace`    | Google Workspace ecosystem integration (Gmail, Drive, Docs, etc).     | `GOOGLE_WORKSPACE_ENABLE=True` (D)    | `universal-skills[google-workspace]`    |
| `jupyter-notebook`    | Create, scaffold, or edit Jupyter notebooks.                          | `JUPYTER_NOTEBOOK_ENABLE=True` (D)    | `universal-skills[jupyter-notebook]`    |
| `mcp-builder`         | Guide for creating high-quality FastMCP servers.                      | `MCP_BUILDER_ENABLE=False`            | `universal-skills[mcp-builder]`         |
| `project-planning`    | High-level reasoning, brainstorming, debugging, and research.         | `PROJECT_PLANNING_ENABLE=False`       | `universal-skills[project-planning]`    |
| `security-tools`      | Threat modeling, Sentry error logs, and security code analysis.       | `SECURITY_TOOLS_ENABLE=False`         | `universal-skills[security-tools]`      |
| `skill-builder`       | Tooling for creating and standardizing new universal skills.          | `SKILL_BUILDER_ENABLE=False`          | `universal-skills[skill-builder]`       |
| `skill-graph-builder` | Transform website documentation into indexed agent skills.            | `SKILL_GRAPH_BUILDER_ENABLE=True` (D) | `universal-skills[skill-graph-builder]` |
| `system-tools`        | Hardware and OS operations (screenshots, bluetooth, tmux).            | `SYSTEM_TOOLS_ENABLE=False`           | `universal-skills[system-tools]`        |
| `systems-manager`     | Fast codebase search, file navigation, and structural code analysis.  | `SYSTEMS_MANAGER_ENABLE=False`        | `universal-skills[systems-manager]`     |
| `web-artifacts`       | Frontend design, UI building, and artifact generation.                | `WEB_ARTIFACTS_ENABLE=False`          | `universal-skills[web-artifacts]`       |
| `website-builder`     | World-class frontend engineer for cinematic landing pages.            | `WEBSITE_BUILDER_ENABLE=False`        | `universal-skills[website-builder]`             |
| `web-crawler`         | High-speed recursive web crawling and sitemap processing.             | `WEB_CRAWLER_ENABLE=True` (D)         | `universal-skills[web-crawler]`         |
| `web-search`          | Search the web via DDG, Google, Bing, or Searxng.                     | `WEB_SEARCH_ENABLE=False`             | `universal-skills[web-search]`          |

## Building Your Own Skill-Graphs

Universal Skills includes a `skill-graph-builder` that allows you to transform any website's documentation into an indexed knowledge base for your agents. These are stored in your local cache directory (`~/.cache/universal-skills/skill-graphs`) and can be enabled via environment variables.

### Example: Creating a Skill-Graph

You can prompt your agent to build a skill-graph for any technical documentation:

> "Use the skill-graph-builder to crawl https://ai.pydantic.dev and create a skill-graph named 'pydantic-ai-docs'."

Once built, the graph will be available in your cache.

### Enabling Your Graphs

To use a manually built graph, set its corresponding enable flag to `True`:

```bash
export PYDANTIC_AI_DOCS_ENABLE=True
```

## Installation

```bash
# Install with all standard skills
pip install universal-skills[all]

# Or install specific skill categories
pip install universal-skills[systems-manager,web-crawler,web-search]
```

## Usage

Universal skills are typically loaded using the `get_universal_skills_path()` utility, which can be integrated into your agent's toolset. The utility will automatically respect the environment variables shown above to filter out disabled skills.

```python
from universal_skills.skill_utilities import get_universal_skills_path, get_skill_graph_path
from pydantic_ai_skills import SkillsToolset

# Load enabled universal skills
skills_directories = [get_universal_skills_path(), get_skill_graph_path()]
skills = SkillsToolset(directories=skills_directories)
```
