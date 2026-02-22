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

*Version: 0.1.2*

## Overview

Universal Skills is a collection of shared, reusable skills designed for Pydantic AI Agents. It provides a standardized way to give agents advanced capabilities like codebase searching, file navigation, and inter-agent communication.

## Included Skills

- **a2a_client**: Enables Agent-to-Agent (A2A) communication, allowing agents to discover and call other agents.
- **bash**: Provides the ability to execute shell commands.
- **codebase-search**: Integrated `ripgrep` (rg) support for efficient searching across local codebases.
- **file-navigation**: Integrated `fd` support for fast file and directory navigation.
- **code-analysis**: Advanced Python code analysis capabilities using tree-sitter.

## Installation

```bash
pip install universal-skills
```

## Usage

Universal skills are typically loaded using the `get_universal_skills_path()` utility, which can be integrated into your agent's toolset.

```python
from universal_skills.skill_utilities import get_universal_skills_path
from pydantic_ai_skills import SkillsToolset

# Load universal skills
skills = SkillsToolset(get_universal_skills_path())
```
