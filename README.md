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

*Version: 0.1.17*

## Overview

Universal Skills is a collection of shared, reusable skills designed for Pydantic AI Agents. It provides a standardized way to give agents advanced capabilities like codebase searching, file navigation, and inter-agent communication.

## Included Skills

The following universal skills are available. You can disable specific skills by setting their corresponding environment variables to `False` (default is `True`).

| Skill Directory       | Description                                                           | Disable Flag                          | Install Command                         |
|:----------------------|:----------------------------------------------------------------------|:--------------------------------------|:----------------------------------------|
| `agent-browser`       | Browser automation CLI for agents using the agent-browser tool.      | `AGENT_BROWSER_ENABLE=False`          | `universal-skills[agent-browser]`       |
| `agent-builder`       | Templates and guidelines for building Single and Multi-Agent systems. | `AGENT_BUILDER_ENABLE=False`          | `universal-skills[agent-builder]`       |
| `agent-workflows`     | Agent-to-Agent communication, orchestration, and subagent dispatch.   | `AGENT_WORKFLOWS_ENABLE=False`        | `universal-skills[agent-workflows]`     |
| `algorithmic-art`      | Generative algorithmic art using p5.js and interactive artifacts.    | `ALGORITHMIC_ART_ENABLE=False`        | `universal-skills[algorithmic-art]`     |
| `brainstorming`       | Structured ideation, problem-framing, and design research.            | `BRAINSTORMING_ENABLE=False`          | `universal-skills[brainstorming]`       |
| `brand-guidelines`    | Creating brand identity systems (logos, palettes, voice/tone).         | `BRAND_GUIDELINES_ENABLE=False`       | `universal-skills[brand-guidelines]`    |
| `browser-tools`       | Web browser interaction and E2E visual QA via Playwright.             | `BROWSER_TOOLS_ENABLE=False`          | `universal-skills[browser-tools]`       |
| `c4-architecture`     | Software architecture documentation using the C4 model in Mermaid.   | `C4_ARCHITECTURE_ENABLE=False`        | `universal-skills[c4-architecture]`     |
| `canvas-design`       | Programmatic graphic design using HTML Canvas or SVG APIs.            | `CANVAS_DESIGN_ENABLE=False`          | `universal-skills[canvas-design]`       |
| `cloudflare-deploy`   | Deploy applications and infrastructure to Cloudflare.                 | `CLOUDFLARE_DEPLOY_ENABLE=True` (D)   | `universal-skills[cloudflare-deploy]`           |
| `creative-media`      | Creative media processing (animations, GIFs, image conversion).       | `CREATIVE_MEDIA_ENABLE=False`         | `universal-skills[creative-media]`     |
| `database-tools`      | Connect and query PostgreSQL, MySQL, and MSSQL databases.             | `DATABASE_TOOLS_ENABLE=False`         | `universal-skills[database-tools]`      |
| `developer-utilities` | Formatting, conversion, generation, cryptographic, and networking.    | `DEVELOPER_UTILITIES_ENABLE=False`    | `universal-skills[developer-utilities]` |
| `document-converter` | Bulk convert .docx and .pdf to Markdown with high fidelity. | `DOCUMENT_CONVERTER_ENABLE=False`    | `universal-skills[document-converter]` |
| `document-tools`      | Read, edit, analyze, or create document files (PDF, spreadsheet, etc) | `DOCUMENT_TOOLS_ENABLE=False`         | `universal-skills[document-tools]`      |
| `github-tools`        | GitHub workflows, PR comments, CI fixes, and git practices.           | `GITHUB_TOOLS_ENABLE=False`           | `universal-skills[github-tools]`        |
| `google-workspace`    | Google Workspace ecosystem integration (Gmail, Drive, Docs, etc).     | `GOOGLE_WORKSPACE_ENABLE=True` (D)    | `universal-skills[google-workspace]`    |
| `internal-comms`      | Creating internal announcements, memos, and executive briefings.      | `INTERNAL_COMMS_ENABLE=False`         | `universal-skills[internal-comms]`      |
| `jira-tools`          | Interact with Jira via CLI or Atlassian MCP for ticket management.    | `JIRA_TOOLS_ENABLE=False`             | `universal-skills[jira-tools]`          |
| `jupyter-notebook`    | Create, scaffold, or edit Jupyter notebooks.                          | `JUPYTER_NOTEBOOK_ENABLE=True` (D)    | `universal-skills[jupyter-notebook]`    |
| `marp-presentations`  | Create professional Marp Markdown presentation slides.                | `MARP_PRESENTATIONS_ENABLE=False`     | `universal-skills[marp-presentations]`  |
| `mcp-builder`         | Guide for creating high-quality FastMCP servers.                      | `MCP_BUILDER_ENABLE=False`            | `universal-skills[mcp-builder]`         |
| `mermaid-diagrams`    | Create software diagrams (class, sequence, flowchart, ERD, C4, etc). | `MERMAID_DIAGRAMS_ENABLE=False`       | `universal-skills[mermaid-diagrams]`    |
| `product-management`  | PRD development, user stories, prioritization, and roadmapping.       | `PRODUCT_MANAGEMENT_ENABLE=False`     | `universal-skills[product-management]`  |
| `product-strategy`    | Market analysis, TAM/SAM/SOM, positioning, and SaaS metrics.          | `PRODUCT_STRATEGY_ENABLE=False`       | `universal-skills[product-strategy]`    |
| `project-planning`    | High-level reasoning, brainstorming, debugging, and research.         | `PROJECT_PLANNING_ENABLE=False`       | `universal-skills[project-planning]`    |
| `qa-planning`         | QA test plans, manual test cases, regression suites, and bug reports. | `QA_PLANNING_ENABLE=False`            | `universal-skills[qa-planning]`         |
| `react-development`   | Type-safe React + TypeScript components, hooks, and routing.          | `REACT_DEVELOPMENT_ENABLE=False`      | `universal-skills[react-development]`   |
| `security-tools`      | Threat modeling, Sentry error logs, and security code analysis.       | `SECURITY_TOOLS_ENABLE=False`         | `universal-skills[security-tools]`      |
| `skill-builder`       | Tooling for creating and standardizing new universal skills.          | `SKILL_BUILDER_ENABLE=False`          | `universal-skills[skill-builder]`       |
| `skill-graph-builder` | Transform website documentation into indexed agent skills.            | `SKILL_GRAPH_BUILDER_ENABLE=True` (D) | `universal-skills[skill-graph-builder]` |
| `skill-installer`     | Install skills into Windsurf, Claude Code, Antigravity, etc.          | `SKILL_INSTALLER_ENABLE=False`        | `universal-skills[skill-installer]`     |
| `session-handoff`     | Create and restore agent session handoff documents.                   | `SESSION_HANDOFF_ENABLE=False`        | `universal-skills[session-handoff]`     |
| `system-tools`        | Hardware and OS operations (screenshots, bluetooth, tmux).            | `SYSTEM_TOOLS_ENABLE=False`           | `universal-skills[system-tools]`        |
| `systems-manager`     | Fast codebase search, file navigation, and structural code analysis.  | `SYSTEMS_MANAGER_ENABLE=False`        | `universal-skills[systems-manager]`     |
| `tdd-methodology`     | Test-Driven Development workflow (Red-Green-Refactor cycle).          | `TDD_METHODOLOGY_ENABLE=False`        | `universal-skills[tdd-methodology]`     |
| `theme-factory`       | Designing themes, design tokens, and CSS variable systems.            | `THEME_FACTORY_ENABLE=False`          | `universal-skills[theme-factory]`       |
| `user-research`       | User discovery, JTBD, personas, and journey mapping.                  | `USER_RESEARCH_ENABLE=False`          | `universal-skills[user-research]`       |
| `web-artifacts`       | Frontend design, UI building, and artifact generation.                | `WEB_ARTIFACTS_ENABLE=False`          | `universal-skills[web-artifacts]`       |
| `website-builder`     | World-class frontend engineer for cinematic landing pages.            | `WEBSITE_BUILDER_ENABLE=False`        | `universal-skills[website-builder]`             |
| `web-crawler`         | High-speed recursive web crawling and sitemap processing.             | `WEB_CRAWLER_ENABLE=True` (D)         | `universal-skills[web-crawler]`         |
| `web-search`          | Search the web via DDG, Google, Bing, or Searxng.                     | `WEB_SEARCH_ENABLE=False`             | `universal-skills[web-search]`          |

## Security & SSL Verification

All relevant scripts in Universal Skills support a standardized approach to SSL verification:

- **CLI Override**: Use the `--insecure` flag to disable SSL verification.
- **Environment Variable**: Set `SSL_VERIFY=False` (or `0`, `off`) to disable verification globally.
- **Precedence**: Command-line flags always take precedence over environment variables.

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
